from django.contrib import admin
from .models import (
    Tenant,
    Facility,
    SourceUpload,
    RawRecord,
    UnitMapping,
    EmissionActivity,
    AuditLog,
)

admin.site.register(Tenant)
admin.site.register(Facility)
admin.site.register(SourceUpload)
admin.site.register(RawRecord)
admin.site.register(UnitMapping)
admin.site.register(EmissionActivity)
admin.site.register(AuditLog)