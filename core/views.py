from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .forms import SignUpForm, StudentProfileForm,AppliedJobForm
from .models import Plan,JobApplier,AppliedJob,JobPosting
import razorpay
from django.views.decorators.csrf import csrf_protect
import pandas as pd
import os, re
from datetime import datetime
from django.db import connections
from django.shortcuts import render
from django.contrib import messages
from datetime import date, timedelta
from datetime import timezone


# Razorpay credentials
RAZORPAY_KEY_ID='rzp_test_Anl5NixDMZZiL0'
RAZORPAY_KEY_SECRET='2fQLWgSjV9PVLJA6ewSSOT6g'
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Check if user is a JobApplier
            if hasattr(user, 'jobapplier'):
                return redirect('job_applier_dashboard')
            else:
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def job_applier_dashboard(request):
    return render(request, 'job_applier_dashboard.html')


def home(request):
    return render(request, 'home.html')

@login_required
def plans(request):
    plans = Plan.objects.all()
    return render(request, 'plans.html', {'plans': plans})


@login_required
def subscribe(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    if request.method == 'POST':
        amount = int(plan.price * 100)
        order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1
        })

        context = {
            'plan': plan,
            'order_id': order['id'],
            'razorpay_key': RAZORPAY_KEY_ID,
            'amount': amount,
            'user': request.user
        }
        return render(request, 'payment_success.html', context)

    return redirect('plans')

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_resume(text):
    data = {
        'firstname': '',
        'lastname': '',
        'skills': '',
        'email': '',
        'description': ''
    }

    # First name & Last name (basic assumption based on first line or email)
    lines = text.strip().split('\n')
    if lines:
        name_parts = lines[0].split()
        if len(name_parts) >= 2:
            data['firstname'] = name_parts[0]
            data['lastname'] = name_parts[1]

    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email_match:
        data['email'] = email_match.group(0)

    # Skills
    skill_keywords = ['Python', 'Django', 'React', 'SQL', 'Machine Learning', 'Java', 'C++', 'HTML', 'CSS']
    skills_found = [skill for skill in skill_keywords if skill.lower() in text.lower()]
    data['skills'] = ", ".join(skills_found)

    # Description (just taking first 5 lines as summary)
    data['description'] = "\n".join(lines[1:6])

    return data


@login_required
def profile_form(request):
    initial_data = {}

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES)

        if request.FILES.get('resume'):
            resume = request.FILES['resume']
            text = ""
            if resume.name.endswith('.pdf'):
                text = extract_text_from_pdf(resume)
            elif resume.name.endswith('.docx'):
                text = extract_text_from_docx(resume)

            parsed_data = parse_resume(text)
            form = StudentProfileForm(initial=parsed_data)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.plan = Plan.objects.last()  # Update as needed
            profile.save()
            return redirect('home')
    else:
        form = StudentProfileForm()

    return render(request, 'profile_form.html', {'form': form})


@login_required(login_url='login')
def applied_job_create(request):
    if request.method == 'POST':
        form = AppliedJobForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Applied job recorded successfully.')
            return redirect('applied-job-create')  # or to a job list view
    else:
        form = AppliedJobForm()
    return render(request, 'job_form.html', {'form': form})


@login_required(login_url='login')  # protect route
def get_filtered_jobs(request):
    user = request.user
    filter_by = request.GET.get('filter', 'day')
    today = date.today()

    # default queryset
    jobs = AppliedJob.objects.none()
    today_count = week_count = month_count = 0

    if filter_by == 'day':
        jobs = AppliedJob.objects.filter(user=user, applied_date=today)
    elif filter_by == 'week':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        jobs = AppliedJob.objects.filter(user=user, applied_date__range=(start_of_week, end_of_week))
    elif filter_by == 'month':
        jobs = AppliedJob.objects.filter(user=user, applied_date__month=today.month, applied_date__year=today.year)

    # counts for metrics
    today_count = AppliedJob.objects.filter(user=user, applied_date=today).count()

    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    week_count = AppliedJob.objects.filter(user=user, applied_date__range=(start_of_week, end_of_week)).count()

    month_count = AppliedJob.objects.filter(user=user, applied_date__month=today.month, applied_date__year=today.year).count()

    # convert queryset to list of dicts for rendering
    records = list(jobs.values('job_title', 'company', 'applied_date', 'job_link'))

    return render(request, 'filtered_jobs.html', {
        'records': records,
        'selected_filter': filter_by,
        'today_count': today_count,
        'week_count': week_count,
        'month_count': month_count
    })
    
    
def job_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')  # or any other login route

    try:
        job_applier = JobApplier.objects.get(user=request.user)
        user_technologies = job_applier.technologies.all()
        matching_jobs = JobPosting.objects.filter(technologies__in=user_technologies).distinct()
    except JobApplier.DoesNotExist:
        matching_jobs = []

    context = {
        'matching_jobs': matching_jobs
    }
    return render(request, 'jobs_to_apply.html', context)