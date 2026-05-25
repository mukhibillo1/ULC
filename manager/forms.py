from django import forms
from helpers import widgets as widget
from common import models
from common.models import Student,Employee ,Teacher , BaseUser
from django.forms import DateInput
from django.utils import timezone
from django.conf import settings
from datetime import date
from django.apps import apps
from django.contrib.auth.forms import UserCreationForm

class UserForm(UserCreationForm):
    class Meta:
        model = models.BaseUser
        fields = ['username', 'email', 'role', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'role': forms.Select(attrs={'class': 'form-control', 'id': 'kt_select2_1'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            "phone" : forms.TelInput(attrs={"class" : "form-control", "placeholder" : "Phone"}),
            "role" : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_2"}),
            "teacher_profile" : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_3"}),
            "password1" : forms.PasswordInput(attrs={"class" : "form-control","id" : "kt_select2_3", "placeholder" : "Please write a password"}),
            "password2" : forms.PasswordInput(attrs={"class" : "form-control","id" : "kt_select2_3" ,"placeholder" : "Please write a password retry"}),

        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        if commit:
            user.save()
        return user


class TeacherForm(forms.ModelForm):
    class Meta:
        model = models.Teacher
        fields = [
            "user",
            "full_name",
            "birth_date",
            "phone",
            "course",
            "type",
            "salary",
            "address",
            "status",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control",}),
            "full_name" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Full name"}),
            "birth_date" : widget.DateWidget(attrs={"class" : "form-control", "id": "kt_datetimepicker_3"}),
            "phone" : forms.TelInput(attrs={"class" : "form-control", "placeholder" : "Phone"}),
            "course" : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"}),
            "type" : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_2"}),
            "salary" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Price"}),
            "address" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Address"}),
            "status" : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"}),

            }

class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = [
            "title",
            "duration",
            "price",
            "description",
        ]
        widgets = {
            "title" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Title"}),
            "duration" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Duration"}),
            "price" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Price"}),
            "description" : forms.Textarea(attrs={"class" : "form-control", "placeholder": "description"})
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = [
            "title",
            "course",
            "room",
            "teacher",
            'start_time',
            'end_time',
            "price",
            "lesson_days",
            'date_started',
            'status'

        ]
        widgets = {
            "title" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Title"}),
            "course" : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"}),
            "teacher" : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"}),
            "room" : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"}),
            "start_time" : forms.TimeInput(attrs={"class" : "form-control", "placeholder" : "Time"}),
            "end_time" : forms.TimeInput(attrs={"class" : "form-control", "placeholder" : "Time"}),
            "lesson_days" : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_2"}),
            "date_started" : widget.DateWidget(attrs={"class" : "form-control", "id": "kt_datetimepicker_3"}),
            "status" : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"}),
            "price" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Price"}),

        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = [
            "full_name",
            "birth_date",
            "group",
            "phone",
            "address",
            "group",
            "balance",
            "date_joined",
            "status",
        ]
        widgets = {
            "full_name" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Full name"}),
            "birth_date" : widget.DateWidget(attrs={"class" : "form-control", "id": "kt_datetimepicker_3"}),
            "group": forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_2"}), 
            "phone" : forms.TelInput(attrs={"class" : "form-control", "placeholder" : "Phone"}),
            "address" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Address"}),
            "group" : forms.Select(attrs={"class" : "form-control", "placeholder" : "group", "id": "kt_select2_2"}),
            "balance" : forms.TextInput(attrs={"class" : "form-control", "placeholder": "balance"}),
            "date_joined": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "status" : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"}),
            "date_joined" : widget.DateWidget(attrs={"class" : "form-control", "id": "kt_datetimepicker_2"}),
            
        }



class PaymentForm(forms.ModelForm):
    class Meta:
        model = models.Payment
        fields = ['group', 'student', 'amount', 'date']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control selectpicker','data-live-search': 'true','id': 'id_group'}),
            'student': forms.Select(attrs={'class': 'form-control selectpicker','data-live-search': 'true','id': 'id_student'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Enter amount'}),
            'date': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Boshlang'ichda student queryset bo‘sh bo‘lsin
        self.fields['student'].queryset = Student.objects.none()

        # POST so‘rov bo‘lsa yoki update
        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                self.fields['student'].queryset = Student.objects.filter(group_id=group_id)
            except (ValueError, TypeError):
                self.fields['student'].queryset = Student.objects.none()
        elif self.instance and self.instance.pk:
            self.fields['student'].queryset = Student.objects.filter(group=self.instance.group)

class LeadForm(forms.ModelForm):
    class Meta:
        model = models.Lead
        fields = [
            "full_name",
            "birth_date",
            "phone",
            "interested_course",
            "address",
            "date_joined",
            "status",
        ]
        widgets = {
            "full_name" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Full name"}),
            "birth_date" : widget.DateWidget(attrs={"class" : "form-control", "id": "kt_datetimepicker_3"}),
            "interested_course" : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_2"}),
            "phone" : forms.TelInput(attrs={"class" : "form-control", "placeholder" : "Phone"}),
            "address" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Address"}),
            "date_joined": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "status" : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"})
        }

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = models.Classroom
        fields = ['name', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = models.Employee
        fields = ['full_name', 'birth_date', 'phone', 'date_joined', 'salary', 'role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form selectpicker',"id": "kt_select2_2"}),
            "full_name" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Full name"}),
            "salary" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Price"}),
            "phone" : forms.TelInput(attrs={"class" : "form-control", "placeholder" : "Phone"}),
            "birth_date" : widget.DateWidget(attrs={"class" : "form-control", "id": "kt_datetimepicker_3"}),
            "date_joined" : widget.DateWidget(attrs={"class" : "form-control", "id": "kt_datetimepicker_2"}),
        }

class WagesForm(forms.ModelForm):
    class Meta:
        model = models.Wages
        fields = ['role', 'employee', 'amount', 'method', 'date']

        widgets = {
            'role': forms.Select(attrs={'class': 'form-control', 'id': 'id_role'}),
            'employee': forms.Select(attrs={'class': 'form-control', 'id': 'id_employee'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount...',
                'min': 0
            }),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['date'].initial = date.today()


        self.fields['employee'].queryset = Employee.objects.none()
        self.fields['employee'].widget.attrs['disabled'] = True


        if 'role' in self.data:
            role_value = self.data.get('role')
            if role_value:
                self.fields['employee'].queryset = Employee.objects.filter(role=role_value)
                self.fields['employee'].widget.attrs.pop('disabled', None)

        elif self.instance.pk:
            role_value = self.instance.role
            self.fields['employee'].queryset = Employee.objects.filter(role=role_value)
            self.fields['employee'].widget.attrs.pop('disabled', None)


class TeacherSalaryForm(forms.ModelForm):
    class Meta:
        model = models.TeacherSalary
        fields = ['course', 'teacher', 'group', 'amount', 'type', 'date']
        widgets = {
            "course" : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"}),
            'teacher' : forms.Select(attrs={"class" : "form-control", "placeholder" : "Teachers"}),
            'amount': forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Summa kiriting','step': '0.01','min': '0'}),
            'group' : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_2"}),
            'type' : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_2"}),
            'date': forms.DateInput(attrs={'class': 'form-control','type': 'date',})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Barcha fieldlarni ixtiyoriy qilamiz (AJAX orqali to'ldiriladi)
        self.fields['teacher'].required = False
        self.fields['group'].required = False


class NotificationForm(forms.ModelForm):
    # recipient'ni IntegerField qilamiz (ModelChoiceField emas!)
    recipient = forms.IntegerField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'person', 'required': True}),
        label='Qabul qiluvchi'
    )
    
    class Meta:
        model = models.Notification
        fields = ['recipient_role', 'course', 'message_type', 'message']
        widgets = {
            'recipient_role': forms.Select(attrs={'class': 'form-control', 'id': 'role', 'required': True}),
            'course': forms.Select(attrs={'class': 'form-control', 'id': 'course'}),
            'message_type': forms.Select(attrs={'class': 'form-control', 'id': 'messageType'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'id': 'message', 'rows': 5, 'placeholder': 'Xabar matni...', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        
        # Course va message_type optional
        self.fields['course'].required = False
        self.fields['course'].queryset = models.Course.objects.all()
        self.fields['message_type'].required = False
        
        # recipient fieldi IntegerField, shuning uchun queryset kerak emas
    
    def clean_recipient(self):
        """recipient fieldini alohida clean qilamiz"""
        recipient_id = self.cleaned_data.get('recipient')
        
        print(f"DEBUG clean_recipient - ID: {recipient_id}, type: {type(recipient_id)}")
        
        if not recipient_id:
            raise forms.ValidationError("Qabul qiluvchini tanlang!")
        
        return recipient_id
    
    def clean(self):
        cleaned_data = super().clean()
        recipient_role = cleaned_data.get('recipient_role')
        course = cleaned_data.get('course')
        message_type = cleaned_data.get('message_type')
        recipient_id = cleaned_data.get('recipient')
        
        print(f"DEBUG clean() - Role: {recipient_role}, Recipient ID: {recipient_id}")
        
        # Validation
        if recipient_role == 'teacher':
            if not course:
                raise forms.ValidationError("Teacher uchun kurs tanlash majburiy!")
            if not message_type:
                raise forms.ValidationError("Teacher uchun xabar turi tanlash majburiy!")
        
        if not recipient_id:
            raise forms.ValidationError("Qabul qiluvchini tanlang!")
        
        # Recipient User objectini topish
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            if recipient_role == 'teacher':
                # Teacher modelidan topamiz
                from common.models import Teacher
                teacher = Teacher.objects.get(id=recipient_id)
                print(f"DEBUG - Teacher topildi: {teacher.full_name}")
                
                # Teacher'ning user accountini topish
                user = None
                
                # Variant 1: teacher.user
                if hasattr(teacher, 'user') and teacher.user:
                    user = teacher.user
                    print(f"DEBUG - User (teacher.user): {user.username}")
                
                # Variant 2: username
                if not user and hasattr(teacher, 'username'):
                    user = User.objects.filter(username=teacher.username).first()
                    if user:
                        print(f"DEBUG - User (username): {user.username}")
                
                # Variant 3: email
                if not user and hasattr(teacher, 'email'):
                    user = User.objects.filter(email=teacher.email).first()
                    if user:
                        print(f"DEBUG - User (email): {user.username}")
                
                if not user:
                    raise forms.ValidationError(
                        f"Teacher '{teacher.full_name}' uchun user account topilmadi! "
                        f"Teacher ID: {teacher.id}"
                    )
                
                cleaned_data['recipient_user'] = user
                
            else:
                # Manager, Reception, Accountant uchun
                user = User.objects.get(id=recipient_id, role=recipient_role)
                print(f"DEBUG - User topildi ({recipient_role}): {user.username}")
                cleaned_data['recipient_user'] = user
                
        except Teacher.DoesNotExist:
            raise forms.ValidationError(f"ID {recipient_id} bilan teacher topilmadi!")
        except User.DoesNotExist:
            raise forms.ValidationError(
                f"ID {recipient_id} bilan {recipient_role} role'dagi user topilmadi!"
            )
        except Exception as e:
            print(f"ERROR in clean: {e}")
            import traceback
            traceback.print_exc()
            raise forms.ValidationError(f"Xatolik: {str(e)}")
        
        return cleaned_data
    
    def save(self, commit=True):
        notification = super().save(commit=False)
        
        if self.sender:
            notification.sender = self.sender
        
        # cleaned_data'dan recipient User objectini olamiz
        if 'recipient_user' in self.cleaned_data:
            notification.recipient = self.cleaned_data['recipient_user']
            print(f"DEBUG save() - Recipient set to: {notification.recipient.username}")
        else:
            raise ValueError("Recipient user topilmadi!")
        
        if commit:
            notification.save()
            print(f"✅ Notification saqlandi: ID={notification.id}")
        
        return notification

    
class InformationsForm(forms.ModelForm):
    class Meta:
        model = models.Informations
        fields = ['tg_admin', 'tg_channel', 'instagram', 'phone', 'logo', 'regions']

        widgets = {
            'tg_admin': forms.TextInput(attrs={'class': 'form-control'}),
            'tg_channel': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'regions' : forms.Select(attrs={"class" : "form-control", "id": "kt_select2_2"})
        }