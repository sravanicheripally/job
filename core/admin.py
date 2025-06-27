from django.contrib import admin
from .models import Plan, StudentProfile,JobApplier,Technology,JobPosting

admin.site.register(Plan)
admin.site.register(StudentProfile)
admin.site.register(JobApplier)
admin.site.register(Technology)
admin.site.register(JobPosting)