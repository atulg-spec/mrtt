from django.contrib import admin
from .models import JobOpening


@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'location', 'employment_type')
    search_fields = ('title', 'department', 'location', 'employment_type')
    list_filter = ('department', 'location', 'employment_type')
    ordering = ('title',)
