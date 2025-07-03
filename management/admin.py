from django.contrib import admin
from .models import JobOpening, Announcement
from django.utils.html import format_html

@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'location', 'employment_type')
    search_fields = ('title', 'department', 'location', 'employment_type')
    list_filter = ('department', 'location', 'employment_type')
    ordering = ('title',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag', 'created_at', 'image_preview')
    search_fields = ('title', 'tag', 'description')
    list_filter = ('tag', 'created_at')
    ordering = ('-created_at',)

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="height: 50px; border-radius: 4px;" />', obj.image_url)
        return "-"
    image_preview.short_description = 'Image'
