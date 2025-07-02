from django.contrib import admin
from .models import JobApplication, ContactForm


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'job', 'applied_at')
    list_filter = ('job', 'applied_at')
    search_fields = ('name', 'email', 'phone', 'job__title')
    readonly_fields = ('applied_at',)
    date_hierarchy = 'applied_at'
    ordering = ('-applied_at',)


@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'service')
    search_fields = ('name', 'email', 'phone', 'service')
    ordering = ('-id',)
