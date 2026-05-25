from django.urls import path
from reception import views
app_name = "reception"


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("information/", views.information_view, name="center-info"),
    path("archive/", views.Archive_list_view, name="archive-list"),
    path('api/search/', views.universal_search, name='universal-search'),
    path("manager/settings/<int:pk>/", views.Settings.as_view(), name="group-settings"),
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
    
    path('reception/rating/<int:group_id>/', views.RatingView.as_view(), name='rating'),
    path('api/rating/<int:group_id>/', views.GroupRatingAPIView.as_view(), name='rating-api'),

    path("teacher/list/", views.TeacherListView.as_view(), name="teacher-list"),
    path("teacher/create/", views.TeacherCreateView.as_view(), name="teacher-create"),
    path("teacher/<int:pk>/update/", views.TeacherUpdateView.as_view(), name="teacher-update"),
    path("teacher/<int:pk>/delete/", views.TeacherDeleteView.as_view(), name="teacher-delete"),

    path("course/list/", views.CourseListView.as_view(), name="course-list"),
    path("course/create/", views.CourseCreateView.as_view(), name="course-create"),
    path("courses/<int:pk>/groups/", views.CourseGroupListView.as_view(), name="course-groups"),
    path("course/<int:pk>/update/", views.CourseUpdateView.as_view(), name="course-update"),
    path("course/<int:pk>/delete/", views.CourseDeleteView.as_view(), name="course-delete"),

    path("group/list/", views.GroupListView.as_view(), name="group-list"),
    path("group/create/", views.GroupCreateView.as_view(), name="group-create"),
    path("group/<int:pk>/update/", views.GroupUpdateView.as_view(), name="group-update"),
    path("group/<int:pk>/delete/", views.GroupDeleteView.as_view(), name="group-delete"),

    path("student/list/", views.StudentListView.as_view(), name="student-list"),
    path("student/create/", views.StudentCreateView.as_view(), name="student-create"),
    path("student/<int:pk>/update/", views.StudentUpdateView.as_view(), name="student-update"),
    path("student/<int:pk>/delete/", views.StudentDeleteView.as_view(), name="student-delete"),

    path("lead/list/", views.LeadListView.as_view(), name="lead-list"),
    path("lead/create/", views.LeadCreateView.as_view(), name="lead-create"),
    path("lead/<int:pk>/update/", views.LeadUpdateView.as_view(), name="lead-update"),
    path("lead/<int:pk>/delete/", views.LeadDeleteView.as_view(), name="lead-delete"),

    path("classroom/list/", views.ClassroomListView.as_view(), name="classroom-list"),
    path("classroom/create/", views.ClassroomCreateView.as_view(), name="classroom-create"),
    path("classroom/<int:pk>/update/", views.ClassroomUpdateView.as_view(), name="classroom-update"),
    path("classroom/<int:pk>/delete/", views.ClassroomDeleteView.as_view(), name="classroom-delete"),
    path("schedule/", views.schedule_view, name="schedule"),

    path("employee/list/", views.EmployeeListView.as_view(), name="employee-list"),
    path("employee/create/", views.EmployeeCreateView.as_view(), name="employee-create"),
    path("employee/<int:pk>/update/", views.EmployeeUpdateView.as_view(), name="employee-update"),
    path("employee/<int:pk>/delete/", views.EmployeeDeleteView.as_view(), name="employee-delete"),

    path("api/attendance/", views.AttendanceListAPIView.as_view(), name="attendance-page"),
    path("attendance/<int:group_id>/", views.AttendanceView.as_view(), name="attendance-list"),
    path("api/attendance/save/", views.SaveAttendanceAPIView.as_view(), name="attendance-save"),
    path("api/groups/<int:group_id>/students/", views.GroupStudentsAPIView.as_view(), name="group-students"),

    path('others/', views.notification_others_view, name="others-notification"),
    path('notifications/count/', views.notification_count_view, name='notification-count'),
    path('notifications/list/', views.notification_list_api_view, name='notification-list-api'),
    path('notifications/<int:notification_id>/detail/', views.notification_detail_api_view, name='notification-detail-api'),
    
    # Notification Pages
    path('notifications/inbox/', views.notification_inbox_view, name='notification-inbox'),
    path('notifications/mark-all-read/', views.notification_mark_all_read_view, name='notification-mark-all-read'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete_view, name='notification-delete'),
]

