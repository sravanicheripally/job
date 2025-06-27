# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')
    skills = models.CharField(max_length=200)
    description = models.TextField()
    email = models.EmailField()
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)


class Technology(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    
class JobApplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)

    technologies = models.ManyToManyField(Technology)  # 👈 preferred tech
    def __str__(self):
        return self.user.username
    
class AppliedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # candidate
    job_link = models.URLField(max_length=500, blank=True, null=True)  # 👈 new field
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    applied_date = models.DateField(default=timezone.now)
   

    def __str__(self):
        return f"{self.user.username} - {self.job_title}"

class JobPosting(models.Model):
    job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    job_link = models.URLField(max_length=500)
    technologies = models.ManyToManyField(Technology)  # 👈 relevant tech
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"
