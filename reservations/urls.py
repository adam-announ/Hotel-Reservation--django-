from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation_list, name='reservation_list'),
    path('<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('create/', views.create_reservation, name='create_reservation'),
    path('<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('<int:pk>/check-in/', views.check_in, name='check_in'),
    path('<int:pk>/check-out/', views.check_out, name='check_out'),
    path('<int:pk>/confirmation/', views.reservation_confirmation, name='reservation_confirmation'),
    path('payment/<int:reservation_id>/', views.create_payment, name='create_payment'),
    path('services/', views.manage_services, name='manage_services'),
]