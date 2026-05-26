from django.urls import path
from . import views

urlpatterns = [
    path("auth/login/", views.login_view),

    path("uploads/", views.list_uploads),
    path("uploads/file/", views.upload_file),

    path("activities/", views.list_activities),
    path("activities/<int:activity_id>/", views.activity_detail),
    path("activities/<int:activity_id>/update/", views.update_activity),
    path("activities/<int:activity_id>/approve/", views.approve_activity),
    path("activities/<int:activity_id>/reject/", views.reject_activity),
    path("activities/<int:activity_id>/lock/", views.lock_activity),

    path("dashboard/summary/", views.dashboard_summary),
    path("audit-logs/", views.list_audit_logs),
]