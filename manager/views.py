from django.shortcuts import render ,get_object_or_404
from django.views import View
from django.contrib import messages
from django.views.generic import ListView , DeleteView, TemplateView, ListView, View
from django.urls import reverse_lazy   
from django.db.models import Q 
from common import models
from django.views import View
from django.db.models import Sum
from django.views.generic import ListView, DetailView
from django.utils.dateparse import parse_date
from rest_framework import viewsets, status 
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from common import models , serializers 
from manager import forms
from django.db import transaction
from common.models import Group,Course,Teacher,Student,Debt
from helpers.views import CreateView, UpdateView, DeleteView
from common import mixins
from datetime import date ,datetime , timedelta
import calendar
from django.utils import timezone
from django.http import JsonResponse
from common.models import Attendance , Student ,Grade,Wages
from common.serializers import AttendanceSerializer , StudentSerializer 
import json
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from helpers.permissions import ManagerPassesTestMixin
from django.db.models import Q




class HomeView(ManagerPassesTestMixin,View):
    def get(self, request):
        print(request.user.role)
        return render(request, "base/index.html")


class Settings(ListView):
    template_name = "manager/settings/list.html"
    model = Group
    context_object_name = "groups"

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Group.objects.filter(id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_queryset().first()
        
        context['group'] = group
        context['active_tab'] = 'all'
        
        if group:
            # O'quvchilar
            context['students'] = group.students.all()
            context['has_students'] = group.students.exists()
            
            # Teacher ma'lumotlari
            context['teacher'] = group.teacher
            
            # Monthly salary hisoblash
            if group.teacher:
                salary_data = group.get_teacher_monthly_salary()
                context['salary_data'] = salary_data
                context['monthly_salary'] = salary_data.get('monthly_salary', 0)
                context['salary_details'] = salary_data.get('details', {})
            else:
                context['salary_data'] = None
                context['monthly_salary'] = 0
                context['salary_details'] = {}
            
            # Qo'shimcha foydali ma'lumotlar
            context['students_count'] = group.get_active_students_count()
            context['total_payment'] = group.get_total_payment()
            context['active_students'] = group.students.filter(status="Active")
            
        else:
            context['students'] = None
            context['has_students'] = False
            context['teacher'] = None
            context['salary_data'] = None
            context['monthly_salary'] = 0
            context['salary_details'] = {}
            context['students_count'] = 0
            context['total_payment'] = 0
            context['active_students'] = []
        
        return context
    
def group_detail_function_view(request, pk):
    """Function-based view variant"""
    group = get_object_or_404(Group, pk=pk)
    
    # Teacher salary hisoblash
    salary_data = group.get_teacher_monthly_salary()
    
    # O'quvchilar
    students = group.students.filter(status="Active")
    students_count = group.get_active_students_count()
    
    context = {
        'group': group,
        'teacher': group.teacher,
        'salary_data': salary_data,
        'students': students,
        'students_count': students_count,
        'total_payment': group.get_total_payment(),
    }
    
    return render(request, 'manager/settings/list.html', context)

def group_debtors_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    debts = models.Payment.objects.filter(group=group, debt__gt=0)
    
    debt = []
    for p in debts:
        p.remaining_debt = p.group.price - p.amount
        p.phone = p.student.phone  
        debt.append(p)
    return render(request, 'manager/debtors/list.html', {
        'group': group,
        'debts': debts,
    })


class TeacherListView(ListView):
    model = models.Teacher
    template_name = "manager/teacher/list.html"
    context_object_name = "objects"
    paginate_by = 10

    def get_queryset(self):
        queryset = models.Teacher.objects.filter(status="Active").order_by("id")
        search = self.request.GET.get("search", None)
        course_id = self.request.GET.get("course", None)

        # Search filter
        if search:
            queryset = queryset.filter(full_name__icontains=search)

        # Course filter
        if course_id:
            queryset = queryset.filter(course__id=course_id) 

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = models.Course.objects.all()
        context['search'] = self.request.GET.get("search", "")
        context['course_id'] = self.request.GET.get("course", "")
        return context

class TeacherCreateView(CreateView):
    model = models.Teacher
    form_class = forms.TeacherForm
    template_name = "manager/teacher/create.html"
    context_object_name = "object"
    success_url = "manager:teacher-list"
    success_create_url = 'manager:teacher-create'
    
    
class TeacherUpdateView(UpdateView):
    model = models.Teacher
    form_class = forms.TeacherForm
    template_name = "manager/teacher/update.html"
    context_object_name = "object"
    success_url = "manager:teacher-list"
    success_create_url = 'manager:teacher-update'
    

class TeacherDeleteView(DeleteView):
    model = models.Teacher
    success_url = 'manager:teacher-list'
    
   

class CourseListView(ListView):
    model = models.Course
    template_name = "manager/course/list.html"
    context_object_name = "courses"
    def get_queryset(self):
        queryset = models.Course.objects.all().order_by("id")
        search = self.request.GET.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
            )
        return queryset

