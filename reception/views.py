from helpers.permissions import ReceptionPassesTestMixin
from django.shortcuts import render ,get_object_or_404 , redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.views.decorators.http import require_GET
from django.apps import apps
from manager.forms import NotificationForm, InformationsForm ,TeacherSalaryForm
from django.contrib import messages
from django.views.generic import ListView , DeleteView, TemplateView, ListView, View
from django.urls import reverse_lazy, reverse 
from django.db.models import Q 
from common import models
from django.views import View
from django.db.models import Sum
from common.models import Notification
from django.views.generic import ListView, DetailView
from django.utils.dateparse import parse_date
from django.utils import timezone
from rest_framework import viewsets, status 
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from common import models , serializers 
from manager import forms
from django.db import transaction
from common.models import Group,Course,Teacher,Student,Debt
from helpers.views import CreateView, UpdateView, DeleteView
from common import mixins
from datetime import date ,datetime , timedelta
import calendar
from django.http import JsonResponse
from common.models import Attendance , Student ,Grade,Wages,Informations, Employee, BaseUser
from common.serializers import AttendanceSerializer , StudentSerializer 
import json , traceback
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.db.models.functions import TruncMonth


class HomeView(ReceptionPassesTestMixin,TemplateView):
    template_name = "reception/base/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Yil va oy parametrlari
        year = int(self.request.GET.get('year', datetime.now().year))
        month = int(self.request.GET.get('month', datetime.now().month))
        
        # Joriy oy boshi va oxiri
        month_start = datetime(year, month, 1).date()
        if month == 12:
            month_end = datetime(year + 1, 1, 1).date()
        else:
            month_end = datetime(year, month + 1, 1).date()
        
        # O'tgan oy
        if month == 1:
            prev_month_start = datetime(year - 1, 12, 1).date()
            prev_month_end = datetime(year, 1, 1).date()
        else:
            prev_month_start = datetime(year, month - 1, 1).date()
            prev_month_end = month_start
        
        # LIDLAR
        current_leads = models.Lead.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        prev_leads = models.Lead.objects.filter(
            created_at__gte=prev_month_start,
            created_at__lt=prev_month_end
        ).count()
        
        leads_diff = current_leads - prev_leads
        
        # SINOV DARSLARI
        current_trials = models.Lead.objects.filter(
            status='Trial',
            date_joined__gte=month_start,
            date_joined__lt=month_end
        ).count()
        
        prev_trials = models.Lead.objects.filter(
            status='Trail',
            created_at__gte=prev_month_start,
            created_at__lt=prev_month_end
        ).count()
        
        trials_diff = current_trials - prev_trials

        current_request = models.Lead.objects.filter(
            status='Request',
            date_joined__gte=month_start,
            date_joined__lt=month_end
        ).count()
        
        # FAOL TALABALAR
        active_students = models.Lead.objects.filter(
            status='In group',
            date_joined__gte=month_start,
            date_joined__lt=month_end
        ).count()
        
        total_active = models.Lead.objects.filter(status='In group').count()
        
        prev_active = models.Student.objects.filter(
            status='Active',
            date_joined__gte=prev_month_start,
            date_joined__lt=prev_month_end
        ).count()
        
        students_diff = active_students - prev_active
        
        # MUZLATILGANLAR
        frozen_count = models.Student.objects.filter(
            status='Archive',
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()

        # ========== SCHEDULE UCHUN MA'LUMOTLAR ==========
        # Soatlar (30 daqiqalik intervallar)
        hours = []
        start_time = datetime.strptime("08:00", "%H:%M")
        end_time = datetime.strptime("18:00", "%H:%M")
        current_time = start_time
        while current_time <= end_time:
            hours.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=30)

        # Filter parametri
        filter_day = self.request.GET.get('day')

        # Xonalar va guruhlar
        rooms = models.Classroom.objects.all()
        room_groups_json = {}

        for room in rooms:
            groups_in_room = models.Group.objects.filter(room=room).order_by('start_time').select_related('teacher')
            
            # Filter qo'llash
            if filter_day == 'odd':
                # Toq kunlar = mo we fri
                groups_in_room = groups_in_room.filter(lesson_days='mo we fri')
            elif filter_day == 'even':
                # Juft kunlar = tu thu sa
                groups_in_room = groups_in_room.filter(lesson_days='tu thu sa')
            
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

        context.update({
            'selected_year': year,
            'selected_month': month,
            
            # Lidlar
            'leads_count': current_leads,
            'leads_diff': leads_diff,
            'leads_diff_abs': abs(leads_diff),
            
            # Sinov darslari
            'trials_count': current_trials,
            'trials_diff': trials_diff,
            'trials_diff_abs': abs(trials_diff),

            # Request
            'Request_count': current_request,
            
            # Faol talabalar
            'active_students_new': active_students,
            'active_students_total': total_active,
            'students_diff': students_diff,
            'students_diff_abs': abs(students_diff),
            
            'frozen_count': frozen_count,
            
            # Schedule
            'hours': json.dumps(hours),
            'room_groups_json': json.dumps(room_groups_json),
            'filter_day': filter_day,  # Bu qo'shildi
        })
        
        return context



