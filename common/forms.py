from django import forms

from common import models

class BaseUserForm(forms.ModelForm):
    class Meta:
        model = models.BaseUser
        fields = [
            "full_name",
            "username",
            "phone",
            "role",
            "teacher_profile",
            "password",
        ]
        widgets = {
            "full_name" : forms.TelInput(attrs={"class" : "form-control", "placeholder" : "Fullname"}),
            "username" : forms.TextInput(attrs={"class" : "form-control", "placeholder" : "Username"}),
            "phone" : forms.TelInput(attrs={"class" : "form-control", "placeholder" : "Phone"}),
            "role" : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_2"}),
            "teacher_profile" : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_3"}),
            "password" : forms.PasswordInput(attrs={"class" : "form-control", "placeholder" : "Password"})
        }
