from django.urls import path
from teacher import views
app_name = "teacher"

urlpatterns = [
    path("", views.TeacherHomeView.as_view(), name='home'),
    path("student/list/", views.StudentListView.as_view(), name="tstudent-list"),
    path("group/list/", views.GroupListView.as_view(), name="tgroup-list"),
    path("teacher/settings/<int:pk>/", views.Settings.as_view(), name="group-settings"),
    path('group/<int:pk>/', views.group_detail_function_view, name='group_detail'),
    path('group/<int:group_id>/debtors/', views.group_debtors_view, name='group-debtors'),

    path('attendance/<int:group_id>/', views.AttendanceView.as_view(), name='attendance-list'),
    path('api/groups/<int:group_id>/students/', views.GroupStudentsAPIView.as_view(), name='group-students'),
    path('api/attendance/', views.AttendanceListAPIView.as_view(), name='attendance-list-api'),
    path('api/attendance/save/', views.SaveAttendanceAPIView.as_view(), name='save-attendance'),

    path('grades/<int:group_id>/', views.GradesView.as_view(), name='grades'),
    path('api/groups/<int:group_id>/students/', views.GroupStudentsAPIView.as_view(), name='group-students'),
    path('api/grades/', views.GradesListAPIView.as_view(), name='grades-list'),
    path('api/grades/save-single/', views.SaveSingleGradeAPIView.as_view(), name='save-single-grade'),
    path('api/grades/save/', views.SaveGradeAPIView.as_view(), name='save-grades'),
    
    path('rating/<int:group_id>/', views.RatingView.as_view(), name='rating'),
    path('api/rating/<int:group_id>/', views.GroupRatingAPIView.as_view(), name='rating-api'),

    path('notifications/count/', views.notification_count_view, name='notification-count'),
    path('notifications/list/', views.notification_list_api_view, name='notification-list-api'),
    path('notifications/<int:notification_id>/detail/', views.notification_detail_api_view, name='notification-detail-api'),
    
    # Notification Pages
    path('notifications/inbox/', views.notification_inbox_view, name='notification-inbox'),
    path('notifications/mark-all-read/', views.notification_mark_all_read_view, name='notification-mark-all-read'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete_view, name='notification-delete'),
]