def universal_search(request):
    """Universal search for all models"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'results': []})
    
    results = []
    
    # ============ TEACHERS QIDIRISH ============
    try:
        teachers = Teacher.objects.filter(full_name__icontains=query)[:5]
        
        for teacher in teachers:
            # Teacher list sahifasiga olib boradi
            url = reverse('reception:teacher-list')
            
            results.append({
                'type': 'teacher',
                'name': teacher.full_name,
                'url': url,
                'label': 'Teacher'
            })
    except ImportError:
        print("Teacher model topilmadi")
    except Exception as e:
        print(f"Teacher search error: {e}")
    
    # ============ STUDENTS QIDIRISH ============
    try:
        students = Student.objects.filter(full_name__icontains=query)[:5]
        
        for student in students:
            # Student list sahifasiga olib boradi
            url = reverse('reception:student-list')
            
            results.append({
                'type': 'student',
                'name': student.full_name,
                'url': url,
                'label': 'Student'
            })
    except ImportError:
        print("Student model topilmadi")
    except Exception as e:
        print(f"Student search error: {e}")
    
    # ============ GROUPS QIDIRISH ============
    try:
        groups = Group.objects.filter(title__icontains=query)[:5]
        
        for group in groups:
            # Group list sahifasiga olib boradi
            url = reverse('reception:group-list')
            
            results.append({
                'type': 'group',
                'name': group.title,
                'url': url,
                'label': 'Group'
            })
    except ImportError:
        print("Group model topilmadi")
    except AttributeError as e:
        print(f"Group field xatosi (title yoki name?): {e}")
    except Exception as e:
        print(f"Group search error: {e}")
    
    # ============ COURSES QIDIRISH ============
    try:
        courses = Course.objects.filter(title__icontains=query)[:5]
        
        for course in courses:
            # Course list sahifasiga olib boradi
            url = reverse('reception:course-list')
            
            results.append({
                'type': 'course',
                'name': course.title,
                'url': url,
                'label': 'Course'
            })
    except ImportError:
        print("Course model topilmadi")
    except Exception as e:
        print(f"Course search error: {e}")
    
    # ============ EMPLOYEES QIDIRISH ============
    try:
        employees = Employee.objects.filter(full_name__icontains=query)[:5]
        
        for employee in employees:
            # Employee list sahifasiga olib boradi
            url = reverse('reception:employee-list')
            
            results.append({
                'type': 'employee',
                'name': employee.full_name,
                'url': url,
                'label': 'Staff'
            })
    except ImportError:
        print("Employee model topilmadi")
    except Exception as e:
        print(f"Employee search error: {e}")
    
    return JsonResponse({'results': results})


class Settings(ListView):
    template_name = "reception/settings/list.html"
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
    
    return render(request, 'reception/settings/list.html', context)

def group_debtors_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    debts = models.Payment.objects.filter(group=group, debt__gt=0)
    
    debt = []
    for p in debts:
        p.remaining_debt = p.group.price - p.amount
        p.phone = p.student.phone  
        debt.append(p)
    return render(request, 'reception/debtors/list.html', {
        'group': group,
        'debts': debts,
    })

def information_view(request):
    info, created = Informations.objects.get_or_create(id=1)

    if request.method == "POST":
        form = InformationsForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            form.save()
            return redirect('reception:center-info')
    else:
        form = InformationsForm(instance=info)

    return render(request, "reception/information/informations.html", {"form": form})


class TeacherListView(ListView):
    model = models.Teacher
    template_name = "reception/teacher/list.html"
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
    template_name = "reception/teacher/create.html"
    context_object_name = "object"
    success_url = "reception:teacher-list"
    success_create_url = 'reception:teacher-create'
    
    
class TeacherUpdateView(UpdateView):
    model = models.Teacher
    form_class = forms.TeacherForm
    template_name = "reception/teacher/update.html"
    context_object_name = "object"
    success_url = "reception:teacher-list"
    success_create_url = 'reception:teacher-update'
    

class TeacherDeleteView(DeleteView):
    model = models.Teacher
    success_url = 'reception:teacher-list'
    
   

class CourseListView(ListView):
    model = models.Course
    template_name = "reception/course/list.html"
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
    template_name = "reception/course/course_groups.html"
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
    template_name = "reception/course/create.html"
    success_url ="reception:course-list"
    success_create_url ="reception:course-list"


class CourseUpdateView(UpdateView):
    model = models.Course
    form_class = forms.CourseForm
    context_object_name = "object"
    template_name = "reception/course/update.html"
    success_url = "reception:course-list"
    success_update_url = "reception:course-update"


class CourseDeleteView(DeleteView):
    model = models.Course
    success_url ="reception:course-list"


class GroupListView(ListView):
    model = models.Group
    template_name = "reception/group/list.html"
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
    template_name = "reception/group/create.html"
    context_object_name = 'object'
    form_class = forms.GroupForm
    success_url ="reception:group-list"
    success_update_url ="reception:group-update" 


class GroupUpdateView(UpdateView):
    model = models.Group
    template_name = "reception/group/update.html"
    context_object_name = 'object'
    form_class = forms.GroupForm
    success_url ="reception:group-list"
    success_update_url ="reception:group-update"

class GroupDeleteView(DeleteView):
    model = models.Group
    success_url ="reception:group-list"




    
class StudentListView(ReceptionPassesTestMixin, ListView):
    model = models.Student
    template_name = "reception/student/list.html"
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
    template_name = "reception/student/create.html"
    context_object_name = "object"
    success_url = "reception:student-list"
    success_create_url = 'reception:student-create'
    
    
class StudentUpdateView(UpdateView):
    model = models.Student
    form_class = forms.StudentForm
    template_name = "reception/student/update.html"
    context_object_name = "object"
    success_url ="reception:student-list"
    success_create_url = 'reception:student-update'
    

class StudentDeleteView(DeleteView):
    model = models.Student
    success_url ='reception:student-list'




class LeadListView(ListView):
    model = models.Lead
    template_name = "reception/lead/list.html"
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
    template_name = "reception/lead/create.html"
    context_object_name = "object"
    success_url = "reception:lead-list"
    success_create_url = 'reception:lead-create'
    
    
class LeadUpdateView(UpdateView):
    model = models.Lead
    form_class = forms.LeadForm
    template_name = "reception/lead/update.html"
    context_object_name = "object"
    success_url ="reception:lead-list"
    success_create_url = 'reception:lead-update'
    

class LeadDeleteView(DeleteView):
    model = models.Lead
    success_url ='reception:lead-list'

class ClassroomListView(ListView):
    model = models.Classroom
    template_name = "reception/classroom/list.html"
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
    template_name = "reception/classroom/create.html"
    context_object_name = "object"
    success_url = "reception:classroom-list"
    success_create_url = 'reception:classroom-create'
    
    
class ClassroomUpdateView(UpdateView):
    model = models.Classroom
    form_class = forms.ClassroomForm
    template_name = "reception/classroom/update.html"
    context_object_name = "object"
    success_url = "reception:classroom-list"
    success_create_url = 'reception:classroom-update'
    

class ClassroomDeleteView(DeleteView):
    model = models.Classroom
    success_url = 'reception:classroom-list'
    


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

    return render(request, "reception/classroom/schedule.html", context)

def Archive_list_view(request):
    context = {
        "archive_teachers": Teacher.objects.filter(status="Archive"),
        "archive_students": Student.objects.filter(status="Archive"),
        "groups_finished": Group.objects.filter(status="Finished"),
    }
    return render(request, "reception/archived/list.html", context)
    


class EmployeeListView(ListView):
    model = models.Employee
    template_name = "reception/employee/list.html"
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
    template_name = "reception/employee/create.html"
    context_object_name = "object"
    success_url = "reception:employee-list"
    success_create_url = 'reception:employee-create'
    
    
class EmployeeUpdateView(UpdateView):
    model = models.Employee
    form_class = forms.EmployeeForm
    template_name = "reception/employee/update.html"
    context_object_name = "object"
    success_url ="reception:employee-list"
    success_create_url = 'reception:employee-update'
    

class EmployeeDeleteView(DeleteView):
    model = models.Employee
    success_url ='reception:employee-list'


class AttendanceView(View):
    """Davomat sahifasini ko'rsatish"""
    def get(self, request, group_id):
        group = get_object_or_404(models.Group, id=group_id)
        return render(request, "reception/attendance/attendance.html", {
            "group": group,
            "active_tab": "attendance"
        })


