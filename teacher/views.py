from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from common.mixins import RoleRequiredMixin
from common import models , serializers
from django.db.models import Q 
from django.views.generic import TemplateView, ListView, DetailView
from common.models import Group , Student , Teacher , Attendance , TeacherSalary
from common import mixins
from django.db.models import Sum
from calendar import monthrange
from datetime import date ,datetime , timedelta
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from django.utils.dateparse import parse_date
from common.serializers import AttendanceSerializer , StudentSerializer 
from django.utils import timezone
import calendar
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from common.models import Notification
from rest_framework.response import Response


class TeacherHomeView(mixins.RoleRequiredMixin, TemplateView):
    template_name = "teacher/base/index.html"
    allowed_roles = ['teacher']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User orqali Teacher instancesini olish
        teacher = get_object_or_404(Teacher, user=self.request.user)
        context['teacher'] = teacher
        
        # Hozirgi sana
        today = timezone.now().date()
        
        # Oylik daromad uchun year va month (GET parametrlardan olish)
        selected_year = int(self.request.GET.get('year', today.year))
        selected_month = int(self.request.GET.get('month', today.month))
        
        context['selected_year'] = selected_year
        context['selected_month'] = selected_month
        
        # Teacher'ning barcha guruhlarini olish
        groups = Group.objects.filter(teacher=teacher)
        context['groups_count'] = groups.count()
        
        # Barcha o'quvchilar sonini hisoblash
        total_students = 0
        total_monthly_salary = 0

        # Har bir guruh bo'yicha hisoblash
        for group in groups:
            students_count = group.students.count()
            total_students += students_count
            
            # Maoshni hisoblash
            salary_info = teacher.calculate_monthly_salary(group)
            total_monthly_salary += salary_info['monthly_salary']
        
        context['students_count'] = total_students
        context['monthly_salary'] = total_monthly_salary
        
        # Agar Percent tipida bo'lsa, umumiy hisob
        if teacher.type == "Precent":
            percent = teacher.get_salary_percent()
            group_price = groups.first().price if groups.exists() else 0
            total_income = total_students * group_price
            context['total_income'] = total_income
            context['salary_percent'] = percent
            context['calculation'] = f"{total_students} students × {group_price:,} som = {total_income:,} som × {percent}% = {total_monthly_salary:,} som"
        else:
            context['total_income'] = 0
            context['calculation'] = f"Fixed salary: {teacher.salary}"
        
        # ===== Oylik daromad (TANLANGAN OY BO'YICHA) =====
        monthly_income = self.get_monthly_income(teacher, selected_year, selected_month)
        context['monthly_income'] = monthly_income
        
        return context
    
    def get_monthly_income(self, teacher, year, month):
        """Oylik daromadni hisoblash"""
        # Tanlangan oydagi barcha to'lovlarni yig'ish
        monthly_salaries = TeacherSalary.objects.filter(
            teacher=teacher,
            date__year=year,
            date__month=month
        ).aggregate(total=Sum('amount'))
        
        return monthly_salaries['total'] or 0
    

    
class GroupListView(RoleRequiredMixin, ListView):
    """Teacher faqat o'z grouplarini ko'radi"""
    model = models.Group
    template_name = "teacher/group/list.html"
    context_object_name = "objects"
    paginate_by = 10
    allowed_roles = ['teacher']
    
    def get_queryset(self):
        # FAQAT SHU TEACHERNING GROUPLARI
        teacher = models.Teacher.objects.get(user=self.request.user)
        queryset = models.Group.objects.filter(
            teacher=teacher,
            status="Active"
        ).select_related('course', 'room', 'teacher').order_by("id")
        
        # Search
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(Q(title__icontains=search))
        
        # Filter by lesson days
        day = self.request.GET.get('day')
        if day == 'odd':
            queryset = queryset.filter(lesson_days='mo we fri')
        elif day == 'even':
            queryset = queryset.filter(lesson_days='tu thu sa')
        
        # Filter by course
        course_id = self.request.GET.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = models.Course.objects.all()
        context['search'] = self.request.GET.get("search", "")
        context['day'] = self.request.GET.get('day', "")
        context['course_id'] = self.request.GET.get('course', "")
        return context


class GroupDetailView(RoleRequiredMixin, DetailView):
    """Group detallari - faqat o'z groupi uchun"""
    model = models.Group
    template_name = "teacher/group/detail.html"
    context_object_name = "object"
    allowed_roles = ['teacher']
    
    def get_queryset(self):
        # Faqat o'z grouplari
        teacher = models.Teacher.objects.get(user=self.request.user)
        return models.Group.objects.filter(teacher=teacher)


class StudentListView(RoleRequiredMixin, ListView):
    """Teacher faqat o'z grouplaridagi studentlarni ko'radi"""
    model = models.Student
    template_name = "teacher/student/list.html"
    context_object_name = "objects"
    paginate_by = 10
    allowed_roles = ['teacher']

    def get_queryset(self):
        # FAQAT SHU TEACHERNING GROUPLARIDAGI STUDENTLAR
        teacher = models.Teacher.objects.get(user=self.request.user)
        queryset = models.Student.objects.filter(
            group__teacher=teacher,
            status="Active"
        ).select_related('group').order_by("id")
        
        # Search
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(full_name__icontains=search)

        # Group filter (faqat teacher ning grouplari)
        group_id = self.request.GET.get("group")
        if group_id:
            queryset = queryset.filter(group_id=group_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # FAQAT SHU TEACHERNING GROUPLARI dropdown uchun
        teacher = models.Teacher.objects.get(user=self.request.user)
        context['groups'] = models.Group.objects.filter(
            teacher=teacher, 
            status="Active"
        )
        context['search'] = self.request.GET.get("search", "")
        context['group_id'] = self.request.GET.get("group", "")
        return context


class StudentDetailView(RoleRequiredMixin, DetailView):
    """Student detallari - faqat o'z groupidagi studentlar"""
    model = models.Student
    template_name = "teacher/student/detail.html"
    context_object_name = "object"
    allowed_roles = ['teacher']
    
    def get_queryset(self):
        # Faqat o'z grouplaridagi studentlar
        teacher = models.Teacher.objects.get(user=self.request.user)
        return models.Student.objects.filter(group__teacher=teacher)
    

class Settings(ListView):
    template_name = "teacher/settings/list.html"
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
    
    return render(request, 'teacher/settings/list.html', context)

def group_debtors_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    debts = models.Payment.objects.filter(group=group, debt__gt=0)
    
    debt = []
    for p in debts:
        p.remaining_debt = p.group.price - p.amount
        p.phone = p.student.phone  
        debt.append(p)
    return render(request, 'teacher/debtors/list.html', {
        'group': group,
        'debts': debts,
    })


class GradesView(View):
    def get(self, request, group_id):
        group = get_object_or_404(models.Group, id=group_id)
        return render(request, "teacher/grade/grade.html", {"group": group})


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
    
    
class AttendanceView(View):
    """Davomat sahifasini ko'rsatish"""
    def get(self, request, group_id):
        group = get_object_or_404(models.Group, id=group_id)
        return render(request, "teacher/attendance/attendance.html", {
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


class RatingView(View):
    """Rating sahifasi - O'quvchilar reytingi"""
    def get(self, request, group_id):
        group = get_object_or_404(models.Group, id=group_id)
        return render(request, "teacher/rating/rating.html", {
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
    
    return render(request, 'teacher/notifications/inbox.html', context)


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

