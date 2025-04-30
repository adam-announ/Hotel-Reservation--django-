from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('<int:pk>/', views.room_detail, name='room_detail'),
    path('create/', views.room_create, name='room_create'),
    path('<int:pk>/update/', views.room_update, name='room_update'),
    path('<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('search/', views.search_availability, name='search_availability'),
    path('types/', views.room_type_list, name='room_type_list'),
    path('types/create/', views.room_type_create, name='room_type_create'),
    path('equipment/', views.manage_equipment, name='manage_equipment'),
]