class CourseGroupListView(ListView):
    model = Group
    template_name = "manager/course/course_groups.html"
    context_object_name = "groups"

    def get_queryset(self):
        course_id = self.kwargs["pk"]
        return Group.objects.filter(course_id=course_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = Course.objects.get(pk=self.kwargs["pk"])
        return context

class CourseCreateView(CreateView):
    model = models.Course
    form_class = forms.CourseForm
    context_object_name = "object"
    template_name = "manager/course/create.html"
    success_url ="manager:course-list"
    success_create_url ="manager:course-list"


class CourseUpdateView(UpdateView):
    model = models.Course
    form_class = forms.CourseForm
    context_object_name = "object"
    template_name = "manager/course/update.html"
    success_url = "manager:course-list"
    success_update_url = "manager:course-update"


class CourseDeleteView(DeleteView):
    model = models.Course
    success_url ="manager:course-list"


class GroupListView(ListView):
    model = models.Group
    template_name = "manager/group/list.html"
    context_object_name = "objects"
    paginate_by = 10
    
    def get_queryset(self):
        queryset = models.Group.objects.filter(status="Active").order_by("id")
        
        # Search
        search = self.request.GET.get("search", None)
        if search:
            queryset = queryset.filter(Q(title__icontains=search))
        
        # Filter by lesson days
        day = self.request.GET.get('day')
        if day == 'odd':
            queryset = queryset.filter(lesson_days='mo we fri')
        elif day == 'even':
            queryset = queryset.filter(lesson_days='tu thu sa')
        
        # Filter by teacher
        teacher_id = self.request.GET.get('teacher')
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        
        # Filter by course
        course_id = self.request.GET.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = models.Teacher.objects.filter(status='Active')
        context['courses'] = models.Course.objects.all()
        return context


class GroupCreateView(CreateView):
    model = models.Group
    template_name = "manager/group/create.html"
    context_object_name = 'object'
    form_class = forms.GroupForm
    success_url ="manager:group-list"
    success_update_url ="manager:group-update" 


class GroupUpdateView(UpdateView):
    model = models.Group
    template_name = "manager/group/update.html"
    context_object_name = 'object'
    form_class = forms.GroupForm
    success_url ="manager:group-list"
    success_update_url ="manager:group-update"

class GroupDeleteView(DeleteView):
    model = models.Group
    success_url ="manager:group-list"




    
class StudentListView(ManagerPassesTestMixin, ListView):
    model = models.Student
    template_name = "manager/student/list.html"
    context_object_name = "objects"
    paginate_by = 10

    def get_queryset(self):
        queryset = models.Student.objects.filter(status="Active").order_by("id")
        search = self.request.GET.get("search")
        group_id = self.request.GET.get("group")

        # Search filter
        if search:
            queryset = queryset.filter(full_name__icontains=search)

        # Group filter
        if group_id:
            queryset = queryset.filter(group_id=group_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = models.Group.objects.all()
        context['search'] = self.request.GET.get("search", "")
        context['group_id'] = self.request.GET.get("group", "")
        return context

class StudentCreateView(CreateView):
    model = models.Student
    form_class = forms.StudentForm
    template_name = "manager/student/create.html"
    context_object_name = "object"
    success_url = "manager:student-list"
    success_create_url = 'manager:student-create'
    
    
class StudentUpdateView(UpdateView):
    model = models.Student
    form_class = forms.StudentForm
    template_name = "manager/student/update.html"
    context_object_name = "object"
    success_url ="manager:student-list"
    success_create_url = 'manager:student-update'
    

class StudentDeleteView(DeleteView):
    model = models.Student
    success_url ='manager:student-list'




class UserListView(ListView):
    model = models.BaseUser
    template_name = "manager/user/list.html"
    context_object_name = "objects"  

    paginate_by = 10


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  
        return kwargs

class UserCreateView(CreateView):
    model = models.BaseUser
    form_class = forms.UserForm
    template_name = "manager/user/create.html"
    context_object_name = "object"
    success_url = "manager:user-list"
    success_create_url = "manager:user-create"


class UserUpdateView(UpdateView):
    model = models.BaseUser
    form_class = forms.UserForm
    template_name = "manager/user/update.html"
    context_object_name = "object"
    success_url = "manager:user-list"
    success_update_url = "manager:user-update"


class UserDeleteView(DeleteView):
    model = models.BaseUser
    success_url = "manager:user-list"

   


class PaymentListView(ListView):
    model = models.Payment
    template_name = "manager/payment/list.html"
    context_object_name = "objects" 
    paginate_by = 10

    def get_queryset(self):
        queryset = models.Payment.objects.all().order_by("id")
        search = self.request.GET.get("search", None)
        
        if search:
            queryset = queryset.filter(
                Q(student__full_name__icontains=search) | Q(group__title__icontains=search)
            )
        return queryset
    
class PaymentCreateView(CreateView):
    model = models.Payment
    form_class = forms.PaymentForm
    template_name = "manager/payment/create.html"
    success_url = "manager:payment-list"

    def form_valid(self, form):
        with transaction.atomic():
            student = form.cleaned_data['student']
            group = form.cleaned_data['group']
            amount = form.cleaned_data['amount'] or 0
            group_price = group.price or 0

            # To‘lov miqdorini group narxiga tenglashtiramiz (ixtiyoriy)
            form.instance.amount = amount

            # Balance va qarzni hisoblash
            difference = group_price - amount  # yetmagan summa

            # Studentning balansini yangilash
            student.balance -= amount

            # Agar yetmagan bo‘lsa — qarzga qo‘shamiz
            if difference > 0:
                student.debt += difference

            student.save(update_fields=['balance', 'debt'])
            messages.success(self.request, f"{student.full_name} to‘lovi muvaffaqiyatli qabul qilindi.")

        return super().form_valid(form)
    
class PaymentUpdateView(UpdateView):
    model = models.Payment
    form_class = forms.PaymentForm
    template_name = "manager/payment/create.html"
    success_url = "manager:payment-list"

    def form_valid(self, form):
        with transaction.atomic():
            old_payment = self.get_object()
            student = form.cleaned_data['student']
            group = form.cleaned_data['group']
            new_amount = form.cleaned_data['amount'] or 0
            group_price = group.price or 0

            # Avvalgi balansni tiklab olamiz (eski to‘lovni qaytarish)
            student.balance += old_payment.amount

            # Yangi to‘lovni hisobga olamiz
            student.balance -= new_amount

            # Qarzni yangilash
            difference = group_price - new_amount
            if difference > 0:
                student.debt += difference

            student.save(update_fields=['balance', 'debt'])
            form.instance.amount = new_amount

            messages.success(self.request, f"{student.full_name} to‘lovi yangilandi.")

        return super().form_valid(form)
    
class PaymentDeleteView(DeleteView):
    model = models.Payment
    template_name = "manager/payment/delete.html"
    context_object_name = "object"
    success_url = "manager:payment-list"

    def delete(self, request, *args, **kwargs):
        payment = self.get_object()
        student = payment.student

        # To‘lovni o‘chirsak — balansni qaytaramiz
        student.balance += payment.amount
        student.save(update_fields=['balance'])

        messages.success(request, f"{student.full_name} to‘lovi o‘chirildi.")
        return super().delete(request, *args, **kwargs)

def ajax_payment_data(request):
    group_id = request.GET.get('group')
    if not group_id:
        return JsonResponse({'students': [], 'monthly_fee': 0})

    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'students': [], 'monthly_fee': 0})

    # Shu groupdagi studentlar
    students = group.students.all()
    student_list = []
    for student in students:
        student_list.append({
            'id': student.id,
            'name': student.full_name,
            'balance': float(student.balance),
            'debt': float(getattr(student, 'debt', 0))
        })

    return JsonResponse({
        'students': student_list,
        'monthly_fee': float(group.price)
    })


