from rest_framework import serializers
from .models import SourceUpload, RawRecord, EmissionActivity, AuditLog


class SourceUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceUpload
        fields = "__all__"


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source="performed_by.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = "__all__"


class EmissionActivitySerializer(serializers.ModelSerializer):
    raw_payload = serializers.JSONField(source="raw_record.raw_payload", read_only=True)
    facility_code = serializers.CharField(source="facility.code", read_only=True)
    audit_logs = AuditLogSerializer(many=True, read_only=True)

    class Meta:
        model = EmissionActivity
        fields = "__all__"