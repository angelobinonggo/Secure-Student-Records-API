"""
admin.py — Register StudentRecord in Django Admin
"""
from django.contrib import admin
from .models import StudentRecord


@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'course', 'year_level', 'gpa', 'owner', 'updated_at')
    list_filter = ('course', 'year_level')
    search_fields = ('full_name', 'owner__username')
    ordering = ('full_name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Student Info', {
            'fields': ('owner', 'full_name', 'course', 'year_level', 'gpa')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