class GroupStudentsAPIView(ListAPIView):
    """Guruh o'quvchilarini API orqali olish"""
    serializer_class = serializers.StudentSerializer
    
    def get_queryset(self):
        return models.Student.objects.filter(
            group_id=self.kwargs['group_id']
        ).only('id', 'full_name', 'date_joined')


class AttendanceListAPIView(ListAPIView):
    """Davomatni API orqali olish"""
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
    """
    Davomatni saqlash
    - Faqat keyingi dars kunigacha ochiq
    - O'tgan kunlarni tahrirlash mumkin emas
    """
    def post(self, request):
        attendance_list = request.data.get('attendance', [])
        
        if not attendance_list:
            return Response({'success': False, 'error': 'Ma\'lumot yuborilmadi'})
        
        print(f"📥 Kelgan ma'lumotlar: {len(attendance_list)} ta davomat")
        
        # Bugungi sana
        today = timezone.now().date()
        
        # Group ma'lumotini olish (lesson_days uchun)
        first_item = attendance_list[0]
        group = models.Group.objects.get(id=first_item['group'])
        
        # Keyingi dars kunini topish
        next_lesson_date = self.get_next_lesson_date(today, group.lesson_days)
        
        print(f"📅 Bugun: {today}, Keyingi dars: {next_lesson_date}")
        
        data_map = {}
        student_ids = set()
        dates = set()
        
        for item in attendance_list:
            date_str = item.get('date_time', '').split('T')[0]
            if date_obj := parse_date(date_str):
                # Faqat bugungi kun va keyingi dars kunigacha
                if date_obj < today:
                    print(f"⛔ O'tgan kun: {date_obj}")
                    continue
                
                if date_obj > next_lesson_date:
                    print(f"⛔ Keyingi darsdan keyin: {date_obj}")
                    continue
                
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
                'error': 'Faqat bugungi kun va keyingi dars kunigacha davomat qo\'yish mumkin'
            })
        
        # Mavjud davomatlarni olish
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
                # Mavjud davomatni yangilash
                obj = existing[key]
                obj.is_present = data['is_present']
                to_update.append(obj)
            else:
                # Yangi davomat yaratish
                to_create.append(models.Attendance(
                    student_id=data['student_id'],
                    group_id=data['group_id'],
                    date_time=data['date'],
                    is_present=data['is_present']
                ))
        
        created = updated = 0
        try:
            if to_create:
                created = len(models.Attendance.objects.bulk_create(to_create, ignore_conflicts=True))
                print(f"✅ Yaratildi: {created}")
            if to_update:
                updated = models.Attendance.objects.bulk_update(to_update, ['is_present'])
                print(f"✅ Yangilandi: {updated}")
        except Exception as e:
            print(f"❌ Xatolik: {str(e)}")
            return Response({
                'success': False,
                'error': f'Bazaga saqlashda xatolik: {str(e)}'
            })
        
        return Response({
            'success': True,
            'created': created,
            'updated': updated,
            'message': f'{created} ta yangi, {updated} ta yangilandi'
        })
    
    def get_next_lesson_date(self, start_date, lesson_days_str):
        """
        Keyingi dars kunini topish
        Masalan: bugun Juma (12), keyingi dars Dushanba (15)
        → Yakshanba 23:59:59 gacha ochiq
        """
        day_map = {
            'mo': 0, 'tu': 1, 'we': 2, 'thu': 3, 
            'fri': 4, 'sa': 5, 'sun': 6
        }
        
        # Dars kunlarini raqamga o'girish
        lesson_days = []
        for day in lesson_days_str.lower().split():
            if day in day_map:
                lesson_days.append(day_map[day])
        
        lesson_days.sort()
        
        # Bugungi kun
        today_weekday = start_date.weekday()
        
        # Keyingi dars kunini topish
        next_days = [d for d in lesson_days if d > today_weekday]
        
        if next_days:
            # Shu haftada keyingi dars bor
            days_until = next_days[0] - today_weekday
        else:
            # Keyingi haftaning birinchi dars kuni
            days_until = (7 - today_weekday) + lesson_days[0]
        
        next_lesson = start_date + timedelta(days=days_until)
        
        # Keyingi darsdan bir kun oldin (deadline)
        deadline = next_lesson - timedelta(days=1)
        
        return deadline


