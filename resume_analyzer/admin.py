from django.contrib import admin
from .models import Analysis, JobDescription, Resume, ResumeVersion

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'quality_score', 'created_at')
    search_fields = ('title', 'user__username')

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'user', 'created_at')
    search_fields = ('title', 'company', 'description')

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'job', 'overall_score', 'created_at')
    list_filter = ('created_at',)

@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = ('version_name', 'resume', 'created_at')