def payment_list(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    group_id = request.GET.get('group') 


    objects = models.Payment.objects.select_related('student', 'group').all().order_by('-date')

    # Group filter
    if group_id:
        objects = objects.filter(group_id=group_id)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if month and year:
            objects = objects.filter(
                date__month=int(month),
                date__year=int(year),
            )
            data = [
            {
                "id": p.id,
                "student_name": p.student.full_name,
                "student_initial": p.student.full_name[0],
                "group": str(p.group),
                "amount": float(p.amount),
                "date": p.date.strftime("%Y-%m-%d"),
                "debt": float(p.debt),
                "update_url": f"/manager/payment/{p.id}/update",
                "delete_url": f"/manager/payment/{p.id}/delete",
            }for p in objects]

            return JsonResponse({
                "payments": data,
                "total": len(data)
            })



    # HTML uchun pagination
    paginator = Paginator(objects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    groups = models.Group.objects.all()

    context = {
        'objects': page_obj,
        'page_obj': page_obj,
        'groups':groups,
    }
    return render(request, 'manager/payment/list.html', context)


class LeadListView(ListView):
    model = models.Lead
    template_name = "manager/lead/list.html"
    context_object_name = "objects"
    paginate_by = 10

    def get_queryset(self):
        queryset = models.Lead.objects.all().order_by("id")

        # --- Search ---
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
        "Request": models.Lead.objects.filter(status="Request"),
        "Trial": models.Lead.objects.filter(status="Trial"),
        "Ingroup": models.Lead.objects.filter(status="In group"),
    }
        return context


class LeadCreateView(CreateView):
    model = models.Lead
    form_class = forms.LeadForm
    template_name = "manager/lead/create.html"
    context_object_name = "object"
    success_url = "manager:lead-list"
    success_create_url = 'manager:lead-create'
    
    
class LeadUpdateView(UpdateView):
    model = models.Lead
    form_class = forms.LeadForm
    template_name = "manager/lead/update.html"
    context_object_name = "object"
    success_url ="manager:lead-list"
    success_create_url = 'manager:lead-update'
    

class LeadDeleteView(DeleteView):
    model = models.Lead
    success_url ='manager:lead-list'

class ClassroomListView(ListView):
    model = models.Classroom
    template_name = "manager/classroom/list.html"
    context_object_name = "objects"
    paginate_by = 10
    def get_queryset(self):
        queryset = models.Classroom.objects.filter().order_by("id")
        search = self.request.GET.get("search", None)
        
        if search:
            queryset = queryset.filter(
                Q(Name__icontains=search)
            )
        return queryset

class ClassroomCreateView(CreateView):
    model = models.Classroom
    form_class = forms.ClassroomForm
    template_name = "manager/classroom/create.html"
    context_object_name = "object"
    success_url = "manager:classroom-list"
    success_create_url = 'manager:classroom-create'
    
    
class ClassroomUpdateView(UpdateView):
    model = models.Classroom
    form_class = forms.ClassroomForm
    template_name = "manager/classroom/update.html"
    context_object_name = "object"
    success_url = "manager:classroom-list"
    success_create_url = 'manager:classroom-update'
    

class ClassroomDeleteView(DeleteView):
    model = models.Classroom
    success_url = 'manager:classroom-list'
    


def schedule_view(request):
    rooms = models.Classroom.objects.all()

    hours = []
    start_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("18:00", "%H:%M")
    current_time = start_time
    while current_time <= end_time:
        hours.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=30)

    filter_day = request.GET.get('day')
    # Har bir xonaga tegishli guruhlarni olish
    room_groups = {}
    room_groups_json = {}

    for room in rooms:
        groups_in_room = Group.objects.filter(room=room).order_by('start_time').select_related('teacher')

        if filter_day == 'odd':
                # Toq kunlar = mo we fri
                groups_in_room = groups_in_room.filter(lesson_days='mo we fri')
        elif filter_day == 'even':
                # Juft kunlar = tu thu sa
                groups_in_room = groups_in_room.filter(lesson_days='tu thu sa')

        room_groups[room] = groups_in_room

        # JSON uchun formatlash
        room_groups_json[room.name] = [
            {
                'name': group.title,
                'teacher': str(group.teacher) if group.teacher else 'O\'qituvchi yo\'q',
                'students_count': group.students.count(),
                'start_time': str(group.start_time) if hasattr(group, 'start_time') else '00:00',
                'end_time': str(group.end_time) if hasattr(group, 'end_time') else None
            }
            for group in groups_in_room
        ]

    context = {
        "hours": json.dumps(hours),
        "room_groups": room_groups,
        "room_groups_json": json.dumps(room_groups_json),
    }

    return render(request, "manager/classroom/schedule.html", context)

