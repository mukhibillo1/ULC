from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class ManagerPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "manager"
        
    def handle_no_permission(self):
        user = self.request.user
        if user.role == "teacher":
            return redirect("teacher:home")
        if user.role == "reception":
            return redirect("reception:home")
        if user.role == "accountant":
            return redirect("accountant:home")


class ReceptionPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "reception"

    def handle_no_permission(self):
        user = self.request.user
        if user.role == "teacher":
            return redirect("teacher:home")
        if user.role == "manager":
            return redirect("manager:home")
        if user.role == "accountant":
            return redirect("accountant:home")


class AccountantPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "accountant"

    def handle_no_permission(self):
        user = self.request.user
        if user.role == "teacher":
            return redirect("teacher:home")
        if user.role == "manager":
            return redirect("manager:home")
        if user.role == "reception":
            return redirect("reception:home")


class TeacherPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "teacher"

    def handle_no_permission(self):
        user = self.request.user
        if user.role == "Accountant":
            return redirect("accountant:home")
        if user.role == "Manager":
            return redirect("manager:home")
        if user.role == "Reception":
            return redirect("reception:home")