class GradesView(View):
    def get(self, request, group_id):
        group = get_object_or_404(models.Group, id=group_id)
        return render(request, "reception/grade/grade.html", {"group": group})


class GroupStudentsAPIView(ListAPIView):
    serializer_class = serializers.StudentSerializer
    
    def get_queryset(self):
        return models.Student.objects.filter(
            group_id=self.kwargs['group_id']
        ).only('id', 'full_name', 'date_joined')


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
    """
    Bitta baho saqlash uchun endpoint
    Faqat bugun va ertaga (ertaga 23:59:59 gacha) baho qo'yish mumkin
    """
    def post(self, request):
        student_id = request.data.get('student_id')
        group_id = request.data.get('group_id')
        date_str = request.data.get('date')
        grade_value = request.data.get('grade')

        print(f"📥 Kelgan ma'lumotlar: student_id={student_id}, group_id={group_id}, date={date_str}, grade={grade_value}")

        # Ma'lumotlar to'liqligini tekshirish
        if not all([student_id, group_id, date_str, grade_value]):
            return Response({
                'success': False, 
                'error': 'Ma\'lumotlar to\'liq emas'
            })

        try:
            # Sanani parse qilish
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({
                'success': False,
                'error': 'Noto\'g\'ri sana formati'
            })

        # Bugungi sana va vaqt
        now = timezone.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)
        
        print(f"📅 Bugun: {today}, Ertaga: {tomorrow}, Kelgan sana: {date_obj}")
        
        # Ertaga soat 23:59:59 (deadline)
        tomorrow_end = timezone.make_aware(
            datetime.combine(tomorrow, datetime.max.time())
        )
        
        # Deadline o'tganligini tekshirish
        if now > tomorrow_end:
            return Response({
                'success': False,
                'error': 'Baholash muddati tugagan. Faqat bugun va ertaga baho qo\'yish mumkin'
            })
        
        # Baho qo'yilayotgan sana bugun yoki ertaga bo'lishi kerak
        if date_obj != today and date_obj != tomorrow:
            return Response({
                'success': False,
                'error': f'Faqat bugun ({today.strftime("%d.%m.%Y")}) va ertaga ({tomorrow.strftime("%d.%m.%Y")}) baho qo\'yish mumkin'
            })

        # Bahoni yangilash yoki yaratish
        try:
            grade_obj, created = models.Grade.objects.update_or_create(
                student_id=student_id,
                group_id=group_id,
                date_time=date_obj,
                defaults={'grade': grade_value}
            )
            
            print(f"✅ Baho saqlandi: ID={grade_obj.id}, Created={created}, Grade={grade_obj.grade}")
            
            return Response({
                'success': True,
                'created': created,
                'updated': not created,
                'grade_id': grade_obj.id,
                'grade_value': grade_obj.grade,
                'message': 'Baho muvaffaqiyatli saqlandi' if created else 'Baho yangilandi'
            })
        except Exception as e:
            print(f"❌ Xatolik: {str(e)}")
            return Response({
                'success': False,
                'error': f'Bazaga saqlashda xatolik: {str(e)}'
            })


