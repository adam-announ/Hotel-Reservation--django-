from django.db import models
from django.utils import timezone
from accounts.models import Employee

class ReportType(models.TextChoices):
    OCCUPANCY = 'OCCUPANCY', 'Taux d\'occupation'
    REVENUE = 'REVENUE', 'Revenus'
    CLIENT_STATS = 'CLIENT_STATS', 'Statistiques clients'
    SERVICES = 'SERVICES', 'Services'

class Report(models.Model):
    title = models.CharField(max_length=200)
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        default=ReportType.OCCUPANCY
    )
    date_generated = models.DateTimeField(default=timezone.now)
    generated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='reports')
    content = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return f"{self.title} - {self.date_generated.strftime('%Y-%m-%d')}"