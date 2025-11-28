from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from helpers.models import BaseModel
from django.db.models import CASCADE
from datetime import date 
from datetime import timedelta
from django.utils import timezone



class BaseUser(AbstractUser):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('teacher', 'Teacher'),
        ('reception', 'Reception'),
        ('accountant', 'Accountant'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Teacher(BaseModel):
    status_choices = [
        ("Active", "Active"),
        ("Archive", "Archive")
    ]
    type_choice = [
        ("Precent", "Precent"),
        ("Group by", "Group by")
    ]
    
    full_name = models.CharField(_("full name"), max_length=256)
    birth_date = models.DateField(_("birth date"))
    course = models.ForeignKey("common.Course", on_delete=models.SET_NULL, verbose_name="course", related_name="teachers", null=True, blank=False)
    phone = models.CharField(_("phone"), max_length=256)
    type = models.CharField(_("type"), max_length=100, choices=type_choice)
    salary = models.CharField(_("salary"), max_length=100, help_text="Foiz: '20%' yoki Fix summa: '500000'")
    address = models.CharField(_("address"), max_length=256)
    status = models.CharField(_("status"), max_length=256, choices=status_choices)

    class Meta:
        db_table = "teachers"
        verbose_name = _("teacher")
        verbose_name_plural = _("teachers")

    def __str__(self):
        return self.full_name
    
    def get_salary_percent(self):
        """Foiz miqdorini olish"""
        if self.type == "Precent" and '%' in str(self.salary):
            try:
                return float(str(self.salary).replace('%', '').strip())
            except:
                return 0
        return 0
    
    def get_fixed_salary(self):
        """Fix summa olish (Group by uchun)"""
        if self.type == "Group by":
            try:
                return float(str(self.salary).replace(',', '').replace(' ', '').strip())
            except:
                return 0
        return 0
    
    def calculate_monthly_salary(self, group):
        """
        Oylik maoshni hisoblash
        
        Args:
            group: Group obyekti
        
        Returns:
            dict: Hisoblangan oylik va detallari
        """
        result = {
            'monthly_salary': 0,
            'type': self.type,
            'salary': self.salary,
            'details': {}
        }
        
        if self.type == "Group by":
            # Fix summa
            result['monthly_salary'] = self.get_fixed_salary()
            result['details'] = {
                'description': f"Fixed salary for group: {self.salary}"
            }
        
        elif self.type == "Precent":
            # O'quvchilar soni (group.students ga qarab)
            students_count = group.students.filter().count()
            group_price = group.price
            percent = self.get_salary_percent()
            
            # Jami to'lov: students_count × group_price
            total_payment = students_count * group_price
            
            # Teacher foizi
            monthly_salary = (total_payment * percent) / 100
            
            result['monthly_salary'] = monthly_salary
            result['details'] = {
                'students_count': students_count,
                'group_price': group_price,
                'total_payment': total_payment,
                'percent': percent,
                'calculation': f"{students_count} students × {group_price:,} so'm = {total_payment:,} so'm × {percent}% = {monthly_salary:,} so'm"
            }
        
        return result
        return self.full_name

class Course(BaseModel):
    title = models.CharField(_("title"), max_length=256)
    description = models.TextField(_("description"), null=True, blank=True)
    duration = models.CharField(_("duration"), max_length=256)

    class Meta:
        db_table = "courses"
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        return self.title

class Group(BaseModel):
    day_choices = [
        ("mo we fri", "Mon Wed Fri"),
        ("tu thu sa", "Tu Thu Sat"),
    ]
    status_choices = [
        ("Active", "Active"),
        ("Finished", "Finished"),
    ]
    
    title = models.CharField(_("title"), max_length=256)
    course = models.ForeignKey("common.Course", on_delete=models.SET_NULL, verbose_name="course", related_name="groups", null=True, blank=False)
    price = models.IntegerField(_("price"))
    room = models.ForeignKey("common.Classroom", on_delete=models.SET_NULL, null=True, blank=False)
    teacher = models.ForeignKey("common.Teacher", on_delete=models.SET_NULL, verbose_name="teacher", related_name="groups", null=True, blank=False)
    lesson_days = models.CharField(_("lesson days"), max_length=256, choices=day_choices)
    start_time = models.TimeField(_("start_time"))
    end_time = models.TimeField(_("end_time"))
    date_started = models.DateField("date")
    status = models.CharField(_("status"), max_length=256, choices=status_choices, default="Active") 

    class Meta:
        db_table = "groups"
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __str__(self):
        return self.title
    
    def get_active_students_count(self):
        """Faol o'quvchilar soni"""
        return self.students.filter(status="Active").count()
    
    def get_total_payment(self):
        """Umumiy to'lovlar (faol o'quvchilar × price)"""
        return self.get_active_students_count() * self.price
    
    def get_teacher_monthly_salary(self):
        """Teacher oyligini hisoblash"""
        if self.teacher:
            return self.teacher.calculate_monthly_salary(self)
        return {
            'monthly_salary': 0,
            'type': None,
            'salary': None,
            'details': {'error': 'No teacher assigned'}
        }


class Student(BaseModel):
    status_choices = [
        (_("Active"), _("Active")),
        (_("Archive"), _("Archive")),

    ]
    full_name = models.CharField(_("full name"), max_length=256)
    group = models.ForeignKey("common.Group", on_delete=models.CASCADE, verbose_name="group", related_name="students")
    birth_date = models.DateField(_("birth date"))
    phone = models.CharField(_("phone"), max_length=256)
    address = models.CharField(_("address"), max_length=256)
    balance = models.IntegerField(_("balance"))
    date_joined = models.DateField(_("joined"), null=True, blank=True,  default=date.today)
    status = models.CharField(_("status"), max_length=256, choices=status_choices)

    class Meta:
        db_table = "students"
        verbose_name = _("student")
        verbose_name_plural = _("students")

    def __str__(self):
        return self.full_name


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances", null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="attendances", null=True, blank=True)
    date_time = models.DateField()
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "date_time") 
        ordering = ["-date_time"]

    def __str__(self):
        return f"{self.student.full_name} - {self.date_time} - {'Bor' if self.is_present else 'Yo‘q'}"