class SaveGradeAPIView(APIView):
    """
    Ko'p baholarni bir vaqtda saqlash uchun endpoint
    Faqat bugun va ertaga (ertaga 23:59:59 gacha) baho qo'yish mumkin
    """
    def post(self, request):
        grade_list = request.data.get('grades', [])
        
        if not grade_list:
            return Response({
                'success': False,
                'error': 'Ma\'lumot yuborilmadi'
            })
        
        # Bugungi sana va vaqt
        now = timezone.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)
        
        # Ertaga soat 23:59:59 (deadline)
        tomorrow_end = timezone.make_aware(
            datetime.combine(tomorrow, datetime.max.time())
        )
        
        # Deadline o'tganligini tekshirish
        if now > tomorrow_end:
            return Response({
                'success': False,
                'error': 'Baholash muddati tugagan. Faqat bugun va ertaga baho qo\'yish mumkin'
            })
        
        data_map = {}
        student_ids = set()
        dates = set()
        
        for item in grade_list:
            date_str = item.get('date', '').split('T')[0]
            if date_obj := parse_date(date_str):
                # Faqat bugun va ertaga ruxsat
                if date_obj != today and date_obj != tomorrow:
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
                'error': f'Faqat bugun ({today.strftime("%d.%m.%Y")}) va ertaga ({tomorrow.strftime("%d.%m.%Y")}) baho qo\'yish mumkin'
            })
        
        # Mavjud baholarni olish
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
                # Mavjud bahoni yangilash
                obj = existing[key]
                obj.grade = data['grade']
                to_update.append(obj)
            else:
                # Yangi baho yaratish
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
        
        return Response({
            'success': True,
            'created': created,
            'updated': updated,
            'message': f'{created} ta yangi baho qo\'shildi, {updated} ta yangilandi'
        })
    