def Archive_list_view(request):
    context = {
        "archive_teachers": Teacher.objects.filter(status="Archive"),
        "archive_students": Student.objects.filter(status="Archive"),
        "groups_finished": Group.objects.filter(status="Finished"),
    }
    return render(request, "manager/archived/list.html", context)
    



class AttendanceView(View):
    def get(self, request, group_id):
        group = get_object_or_404(models.Group, id=group_id)
        return render(request, "manager/attendance/attendance.html", {"group": group})


class GroupStudentsAPIView(ListAPIView):
    serializer_class = serializers.StudentSerializer
    
    def get_queryset(self):
        return models.Student.objects.filter(
            group_id=self.kwargs['group_id']
        ).only('id', 'full_name', 'date_joined')


class AttendanceListAPIView(ListAPIView):
    serializer_class = serializers.AttendanceSerializer

    def get_queryset(self):
        params = self.request.query_params
        filters = Q()
        
        if group_id := params.get('group'):
            filters &= Q(group_id=group_id)
        if start := parse_date(params.get('start_date', '')):
            filters &= Q(date_time__gte=start)
        if end := parse_date(params.get('end_date', '')):
            filters &= Q(date_time__lte=end)
        
        return models.Attendance.objects.filter(filters).select_related('student')


class SaveAttendanceAPIView(APIView):
    def post(self, request):
        attendance_list = request.data.get('attendance', [])
        
        if not attendance_list:
            return Response({'success': False, 'error': 'No data provided'})
        
        # Bugungi sanani olish
        today = timezone.now().date()
        
        data_map = {}
        student_ids = set()
        dates = set()
        
        for item in attendance_list:
            date_str = item.get('date_time', '').split('T')[0]
            if date_obj := parse_date(date_str):
                # O'tgan kunlarni tahrirlashni oldini olish
                if date_obj < today:
                    continue  # O'tgan kunlarni o'tkazib yuborish
                
                student_id = item['student']
                key = f"{student_id}-{date_obj}"
                data_map[key] = {
                    'student_id': student_id,
                    'group_id': item['group'],
                    'date': date_obj,
                    'is_present': item['is_present']
                }
                student_ids.add(student_id)
                dates.add(date_obj)
        
        if not data_map:
            return Response({
                'success': False, 
                'error': 'O\'tgan kunlarni tahrirlash mumkin emas'
            })
        
        existing = {
            f"{obj.student_id}-{obj.date_time}": obj
            for obj in models.Attendance.objects.filter(
                student_id__in=student_ids,
                date_time__in=dates
            )
        }
        
        to_create = []
        to_update = []
        
        for key, data in data_map.items():
            if key in existing:
                obj = existing[key]
                obj.is_present = data['is_present']
                to_update.append(obj)
            else:
                to_create.append(models.Attendance(
                    student_id=data['student_id'],
                    group_id=data['group_id'],
                    date_time=data['date'],
                    is_present=data['is_present']
                ))
        
        created = updated = 0
        if to_create:
            created = len(models.Attendance.objects.bulk_create(to_create, ignore_conflicts=True))
        if to_update:
            updated = models.Attendance.objects.bulk_update(to_update, ['is_present'])
        
        return Response({'success': True, 'created': created, 'updated': updated})
    

