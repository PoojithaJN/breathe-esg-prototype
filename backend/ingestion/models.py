from django.db import models
from django.contrib.auth.models import User


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Facility(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100, default="India")

    class Meta:
        unique_together = ("tenant", "code")

    def __str__(self):
        return f"{self.code} - {self.name}"


class SourceUpload(models.Model):
    SOURCE_TYPES = [
        ("SAP", "SAP Fuel/Procurement"),
        ("UTILITY", "Utility Electricity"),
        ("TRAVEL", "Corporate Travel"),
    ]

    STATUS = [
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    original_file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default="PROCESSING")
    total_rows = models.IntegerField(default=0)
    successful_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    suspicious_rows = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.source_type} - {self.original_file_name}"


class RawRecord(models.Model):
    upload = models.ForeignKey(SourceUpload, on_delete=models.CASCADE, related_name="raw_records")
    row_number = models.IntegerField()
    raw_payload = models.JSONField()
    parse_status = models.CharField(max_length=30, default="PENDING")
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"Upload {self.upload.id} Row {self.row_number}"


class UnitMapping(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    source_unit = models.CharField(max_length=50)
    normalized_unit = models.CharField(max_length=50)
    multiplier = models.DecimalField(max_digits=14, decimal_places=6)

    def __str__(self):
        return f"{self.source_unit} -> {self.normalized_unit}"


class EmissionActivity(models.Model):
    SCOPES = [
        ("SCOPE_1", "Scope 1"),
        ("SCOPE_2", "Scope 2"),
        ("SCOPE_3", "Scope 3"),
    ]

    STATUS = [
        ("NEEDS_REVIEW", "Needs Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("LOCKED", "Locked"),
        ("FAILED", "Failed"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    raw_record = models.OneToOneField(RawRecord, on_delete=models.CASCADE, related_name="activity")

    source_type = models.CharField(max_length=20)
    scope = models.CharField(max_length=20, choices=SCOPES)
    category = models.CharField(max_length=100)

    activity_date = models.DateField(null=True, blank=True)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)

    quantity = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    original_unit = models.CharField(max_length=50, blank=True)
    normalized_quantity = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    normalized_unit = models.CharField(max_length=50, blank=True)

    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True)

    validation_status = models.CharField(max_length=30, choices=STATUS, default="NEEDS_REVIEW")
    suspicious_flags = models.JSONField(default=list)

    is_locked = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    source_reference = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_flags(self):
        return len(self.suspicious_flags or []) > 0

    def __str__(self):
        return f"{self.source_type} - {self.category} - {self.validation_status}"


class AuditLog(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    activity = models.ForeignKey(
        EmissionActivity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="audit_logs"
    )
    action = models.CharField(max_length=100)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    performed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} at {self.performed_at}"