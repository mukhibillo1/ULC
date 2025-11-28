from django.urls import path, include
from manager import views

app_name = "manager"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("archive/", views.Archive_list_view, name="archive-list"),
    path("manager/settings/<int:pk>/", views.Settings.as_view(), name="group-settings"),
    path('group/<int:pk>/', views.group_detail_function_view, name='group_detail'),
    path('group/<int:group_id>/debtors/', views.group_debtors_view, name='group-debtors'),


    path('manager/user/',views.UserListView.as_view(),name='user-list'),
    path('manager/user/create/',views.UserCreateView.as_view(),name='user-create'),
    path('manager/user/<int:pk>/update/',views.UserUpdateView.as_view(),name='user-update'),
    path('manager/user/<int:pk>/delete/',views.UserDeleteView.as_view(),name='user-delete'),

    path("api/attendance/", views.AttendanceListAPIView.as_view(), name="attendance-list"),
    path("api/attendance/save/", views.SaveAttendanceAPIView.as_view(), name="save-attendance"),
    path("attendance/<int:group_id>/", views.AttendanceView.as_view(), name="attendance-page"),
    path("api/groups/<int:group_id>/students/", views.GroupStudentsAPIView.as_view(), name="group-students"),

    path('manager/grades/<int:group_id>/', views.GradesView.as_view(), name='grades'),
    path('api/groups/<int:group_id>/students/', views.GroupStudentsAPIView.as_view(), name='group-students'),
    path('api/grades/', views.GradesListAPIView.as_view(), name='grades-list'),
    path('manager/api/grades/save-single/', views.SaveSingleGradeAPIView.as_view(), name='save-single-grade'),
    path('api/grades/save/', views.SaveGradeAPIView.as_view(), name='save-grades'),

    path("user/list/", views.UserListView.as_view(), name="user-list"),
    path("user/create/", views.UserCreateView.as_view(), name="user-create"),
    path("user/<int:pk>/update/", views.UserUpdateView.as_view(), name="user-update"),
    path("user/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user-delete"),

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

    path("payment/", views.PaymentListView.as_view(), name='payment-list'),
    path('payment/create', views.PaymentCreateView.as_view(), name='payment-create'),
    path('payment/<int:pk>/delete', views.PaymentDeleteView.as_view(), name='payment-delete'),
    path('payment/<int:pk>/update', views.PaymentUpdateView.as_view(), name='payment-update'),
    path('payment/ajax-data/', views.ajax_payment_data, name='ajax-payment-data'),
    path('payments/', views.payment_list, name='payment-list'),

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

    path("wages/list/", views.WagesListView.as_view(), name="wages-list"),
    path("wages/create/", views.WagesCreateView.as_view(), name="wages-create"),
    path("wages/<int:pk>/update/", views.WagesUpdateView.as_view(), name="wages-update"),
    path("wages/<int:pk>/delete/", views.WagesDeleteView.as_view(), name="wages-delete"),
    path("ajax/load-employees/", views.get_employees_by_role, name="get-employees-by-role"),
    path('wages/', views.wages_list, name='wages_list'),

    path("api/attendance/", views.AttendanceListAPIView.as_view(), name="attendance-page"),
    path("attendance/<int:group_id>/", views.AttendanceView.as_view(), name="attendance-list"),
    path("api/attendance/save/", views.SaveAttendanceAPIView.as_view(), name="attendance-save"),
    path("api/groups/<int:group_id>/students/", views.GroupStudentsAPIView.as_view(), name="group-students"),
    
]
