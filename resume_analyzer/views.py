import json
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import JobDescriptionForm, ResumeUploadForm, ResumeVersionForm, RewriteForm, SignUpForm
from .models import Analysis, JobDescription, Resume, ResumeVersion
from .services.engine import analyze_resume, extract_text, parse_resume, rewrite_resume_text
from .services.reports import build_pdf_report


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'auth/register.html', {'form': form})


@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
    jobs = JobDescription.objects.filter(user=request.user)
    analyses = Analysis.objects.filter(user=request.user).select_related('resume','job')[:8]
    return render(request, 'dashboard.html', {'resumes': resumes, 'jobs': jobs, 'analyses': analyses})


@login_required
def resume_upload(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            try:
                resume.save()
                path = resume.file.path
                text = extract_text(path)
                if not text.strip():
                    resume.delete()
                    messages.error(request, 'No readable text was found in this file.')
                    return render(request, 'resume_upload.html', {'form': form})
                parsed = parse_resume(text, path)
                resume.extracted_text = text
                resume.parsed_data = parsed
                resume.quality_score = 0
                resume.save(update_fields=['extracted_text','parsed_data','quality_score','updated_at'])
            except Exception as exc:
                if resume.pk:
                    resume.delete()
                messages.error(request, f'Resume processing failed: {exc}')
                return render(request, 'resume_upload.html', {'form': form})
            ResumeVersion.objects.create(resume=resume, version_name='Original', note='Initial uploaded version')
            messages.success(request, 'Resume uploaded and parsed successfully.')
            return redirect('resume_detail', resume.id)
    else:
        form = ResumeUploadForm()
    return render(request, 'resume_upload.html', {'form': form})


@login_required
def resume_detail(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    return render(request, 'resume_detail.html', {'resume': resume, 'versions': resume.versions.all()})


@login_required
def create_version(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if request.method == 'POST':
        form = ResumeVersionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.resume = resume
            obj.save()
            messages.success(request, 'Resume version added.')
            return redirect('resume_detail', resume.id)
    else:
        form = ResumeVersionForm()
    return render(request, 'version_form.html', {'form': form, 'resume': resume})


@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            parsed = {'skills': [], 'title': job.title}
            job.extracted_data = parsed
            job.save(update_fields=['extracted_data'])
            messages.success(request, 'Job description saved.')
            return redirect('run_analysis', resume_id=request.GET.get('resume') or 0, job_id=job.id) if request.GET.get('resume') else redirect('dashboard')
    else:
        form = JobDescriptionForm()
    return render(request, 'job_form.html', {'form': form})


@login_required
def run_analysis(request, resume_id, job_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    job = get_object_or_404(JobDescription, id=job_id, user=request.user)
    try:
        result = analyze_resume(resume.extracted_text, job.description, resume.file.path)
    except Exception as exc:
        messages.error(request, f'Analysis failed: {exc}')
        return redirect('dashboard')
    analysis = Analysis.objects.create(
        user=request.user, resume=resume, job=job,
        overall_score=result['ats_score'], quality_score=result['resume_quality'], result=result
    )
    resume.quality_score = result['resume_quality']
    resume.save(update_fields=['quality_score','updated_at'])
    return redirect('analysis_detail', analysis.id)


@login_required
def analysis_detail(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    return render(request, 'analysis_detail.html', {'analysis': analysis, 'result': analysis.result})


@login_required
def download_report(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    try:
        pdf = build_pdf_report(analysis, analysis.result)
    except Exception as exc:
        messages.error(request, f'Could not generate report: {exc}')
        return redirect('analysis_detail', analysis.id)
    filename = f'ATS_Report_{analysis.id}.pdf'
    return FileResponse(pdf, as_attachment=True, filename=filename, content_type='application/pdf')


@login_required
def rewrite_view(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    if request.method == 'POST':
        form = RewriteForm(request.POST)
        if form.is_valid():
            original = form.cleaned_data['text']
            improved = rewrite_resume_text(original, form.cleaned_data.get('context',''))
            return render(request, 'rewrite.html', {'analysis': analysis, 'form': form, 'original': original, 'improved': improved})
    else:
        form = RewriteForm(initial={'text': '', 'context': analysis.job.title})
    return render(request, 'rewrite.html', {'analysis': analysis, 'form': form})