class RatingView(View):
    """Rating sahifasi - O'quvchilar reytingi"""
    def get(self, request, group_id):
        group = get_object_or_404(models.Group, id=group_id)
        return render(request, "reception/rating/rating.html", {
            "group": group,
            "active_tab": "rating"
        })


class GroupRatingAPIView(APIView):
    """
    Guruh talabalarining reytingi API
    GET: /manager/api/rating/<group_id>/?month=12&year=2025
    """
    def get(self, request, group_id):
        # Oy va yilni olish (1-12 formatida)
        month = int(request.query_params.get('month', timezone.now().month))
        year = int(request.query_params.get('year', timezone.now().year))
        
        print(f"📥 Kelgan so'rov: group_id={group_id}, month={month}, year={year}")
        
        # Oy boshi va oxirini hisoblash
        start_date = timezone.datetime(year, month, 1).date()
        
        # Oy oxirini topish
        last_day = calendar.monthrange(year, month)[1]
        end_date = timezone.datetime(year, month, last_day).date()
        
        print(f"📅 Rating davri: {start_date} dan {end_date} gacha")
        
        # Shu davrdagi barcha baholarni tekshirish
        all_grades = models.Grade.objects.filter(
            group_id=group_id,
            date_time__gte=start_date,
            date_time__lte=end_date
        )
        print(f"📊 Shu davrdagi jami baholar: {all_grades.count()}")
        
        # Guruhni tekshirish
        group = get_object_or_404(models.Group, id=group_id)
        
        # Talabalarni olish
        students = models.Student.objects.filter(group=group)
        
        rating_data = []
        
        for student in students:
            # Talabaning shu oydagi barcha baholari
            student_grades = models.Grade.objects.filter(
                student=student,
                group=group,
                date_time__gte=start_date,
                date_time__lte=end_date
            )
            
            # Baholar ro'yxati
            grades_list = list(student_grades.values_list('grade', flat=True))
            
            if grades_list:
                average = sum(grades_list) / len(grades_list)
                total_grades = len(grades_list)
            else:
                average = 0
                total_grades = 0
            
            # Telefon raqamini olish (agar mavjud bo'lsa)
            phone = getattr(student, 'phone', None) or getattr(student, 'phone_number', None)
            
            rating_data.append({
                'id': student.id,
                'name': student.full_name,
                'phone': phone,
                'average': round(average, 1),  # 1 kasr raqamgacha
                'total_grades': total_grades,
                'grades_list': grades_list
            })
        
        # O'rtacha baho bo'yicha tartiblash (yuqoridan pastga)
        # Agar baholar bir xil bo'lsa, baho soni bo'yicha
        rating_data.sort(
            key=lambda x: (x['average'], x['total_grades']), 
            reverse=True
        )
        
        # Rank (o'rin) qo'shish
        for rank, student in enumerate(rating_data, start=1):
            student['rank'] = rank
        
        print(f"✅ {len(rating_data)} ta talaba reytingi tayyor")
        
        return Response({
            'success': True,
            'month': month,
            'year': year,
            'period': f"{start_date} - {end_date}",
            'total_students': len(rating_data),
            'students': rating_data
        })

