from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('<int:pk>/delete/', views.report_delete, name='report_delete'),
    path('occupancy/', views.occupancy_report, name='occupancy_report'),
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('clients/', views.client_stats, name='client_stats'),
]