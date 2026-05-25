from django.shortcuts import render , redirect, get_object_or_404
from django.views.generic import View
from helpers.permissions import AccountantPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from common import models
from django.utils import timezone
from manager import forms
import traceback
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from manager.forms import NotificationForm, InformationsForm ,TeacherSalaryForm
from django.contrib import messages
from django.views.generic import ListView , DeleteView, TemplateView, ListView, View
from common.models import Group,Course,Teacher,Student,Debt,BaseUser,Notification
from helpers.views import CreateView, UpdateView, DeleteView
from django.db.models import Q 
from django.http import JsonResponse
from helpers import permissions
from datetime import date ,datetime , timedelta
from django.db import transaction
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse 



class HomeView(TemplateView):
    template_name = "accountant/base/index.html"
    
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
        
        # TO'LOVLAR
        payments_count = models.Payment.objects.filter(
            date__gte=month_start,
            date__lt=month_end
        ).values('student').distinct().count()
        
        # QARZDORLAR
        debtors_count = models.Payment.objects.filter(debt__gt=0).values('student').distinct().count()

        # ============================================
        # CHART MA'LUMOTLARI
        # ============================================
        
        chart_year = int(self.request.GET.get('chart_year', year))
        
        # Payments - oylar bo'yicha
        payments_by_month = models.Payment.objects.filter(
            date__year=chart_year
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        # Wages - oylar bo'yicha
        wages_by_month = models.Wages.objects.filter(
            date__year=chart_year
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        # Teacher Salaries - oylar bo'yicha (YANGI)
        teacher_salaries_by_month = models.TeacherSalary.objects.filter(
            date__year=chart_year
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        # Oy nomlari
        month_names = {
            1: 'January',2: 'February',3: 'March',4: 'April',5: 'May',
            6: 'June',7: 'July',8: 'August',9: 'September',10: 'October',
            11: 'November',12: 'December'
        }
        
        # Har bir oy uchun ma'lumotlarni tayyorlash
        chart_data = []
        for month_num in range(1, 13):
            # Payment summasi
            payment_total = next(
                (item['total'] for item in payments_by_month 
                 if item['month'] and item['month'].month == month_num), 
                0
            )
            
            # Wages summasi
            wages_total = next(
                (item['total'] for item in wages_by_month 
                 if item['month'] and item['month'].month == month_num), 
                0
            )
            
            # Teacher Salaries summasi (YANGI)
            teacher_salary_total = next(
                (item['total'] for item in teacher_salaries_by_month 
                 if item['month'] and item['month'].month == month_num), 
                0
            )
            
            chart_data.append({
                'month': month_names[month_num],
                'payments': float(payment_total or 0),
                'wages': float(wages_total or 0),
                'teacher_salaries': float(teacher_salary_total or 0)  # YANGI
            })
        
        # Jami summa
        total_payments = sum(item['payments'] for item in chart_data)
        total_wages = sum(item['wages'] for item in chart_data)
        total_teacher_salaries = sum(item['teacher_salaries'] for item in chart_data)  # YANGI
        
        context.update({
            'selected_year': year,
            'selected_month': month,
            'month_name': month_names.get(month, ''),

            # Boshqalar
            'payments_count': payments_count,
            'debtors_count': debtors_count,
            
            # CHART MA'LUMOTLARI
            'chart_data': chart_data,
            'chart_year': chart_year,
            'total_payments': total_payments,
            'total_wages': total_wages,
            'total_teacher_salaries': total_teacher_salaries,  # YANGI
            'available_years': [year - i for i in range(5)],
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
            # List sahifasiga olib boradi va filter qo'shadi
            url = reverse('accountant:teacher-list') + f'?search={teacher.full_name}'
            
            results.append({
                'type': 'teacher',
                'name': teacher.full_name,
                'url': url,
                'label': 'Teacher'
            })
    except Exception as e:
        print(f"Teacher search error: {e}")
    
    # ============ STUDENTS QIDIRISH ============
    try:
        students = Student.objects.filter(full_name__icontains=query)[:5]
        
        for student in students:
            url = reverse('accountant:student-list') + f'?search={student.full_name}'
            
            results.append({
                'type': 'student',
                'name': student.full_name,
                'url': url,
                'label': 'Student'
            })
    except Exception as e:
        print(f"Student search error: {e}")
    
    # ============ GROUPS QIDIRISH ============
    try:
        groups = Group.objects.filter(title__icontains=query)[:5]
        
        for group in groups:
            url = reverse('accountant:group-list') + f'?search={group.title}'
            
            results.append({
                'type': 'group',
                'name': group.title,
                'url': url,
                'label': 'Group'
            })
    except Exception as e:
        print(f"Group search error: {e}")
    
    return JsonResponse({'results': results})


class Settings(ListView):
    template_name = "accountant/settings/list.html"
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
    
    return render(request, 'accountant/settings/list.html', context)

def group_debtors_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    debts = models.Payment.objects.filter(group=group, debt__gt=0)
    
    debt = []
    for p in debts:
        p.remaining_debt = p.group.price - p.amount
        p.phone = p.student.phone  
        debt.append(p)
    return render(request, 'accountant/debtors/list.html', {
        'group': group,
        'debts': debts,
    })



class TeacherListView(ListView):
    model = models.Teacher
    template_name = "accountant/teacher/list.html"
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
    template_name = "accountant/teacher/create.html"
    context_object_name = "object"
    success_url = "accountant:teacher-list"
    success_create_url = 'accountant:teacher-create'
    
    
class TeacherUpdateView(UpdateView):
    model = models.Teacher
    form_class = forms.TeacherForm
    template_name = "accountant/teacher/update.html"
    context_object_name = "object"
    success_url = "accountant:teacher-list"
    success_create_url = 'accountant:teacher-update'
    

class TeacherDeleteView(DeleteView):
    model = models.Teacher
    success_url = 'accountant:teacher-list'
    
   

class CourseListView(ListView):
    model = models.Course
    template_name = "accountant/course/list.html"
    context_object_name = "courses"
    def get_queryset(self):
        queryset = models.Course.objects.all().order_by("id")
        search = self.request.GET.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
            )
        return queryset



class GroupListView(ListView):
    model = models.Group
    template_name = "accountant/group/list.html"
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
    template_name = "accountant/group/create.html"
    context_object_name = 'object'
    form_class = forms.GroupForm
    success_url ="accountant:group-list"
    success_update_url ="accountant:group-update" 


class GroupUpdateView(UpdateView):
    model = models.Group
    template_name = "accountant/group/update.html"
    context_object_name = 'object'
    form_class = forms.GroupForm
    success_url ="accountant:group-list"
    success_update_url ="accountant:group-update"

class GroupDeleteView(DeleteView):
    model = models.Group
    success_url ="accountant:group-list"




    
class StudentListView(AccountantPassesTestMixin, ListView):
    model = models.Student
    template_name = "accountant/student/list.html"
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
    template_name = "accountant/student/create.html"
    context_object_name = "object"
    success_url = "accountant:student-list"
    success_create_url = 'accountant:student-create'
    
    
class StudentUpdateView(UpdateView):
    model = models.Student
    form_class = forms.StudentForm
    template_name = "accountant/student/update.html"
    context_object_name = "object"
    success_url ="accountant:student-list"
    success_create_url = 'accountant:student-update'
    

class StudentDeleteView(DeleteView):
    model = models.Student
    success_url ='accountant:student-list'


class PaymentListView(ListView):
    model = models.Payment
    template_name = "accountant/payment/list.html"
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
    template_name = "accountant/payment/create.html"
    success_url = "accountant:payment-list"

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
    template_name = "accountant/payment/create.html"
    success_url = "accountant:payment-list"

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
    template_name = "accountant/payment/delete.html"
    context_object_name = "object"
    success_url = "accountant:payment-list"

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
                "update_url": f"/accountant/payment/{p.id}/update",
                "delete_url": f"/accountant/payment/{p.id}/delete",
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
    return render(request, 'accountant/payment/list.html', context)


class WagesListView(ListView):
    model = models.Wages
    template_name = "accountant/Wages/list.html"
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
    template_name = "accountant/Wages/create.html"
    success_url = "accountant:wages-list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["roles"] = models.Employee.ROLE_CHOICES
        return context



class WagesUpdateView(UpdateView):
    model = models.Wages
    form_class = forms.WagesForm
    template_name = "accountant/Wages/update.html"
    success_url = "accountant:wages-list"



class WagesDeleteView(DeleteView):
    model = models.Wages
    success_url = "accountant:wages-list"


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
            "update_url": f"/accountant/wages/{w.id}/update",
            "delete_url": f"/accountant/wages/{w.id}/delete",
        } for w in objects]

        return JsonResponse({'wages': data, 'total': len(data)})

    paginator = Paginator(objects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    role_choices = models.Employee.ROLE_CHOICES

    return render(request, 'accountant/Wages/list.html', {
        'objects': page_obj,
        'role_choices': role_choices,
    })



class TeacherSalaryListView(ListView):
    model = models.TeacherSalary
    template_name = "accountant/salary/list.html"
    context_object_name = "objects"
    paginate_by = 20  # Pagination qo'shish

    def get_queryset(self):
        qs = super().get_queryset().select_related('teacher', 'course', 'group')
        
        # Oy va yil filterlari
        year = int(self.request.GET.get("year", date.today().year))
        month = int(self.request.GET.get("month", date.today().month))
        
        qs = qs.filter(date__year=year, date__month=month)
        
        # Search filter (agar mavjud bo'lsa)
        search = self.request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(teacher__full_name__icontains=search) |
                Q(course__title__icontains=search) |
                Q(group__name__icontains=search)
            )
        
        return qs.order_by('-date', '-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Tanlangan oy va yilni contextga qo'shish
        context['selected_month'] = int(self.request.GET.get("month", date.today().month))
        context['selected_year'] = int(self.request.GET.get("year", date.today().year))
        
        return context

class TeacherSalaryCreateView(View):
    template_name = "accountant/salary/create.html"

    def get(self, request):
        courses = Course.objects.all()
        today = timezone.now().date().strftime('%Y-%m-%d')

        return render(request, self.template_name, {
            "courses": courses,
            "today": today
        })

    def post(self, request):
        # Manual validation
        course_id = request.POST.get("course")
        teacher_id = request.POST.get("teacher")
        group_id = request.POST.get("group") or None
        amount = request.POST.get("amount")
        payment_type = request.POST.get("type")
        payment_date = request.POST.get("date")

        try:
            models.TeacherSalary.objects.create(
                course_id=course_id,
                teacher_id=teacher_id,
                group_id=group_id,
                amount=amount,
                type=payment_type,
                date=payment_date
            )
            return redirect("accountant:tsalary-list")
        except Exception as e:
            courses = Course.objects.all()
            return render(request, self.template_name, {
                "courses": courses,
                "today": timezone.now().date().strftime('%Y-%m-%d'),
                "error": str(e)
            })


class TeacherSalaryUpdateView(UpdateView):
    model = models.TeacherSalary
    form_class = TeacherSalaryForm
    template_name = "accountant/salary/update.html"
    success_url = "accountant:tsalary-list"


class TeacherSalaryDeleteView(DeleteView):
    model = models.TeacherSalary
    template_name = "accountant/salary/delete.html"
    success_url = "accountant:tsalary-list"


# ==================== AJAX ENDPOINTS ====================

@require_GET
def get_teachers_by_course(request):
    course_id = request.GET.get("course_id")
    
    if not course_id:
        return JsonResponse([], safe=False)
    
    try:
        teachers = Teacher.objects.filter(course_id=course_id).values(
            "id", "full_name", "type"
        )
        return JsonResponse(list(teachers), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_GET
def get_teacher_info(request):
    teacher_id = request.GET.get("teacher_id")
    
    if not teacher_id:
        return JsonResponse({"error": "teacher_id required"}, status=400)
    
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        
        # Salary ni string ga aylantirish va % olib tashlash
        salary_str = str(teacher.salary)
        salary_clean = salary_str.replace('%', '').strip()
        
        # Float ga aylantirish
        try:
            salary_float = float(salary_clean)
        except (ValueError, TypeError):
            salary_float = 0
        
        return JsonResponse({
            "type": teacher.type,
            "salary": salary_float,
            "has_groups": Group.objects.filter(teacher=teacher).exists()
        })
        
    except Teacher.DoesNotExist:
        return JsonResponse({"error": "Teacher not found"}, status=404)
    except Exception as e:
        import traceback
        print(f"ERROR in get_teacher_info: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)

@require_GET
def get_teacher_groups(request):
    teacher_id = request.GET.get("teacher_id")
    
    if not teacher_id:
        return JsonResponse([], safe=False)
    
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        groups = Group.objects.filter(teacher=teacher)
        
        data = []
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        for g in groups:
            # Shu oy uchun bu group bo'yicha to'langan yoki yo'qligi
            already_paid = models.TeacherSalary.objects.filter(
                teacher=teacher, 
                group=g,
                date__month=current_month,
                date__year=current_year
            ).exists()
            
            # Teacher salary ni tozalash
            salary_str = str(teacher.salary)
            salary_clean = salary_str.replace('%', '').strip()
            
            try:
                teacher_salary = float(salary_clean)
            except (ValueError, TypeError):
                teacher_salary = 0
            
            # Hisoblash logikasi
            monthly_salary = 0
            
            if teacher.type == "Group by":
                # Group by: Fixed salary
                monthly_salary = teacher_salary
                
            elif teacher.type == "Precent":
                # Precent: Students * Price * Percentage
                students_count = g.students.count()
                
                try:
                    group_price = float(str(g.price).replace(',', ''))
                except (ValueError, TypeError):
                    group_price = 0
                
                total_income = students_count * group_price
                monthly_salary = (total_income * teacher_salary) / 100
                
            elif teacher.type == "Fixed":
                # Fixed: Teacher salary
                monthly_salary = teacher_salary
            
            # Group name field (title yoki name)
            group_name = g.title if hasattr(g, 'title') else (g.name if hasattr(g, 'name') else f"Group {g.id}")
            
            data.append({
                "id": g.id,
                "name": group_name,  # ✅ "name" ishlatamiz (HTML da kutilmoqda)
                "students": g.students.count(),
                "price": float(str(g.price).replace(',', '')) if g.price else 0,
                "monthly_salary": float(monthly_salary),  # ✅ Float ga aylantirish
                "type": teacher.type,
                "percentage": float(teacher_salary) if teacher.type == "Precent" else 0,
                "disabled": already_paid
            })
        
        print(f"DEBUG: Sending {len(data)} groups for teacher {teacher_id}")  # Debug
        print(f"DEBUG: Data = {data}")  # Debug
        
        return JsonResponse(data, safe=False)
        
    except Teacher.DoesNotExist:
        return JsonResponse({"error": "Teacher not found"}, status=404)
    except Exception as e:
        import traceback
        print(f"ERROR in get_teacher_groups: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)

#--------------------------------------------------------------------------------------------------------------#

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
    return render(request, 'accountant/notifications/notification_others.html', {
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
    
    return render(request, 'accountant/notifications/inbox.html', context)


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