@login_required
@require_http_methods(["GET", "POST"])
def notification_others_view(request):
    """Others - Manager, Teacher, Reception uchun notification yuborish"""
    
    # POST - Notification yaratish
    if request.method == 'POST':
        print("=" * 50)  # DEBUG
        print("POST request keldi")  # DEBUG
        print(f"POST data: {request.POST}")  # DEBUG
        
        form = NotificationForm(request.POST, sender=request.user)
        
        if form.is_valid():
            try:
                notification = form.save()
                print(f"✅ Notification muvaffaqiyatli yaratildi: ID={notification.id}")  # DEBUG
                print(f"   Sender: {notification.sender.username}")  # DEBUG
                print(f"   Recipient: {notification.recipient.username}")  # DEBUG
                print(f"   Role: {notification.recipient_role}")  # DEBUG
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Xabar muvaffaqiyatli yuborildi!',
                    'notification_id': notification.id,
                    'recipient': notification.recipient.get_full_name() or notification.recipient.username,
                    'recipient_role': notification.recipient_role
                })
            except Exception as e:
                print(f"❌ Save error: {e}")  # DEBUG
                traceback.print_exc()
                return JsonResponse({
                    'success': False, 
                    'errors': {'save': [str(e)]}
                }, status=500)
        else:
            print(f"❌ Form validation failed")  # DEBUG
            print(f"Form errors: {form.errors}")  # DEBUG
            
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(e) for e in error_list]
            
            return JsonResponse({
                'success': False, 
                'errors': errors
            }, status=400)
    
    # GET - AJAX requests
    action = request.GET.get('action')
    
    # 1. Kurslarni olish
    if action == 'get_courses':
        try:
            courses = Course.objects.all().order_by('title')
            data = [{'id': c.id, 'name': c.title} for c in courses]
            print(f"✅ Courses yuklandi: {len(data)} ta")  # DEBUG
            return JsonResponse({'courses': data})
        except Exception as e:
            print(f"❌ Get courses error: {e}")  # DEBUG
            return JsonResponse({'error': str(e), 'courses': []}, status=500)
    
    # 2. Role bo'yicha userlarni olish
    if action == 'get_users':
        role = request.GET.get('role')
        course_id = request.GET.get('course_id')
        
        print(f"📥 get_users: role={role}, course_id={course_id}")  # DEBUG
        
        try:
            if role == 'teacher':
                if course_id:
                    # O'sha kursda ishlaydigan teacherlar
                    teachers = Teacher.objects.filter(
                        groups__course_id=course_id, 
                        status='Active'
                    ).distinct().order_by('full_name')
                    print(f"   Teacher query: course_id={course_id}")  # DEBUG
                else:
                    # Barcha active teacherlar
                    teachers = Teacher.objects.filter(status='Active').order_by('full_name')
                    print(f"   Teacher query: barcha active")  # DEBUG
                
                print(f"   Topilgan teacherlar: {teachers.count()} ta")  # DEBUG
                
                data = []
                for t in teachers:
                    data.append({
                        'id': t.id,  # Bu Teacher ID (User ID emas!)
                        'name': t.full_name,
                        'username': getattr(t, 'username', 'N/A')
                    })
                    print(f"     - {t.full_name} (ID: {t.id})")  # DEBUG
                
            elif role in ['manager', 'reception', 'accountant']:
                # Manager, Reception, Accountant uchun
                users = BaseUser.objects.filter(role=role).order_by('first_name', 'last_name')
                print(f"   User query: role={role}, count={users.count()}")  # DEBUG
                
                data = []
                for u in users:
                    data.append({
                        'id': u.id,  # Bu User ID
                        'name': u.get_full_name() or u.username,
                        'username': u.username
                    })
                    print(f"     - {u.username} (ID: {u.id})")  # DEBUG
            else:
                print(f"   ⚠️ Noma'lum role: {role}")  # DEBUG
                data = []
            
            print(f"✅ Users yuklandi: {len(data)} ta")  # DEBUG
            return JsonResponse({'users': data, 'count': len(data)})
            
        except Exception as e:
            print(f"❌ Get users error: {e}")  # DEBUG
            traceback.print_exc()
            return JsonResponse({'error': str(e), 'users': []}, status=500)
    
    # Oddiy GET - Form ko'rsatish
    form = NotificationForm()
    return render(request, 'reception/notifications/notification_others.html', {
        'form': form,
        'current_user': request.user
    })