class Lead(BaseModel):
    status_choices = [
        (_("Request"), _("Request")),
        (_("Trial"), _("Trial")),
        (_("In group"), _("In group")),
    ]
    full_name = models.CharField(_("full name"), max_length=256)
    birth_date = models.DateField(_("birth date"))
    phone = models.CharField(_("phone"), max_length=256)
    address = models.CharField(_("address"), max_length=256)
    interested_course = models.ForeignKey("common.Course", on_delete=models.SET_NULL, verbose_name="interested course", related_name="leads", null=True) 
    status = models.CharField(_("status"), max_length=256, choices=status_choices)

    class Meta:
        db_table = "leads"
        verbose_name = _("lead")
        verbose_name_plural = _("leads")

    def __str__(self):
        return self.full_name



class Payment(models.Model):
    student = models.ForeignKey("Student",on_delete=models.CASCADE,related_name='payments')
    group = models.ForeignKey("Group",on_delete=models.CASCADE,related_name='payments',null=True,blank=True)
    amount = models.PositiveIntegerField(_("amount"))
    date = models.DateField(_("date"), default=date.today)
    debt = models.PositiveIntegerField(_("debt"), default=0)

    class Meta:
        db_table = "payment"
        verbose_name = "payment"
        verbose_name_plural = "payments"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        student = self.student
        group_fee = self.group.price if self.group else 0

        if is_new:
            # Amount avtomatik to'lovga teng bo'lishi mumkin
            if not self.amount:
                self.amount = group_fee

            # Agar to'lov yetarli bo'lmasa, debt hisoblash
            if self.amount < group_fee:
                self.debt = group_fee - self.amount
            else:
                self.debt = 0

            # Student balance kamayadi (faqat to'langan miqdor)
            student.balance -= self.amount

        else:
            # Payment update qilinsa
            old = Payment.objects.get(pk=self.pk)
            diff = self.amount - old.amount
            student.balance -= diff

        student.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Payment o‘chirilsa balansni qaytarish
        student = self.student
        student.balance += self.amount
        if hasattr(student, 'debt'):
            student.debt += self.amount
        student.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.student}"

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_time = models.DateField()
    grade = models.PositiveSmallIntegerField(default=0)

class Classroom(models.Model):
    name = models.CharField(_("name"), max_length=100)
    capacity = models.CharField(_("capacity"), max_length=100)
    
    def __str__(self):
        return self.name
    

class Employee(BaseModel):
    ROLE_CHOICES = [
        ('Administrator', 'Administrator'),
        ('Accountant', 'Accountant'),
        ('Support', 'Support'),
        ('Receptionist', 'Receptionist'),
    ]
    full_name = models.CharField(_("full name"), max_length=256)
    birth_date = models.DateField(_("birth date"), null=True, blank=True)
    phone = models.CharField(_("phone"), max_length=256)
    date_joined = models.DateField(_("joined"), null=True, blank=True,  default=date.today)
    salary = models.PositiveIntegerField(_("Monthly Salary"))
    role = models.CharField(_("status"), max_length=256, choices=ROLE_CHOICES)

    class Meta:
        db_table = "Employee"
        verbose_name = _("Employee")
        verbose_name_plural = _("Employee")

    def __str__(self):
        return self.full_name
    
class Wages(models.Model):
    ROLE_CHOICES = Employee.ROLE_CHOICES 
    status_method =[
        ('Bank Card', 'Bank Card'),
        ('Cash', 'Cash'),
    ]
    role = models.CharField(max_length=256, choices=ROLE_CHOICES)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(_("status"), max_length=100, choices=status_method)
    amount = models.PositiveIntegerField()
    date = models.DateField(_("date"), default=date.today)

    def __str__(self):
        return f"{self.employee.full_name} - {self.amount}"
    

class Debt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    phone = models.CharField(_("phone"), max_length=256)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student.name} - {self.amount}"