class EmployeeListView(ListView):
    model = models.Employee
    template_name = "manager/employee/list.html"
    context_object_name = "objects"
    paginate_by = 10
    def get_queryset(self):
        queryset = models.Employee.objects.all().order_by("id")
        search = self.request.GET.get("search", None)
        
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
            )
        return queryset

class EmployeeCreateView(CreateView):
    model = models.Employee
    form_class = forms.EmployeeForm
    template_name = "manager/employee/create.html"
    context_object_name = "object"
    success_url = "manager:employee-list"
    success_create_url = 'manager:employee-create'
    
    
class EmployeeUpdateView(UpdateView):
    model = models.Employee
    form_class = forms.EmployeeForm
    template_name = "manager/employee/update.html"
    context_object_name = "object"
    success_url ="manager:employee-list"
    success_create_url = 'manager:employee-update'
    

class EmployeeDeleteView(DeleteView):
    model = models.Employee
    success_url ='manager:employee-list'



class WagesListView(ListView):
    model = models.Wages
    template_name = "manager/Wages/list.html"
    context_object_name = "objects"
    paginate_by = 10

    def get_queryset(self):
        queryset = models.Wages.objects.select_related("employee").order_by("-date")
        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(employee__full_name__icontains=search)

        return queryset


class WagesCreateView(CreateView):
    model = models.Wages
    form_class = forms.WagesForm
    template_name = "manager/Wages/create.html"
    success_url = "manager:wages-list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["roles"] = models.Employee.ROLE_CHOICES
        return context



