from helpers.permissions import ReceptionPassesTestMixin
from common import models
from django.shortcuts import render ,get_object_or_404
from django.views import View
from django.views.generic import ListView , DeleteView
from django.urls import reverse_lazy   
from django.db.models import Q 
from common import models
from manager import forms
from common.models import Group,Course
from helpers.views import CreateView, UpdateView, DeleteView
from common.mixins import RoleRequiredMixin
from helpers import permissions



class HomeView(ReceptionPassesTestMixin,View):
    def get(self, request):
        return render(request, "reception/base/index.html")



class CourseListView(ListView):
    model = models.Course
    template_name = "manager/course/list.html"
    context_object_name = "courses"
    def get_queryset(self):
        queryset = models.Course.objects.all().order_by("id")
        search = self.request.GET.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
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
    success_url ="reception:course-list"
    success_create_url ="reception:course-list"


class CourseUpdateView(UpdateView):
    model = models.Course
    form_class = forms.CourseForm
    context_object_name = "object"
    template_name = "manager/course/update.html"
    success_url = "reception:course-list"
    success_update_url = "reception:course-update"


class CourseDeleteView(DeleteView):
    model = models.Course
    success_url ="reception:course-list"


class GroupListView(ListView):
    model = models.Group
    template_name = "manager/group/list.html"
    context_object_name = "objects"
    paginate_by = 10
    def get_queryset(self):
        queryset = models.Group.objects.all().order_by("id")
        search = self.request.GET.get("search", None)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search))
        return queryset

def group_students(request, pk):
    group = get_object_or_404(Group, pk=pk)
    students = group.students.filter(status='ACTIVE') 
    context = {
        "group":group,
        "students":students
    }
    return render(request, "reception/group/group_students.html",context)

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

class StudentListView(ListView):
    model = models.Student
    template_name = "reception/student/list.html"
    context_object_name = "objects"
    paginate_by = 10
    def get_queryset(self):
        queryset = models.Student.objects.all().order_by("id")
        search = self.request.GET.get("search", None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(surname__icontains=search)
            )
        return queryset

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
        search = self.request.GET.get("search", None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(surname__icontains=search)
            )
        return queryset

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
