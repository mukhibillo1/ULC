from django.urls import path
from accountant import views
app_name = "accountant"

urlpatterns = [
    path("", views.HomeView.as_view(), name='home'),
    path('api/search/', views.universal_search, name='universal-search'),
    path("manager/settings/<int:pk>/", views.Settings.as_view(), name="group-settings"),
    path('group/<int:pk>/', views.group_detail_function_view, name='group_detail'),
    path('api/search/', views.universal_search, name='universal-search'),
    path('group/<int:group_id>/debtors/', views.group_debtors_view, name='group-debtors'),

    path("teacher/list/", views.TeacherListView.as_view(), name="teacher-list"),
    path("teacher/create/", views.TeacherCreateView.as_view(), name="teacher-create"),
    path("teacher/<int:pk>/update/", views.TeacherUpdateView.as_view(), name="teacher-update"),
    path("teacher/<int:pk>/delete/", views.TeacherDeleteView.as_view(), name="teacher-delete"),

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

    path("wages/list/", views.WagesListView.as_view(), name="wages-list"),
    path("wages/create/", views.WagesCreateView.as_view(), name="wages-create"),
    path("wages/<int:pk>/update/", views.WagesUpdateView.as_view(), name="wages-update"),
    path("wages/<int:pk>/delete/", views.WagesDeleteView.as_view(), name="wages-delete"),
    path("ajax/load-employees/", views.get_employees_by_role, name="get-employees-by-role"),
    path('wages/', views.wages_list, name='wages_list'),

    path('salaries/', views.TeacherSalaryListView.as_view(), name='tsalary-list'),
    path('salaries/create/', views.TeacherSalaryCreateView.as_view(), name='tsalary-create'),
    path('salaries/<int:pk>/update/', views.TeacherSalaryUpdateView.as_view(), name='tsalary-update'),
    path('salaries/<int:pk>/delete/', views.TeacherSalaryDeleteView.as_view(), name='tsalary-delete'),
    path("ajax/get-teachers/", views.get_teachers_by_course, name="ajax_teachers"),
    path("ajax/get-teacher-info/", views.get_teacher_info, name="ajax_teacher_info"),
    path("ajax/get-teacher-groups/", views.get_teacher_groups, name="ajax_teacher_groups"),

    path('others/', views.notification_others_view, name="others-notification"),
    path('notifications/count/', views.notification_count_view, name='notification-count'),
    path('notifications/list/', views.notification_list_api_view, name='notification-list-api'),
    path('notifications/<int:notification_id>/detail/', views.notification_detail_api_view, name='notification-detail-api'),
    
    # Notification Pages
    path('notifications/inbox/', views.notification_inbox_view, name='notification-inbox'),
    path('notifications/mark-all-read/', views.notification_mark_all_read_view, name='notification-mark-all-read'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete_view, name='notification-delete'),
]