class WagesUpdateView(UpdateView):
    model = models.Wages
    form_class = forms.WagesForm
    template_name = "manager/Wages/update.html"
    success_url = "manager:wages-list"



class WagesDeleteView(DeleteView):
    model = models.Wages
    success_url = "manager:wages-list"


def get_employees_by_role(request):
    role_name = request.GET.get("role", "")

    employees = []
    if role_name:
        employees = models.Employee.objects.filter(
            role=role_name
        ).values("id", "full_name", "salary")

    return JsonResponse({"employees": list(employees)})


def wages_list(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    role = request.GET.get('role') 

    objects = models.Wages.objects.select_related('employee').all().order_by('-date')

    if role:
        objects = objects.filter(role=role)

    # AJAX bo'limi
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        if month and year:
            objects = objects.filter(
                date__month=int(month),
                date__year=int(year),
            )

        # ROLE filtri AJAXda ham ishlasin
        if role:
            objects = objects.filter(role=role)

        data = [{
            'id': w.id,
            'employee_name': w.employee.full_name,
            'employee_initial': w.employee.full_name[0],
            'role': w.get_role_display(),
            'method': w.method,
            'amount': float(w.amount),
            'date': w.date.strftime('%Y-%m-%d'),
            "update_url": f"/manager/wages/{w.id}/update",
            "delete_url": f"/manager/wages/{w.id}/delete",
        } for w in objects]

        return JsonResponse({'wages': data, 'total': len(data)})

    paginator = Paginator(objects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    role_choices = models.Employee.ROLE_CHOICES

    return render(request, 'manager/Wages/list.html', {
        'objects': page_obj,
        'role_choices': role_choices,
    })



class GradesView(View):
    def get(self, request, group_id):
        group = get_object_or_404(models.Group, id=group_id)
        return render(request, "manager/grade/grade.html", {"group": group})

# 2. GroupStudentsAPIView (xuddi shunaqa qoladi)
class GroupStudentsAPIView(ListAPIView):
    serializer_class = serializers.StudentSerializer
    
    def get_queryset(self):
        return models.Student.objects.filter(
            group_id=self.kwargs['group_id']
        ).only('id', 'full_name', 'date_joined')

# 3. AttendanceListAPIView → GradesListAPIView
class GradesListAPIView(ListAPIView):
    serializer_class = serializers.GradeSerializer

    def get_queryset(self):
        params = self.request.query_params
        filters = Q()
        
        if group_id := params.get('group'):
            filters &= Q(group_id=group_id)
        if start := parse_date(params.get('start_date', '')):
            filters &= Q(date_time__gte=start)
        if end := parse_date(params.get('end_date', '')):
            filters &= Q(date_time__lte=end)
        
        return models.Grade.objects.filter(filters).select_related('student')
    
class SaveSingleGradeAPIView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        group_id = request.data.get('group_id')
        date_str = request.data.get('date')
        grade_value = request.data.get('grade')

        if not all([student_id, group_id, date_str, grade_value]):
            return Response({'success': False, 'error': 'Incomplete data'})

        today = timezone.localdate()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        if date_obj != today and date_obj != today + timezone.timedelta(days=1):
            return Response({'success': False, 'error': "Foydalanuvchi faqat bugun yoki ertaga baho qo'yishi mumkin"})

        # Yangilash yoki yaratish
        grade_obj, created = models.Grade.objects.update_or_create(
            student_id=student_id,
            group_id=group_id,
            date_time=date_obj,
            defaults={'grade': grade_value}
        )

        return Response({'success': True, 'created': created, 'updated': not created})
    
# 4. SaveAttendanceAPIView → SaveGradeAPIView
class SaveGradeAPIView(APIView):
    """
    Single or multiple grade save endpoint
    """
    def post(self, request):
        grade_list = request.data.get('grades', [])
        
        if not grade_list:
            return Response({'success': False, 'error': 'No data provided'})
        
        today = timezone.now().date()
        
        data_map = {}
        student_ids = set()
        dates = set()
        
        for item in grade_list:
            date_str = item.get('date', '').split('T')[0]
            if date_obj := parse_date(date_str):
                # O'tgan kunlarni tahrirlashni oldini olish
                if date_obj < today:
                    continue
                
                student_id = item['student_id']
                key = f"{student_id}-{date_obj}"
                data_map[key] = {
                    'student_id': student_id,
                    'group_id': item['group_id'],
                    'date': date_obj,
                    'grade': item['grade']
                }
                student_ids.add(student_id)
                dates.add(date_obj)
        
        if not data_map:
            return Response({
                'success': False,
                'error': 'O\'tgan kunlarni tahrirlash mumkin emas'
            })
        
        existing = {
            f"{obj.student_id}-{obj.date_time}": obj
            for obj in models.Grade.objects.filter(
                student_id__in=student_ids,
                date_time__in=dates
            )
        }
        
        to_create = []
        to_update = []
        
        for key, data in data_map.items():
            if key in existing:
                obj = existing[key]
                obj.grade = data['grade']
                to_update.append(obj)
            else:
                to_create.append(models.Grade(
                    student_id=data['student_id'],
                    group_id=data['group_id'],
                    date_time=data['date'],
                    grade=data['grade']
                ))
        
        created = updated = 0
        if to_create:
            created = len(models.Grade.objects.bulk_create(to_create, ignore_conflicts=True))
        if to_update:
            updated = models.Grade.objects.bulk_update(to_update, ['grade'])
        
        return Response({'success': True, 'created': created, 'updated': updated})
