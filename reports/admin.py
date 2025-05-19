from django.contrib import admin
from .models import Report, ReportType

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'date_generated', 'generated_by', 'start_date', 'end_date')
    list_filter = ('report_type', 'date_generated')
    search_fields = ('title', 'content')
    readonly_fields = ('date_generated',)
    date_hierarchy = 'date_generated'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'report_type', 'date_generated', 'generated_by')
        }),
        ('Période du rapport', {
            'fields': ('start_date', 'end_date')
        }),
        ('Contenu', {
            'fields': ('content',)
        }),
    )