@login_required
def notification_count_view(request):
    """O'qilmagan xabarlar sonini qaytarish"""
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({
        'unread_count': unread_count
    })


@login_required
def notification_list_api_view(request):
    """Notification list (JSON API)"""
    limit = int(request.GET.get('limit', 4))
    status = request.GET.get('status', 'all')  # all, unread, read
    
    # Base query
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'course').order_by('-created_at')
    
    # Filter by status
    if status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status == 'read':
        notifications = notifications.filter(is_read=True)
    
    total_count = notifications.count()
    notifications = notifications[:limit]
    
    # Serialize
    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'sender_name': notif.sender.get_full_name() or notif.sender.username,
            'message': notif.message,
            'message_type': notif.message_type,
            'message_type_display': notif.get_message_type_display() if notif.message_type else None,
            'course': notif.course.title if notif.course else None,
            'is_read': notif.is_read,
            'created_at': notif.created_at.isoformat(),
        })
    
    return JsonResponse({
        'notifications': data,
        'total_count': total_count,
        'limit': limit
    })


@login_required
def notification_detail_api_view(request, notification_id):
    """Notification detailini olish va mark as read"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )
    
    # Mark as read
    if not notification.is_read:
        notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'notification': {
            'id': notification.id,
            'sender_name': notification.sender.get_full_name() or notification.sender.username,
            'message': notification.message,
            'message_type': notification.message_type,
            'message_type_display': notification.get_message_type_display() if notification.message_type else None,
            'course': notification.course.title if notification.course else None,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
        }
    })


@login_required
def notification_inbox_view(request):
    """Full inbox page (barcha xabarlar)"""
    status_filter = request.GET.get('status', 'all')
    
    # Base query
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'course').order_by('-created_at')
    
    # Filter
    if status_filter == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status_filter == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Stats
    total_count = Notification.objects.filter(recipient=request.user).count()
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    read_count = Notification.objects.filter(recipient=request.user, is_read=True).count()
    
    context = {
        'notifications': notifications,
        'total_count': total_count,
        'unread_count': unread_count,
        'read_count': read_count,
        'status_filter': status_filter,
    }
    
    return render(request, 'reception/notifications/inbox.html', context)


@login_required
def notification_mark_all_read_view(request):
    """Barcha xabarlarni o'qilgan deb belgilash"""
    if request.method == 'POST':
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'message': f'{updated} ta xabar o\'qilgan deb belgilandi'
        })
    
    return JsonResponse({'success': False}, status=400)


@login_required
def notification_delete_view(request, notification_id):
    """Xabarni o'chirish"""
    if request.method == 'POST':
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        notification.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Xabar o\'chirildi'
        })
    
    return JsonResponse({'success': False}, status=400)

