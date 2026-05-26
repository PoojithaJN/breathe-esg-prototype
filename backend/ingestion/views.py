import csv
from io import TextIOWrapper

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import authenticate

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Tenant, Facility, SourceUpload, RawRecord, EmissionActivity, AuditLog
from .serializers import EmissionActivitySerializer, SourceUploadSerializer, AuditLogSerializer

from ingestion.parsers.sap_parser import parse_sap_row
from ingestion.parsers.utility_parser import parse_utility_row
from ingestion.parsers.travel_parser import parse_travel_row

from ingestion.services.validator import validate_sap, validate_utility, validate_travel


def get_demo_tenant():
    tenant, _ = Tenant.objects.get_or_create(
        slug="demo-client",
        defaults={"name": "Demo Enterprise Client"}
    )

    Facility.objects.get_or_create(
        tenant=tenant,
        code="BLR01",
        defaults={"name": "Bangalore Manufacturing Plant", "country": "India"}
    )

    Facility.objects.get_or_create(
        tenant=tenant,
        code="BLR02",
        defaults={"name": "Bangalore Office Campus", "country": "India"}
    )

    return tenant


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "token": token.key,
        "username": user.username
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    source_type = request.data.get("source_type")
    file = request.FILES.get("file")

    if source_type not in ["SAP", "UTILITY", "TRAVEL"]:
        return Response({"error": "Invalid source_type"}, status=400)

    if not file:
        return Response({"error": "File is required"}, status=400)

    tenant = get_demo_tenant()
    facilities = {f.code: f for f in Facility.objects.filter(tenant=tenant)}

    upload = SourceUpload.objects.create(
        tenant=tenant,
        source_type=source_type,
        original_file_name=file.name,
        uploaded_by=request.user,
        status="PROCESSING"
    )

    total_rows = 0
    successful_rows = 0
    failed_rows = 0
    suspicious_rows = 0

    try:
        decoded_file = TextIOWrapper(file.file, encoding="utf-8")
        reader = csv.DictReader(decoded_file)

        with transaction.atomic():
            for index, row in enumerate(reader, start=1):
                total_rows += 1

                raw_record = RawRecord.objects.create(
                    upload=upload,
                    row_number=index,
                    raw_payload=dict(row),
                    parse_status="PENDING"
                )

                try:
                    if source_type == "SAP":
                        parsed = parse_sap_row(row, tenant, facilities)
                        flags = validate_sap(parsed)
                    elif source_type == "UTILITY":
                        parsed = parse_utility_row(row, tenant, facilities)
                        flags = validate_utility(parsed)
                    else:
                        parsed = parse_travel_row(row, tenant, facilities)
                        flags = validate_travel(parsed)

                    if flags:
                        suspicious_rows += 1

                    activity = EmissionActivity.objects.create(
                        tenant=tenant,
                        raw_record=raw_record,
                        source_type=parsed["source_type"],
                        scope=parsed["scope"],
                        category=parsed["category"],
                        activity_date=parsed.get("activity_date"),
                        period_start=parsed.get("period_start"),
                        period_end=parsed.get("period_end"),
                        facility=parsed.get("facility"),
                        quantity=parsed.get("quantity"),
                        original_unit=parsed.get("original_unit", ""),
                        normalized_quantity=parsed.get("normalized_quantity"),
                        normalized_unit=parsed.get("normalized_unit", ""),
                        amount=parsed.get("amount"),
                        currency=parsed.get("currency", ""),
                        validation_status="NEEDS_REVIEW",
                        suspicious_flags=flags,
                        source_reference=parsed.get("source_reference", "")
                    )

                    raw_record.parse_status = "SUCCESS"
                    raw_record.save()

                    AuditLog.objects.create(
                        tenant=tenant,
                        activity=activity,
                        action="CREATED_FROM_UPLOAD",
                        new_value={
                            "source_type": source_type,
                            "row_number": index,
                            "flags": flags,
                        },
                        performed_by=request.user
                    )

                    successful_rows += 1

                except Exception as row_error:
                    failed_rows += 1
                    raw_record.parse_status = "FAILED"
                    raw_record.error_message = str(row_error)
                    raw_record.save()

            upload.total_rows = total_rows
            upload.successful_rows = successful_rows
            upload.failed_rows = failed_rows
            upload.suspicious_rows = suspicious_rows
            upload.status = "COMPLETED"
            upload.save()

    except Exception as error:
        upload.status = "FAILED"
        upload.save()
        return Response({"error": str(error)}, status=500)

    return Response({
        "message": "File processed successfully",
        "upload_id": upload.id,
        "source_type": source_type,
        "total_rows": total_rows,
        "successful_rows": successful_rows,
        "failed_rows": failed_rows,
        "suspicious_rows": suspicious_rows,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_activities(request):
    activities = EmissionActivity.objects.all().order_by("-created_at")

    source = request.GET.get("source")
    status_filter = request.GET.get("status")
    scope = request.GET.get("scope")
    suspicious = request.GET.get("suspicious")

    if source:
        activities = activities.filter(source_type=source)

    if status_filter:
        activities = activities.filter(validation_status=status_filter)

    if scope:
        activities = activities.filter(scope=scope)

    if suspicious == "true":
        activities = [a for a in activities if a.has_flags()]

    serializer = EmissionActivitySerializer(activities, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def activity_detail(request, activity_id):
    try:
        activity = EmissionActivity.objects.get(id=activity_id)
    except EmissionActivity.DoesNotExist:
        return Response({"error": "Activity not found"}, status=404)

    serializer = EmissionActivitySerializer(activity)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_activity(request, activity_id):
    try:
        activity = EmissionActivity.objects.get(id=activity_id)
    except EmissionActivity.DoesNotExist:
        return Response({"error": "Activity not found"}, status=404)

    if activity.is_locked:
        return Response({"error": "Locked records cannot be edited"}, status=400)

    old_value = EmissionActivitySerializer(activity).data

    editable_fields = [
        "category",
        "activity_date",
        "period_start",
        "period_end",
        "quantity",
        "normalized_quantity",
        "normalized_unit",
        "amount",
        "currency",
        "validation_status",
    ]

    for field in editable_fields:
        if field in request.data:
            setattr(activity, field, request.data[field])

    activity.save()

    AuditLog.objects.create(
        tenant=activity.tenant,
        activity=activity,
        action="UPDATED",
        old_value=old_value,
        new_value=request.data,
        performed_by=request.user
    )

    return Response(EmissionActivitySerializer(activity).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_activity(request, activity_id):
    try:
        activity = EmissionActivity.objects.get(id=activity_id)
    except EmissionActivity.DoesNotExist:
        return Response({"error": "Activity not found"}, status=404)

    if activity.is_locked:
        return Response({"error": "Locked record cannot be approved again"}, status=400)

    old_status = activity.validation_status
    activity.validation_status = "APPROVED"
    activity.approved_by = request.user
    activity.approved_at = timezone.now()
    activity.save()

    AuditLog.objects.create(
        tenant=activity.tenant,
        activity=activity,
        action="APPROVED",
        old_value={"status": old_status},
        new_value={"status": "APPROVED"},
        performed_by=request.user
    )

    return Response({"message": "Activity approved"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_activity(request, activity_id):
    try:
        activity = EmissionActivity.objects.get(id=activity_id)
    except EmissionActivity.DoesNotExist:
        return Response({"error": "Activity not found"}, status=404)

    if activity.is_locked:
        return Response({"error": "Locked record cannot be rejected"}, status=400)

    old_status = activity.validation_status
    activity.validation_status = "REJECTED"
    activity.save()

    AuditLog.objects.create(
        tenant=activity.tenant,
        activity=activity,
        action="REJECTED",
        old_value={"status": old_status},
        new_value={"status": "REJECTED"},
        performed_by=request.user
    )

    return Response({"message": "Activity rejected"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def lock_activity(request, activity_id):
    try:
        activity = EmissionActivity.objects.get(id=activity_id)
    except EmissionActivity.DoesNotExist:
        return Response({"error": "Activity not found"}, status=404)

    if activity.validation_status != "APPROVED":
        return Response({"error": "Only approved records can be locked"}, status=400)

    activity.is_locked = True
    activity.validation_status = "LOCKED"
    activity.save()

    AuditLog.objects.create(
        tenant=activity.tenant,
        activity=activity,
        action="LOCKED_FOR_AUDIT",
        old_value={"is_locked": False},
        new_value={"is_locked": True},
        performed_by=request.user
    )

    return Response({"message": "Activity locked for audit"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    activities = EmissionActivity.objects.all()

    data = {
        "total": activities.count(),
        "needs_review": activities.filter(validation_status="NEEDS_REVIEW").count(),
        "approved": activities.filter(validation_status="APPROVED").count(),
        "rejected": activities.filter(validation_status="REJECTED").count(),
        "locked": activities.filter(validation_status="LOCKED").count(),
        "suspicious": sum(1 for a in activities if a.has_flags()),
        "sap": activities.filter(source_type="SAP").count(),
        "utility": activities.filter(source_type="UTILITY").count(),
        "travel": activities.filter(source_type="TRAVEL").count(),
    }

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_uploads(request):
    uploads = SourceUpload.objects.all().order_by("-uploaded_at")
    serializer = SourceUploadSerializer(uploads, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_audit_logs(request):
    logs = AuditLog.objects.all().order_by("-performed_at")[:100]
    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data)