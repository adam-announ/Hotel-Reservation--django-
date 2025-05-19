from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('create/', views.room_create, name='room_create'),
    path('<int:pk>/', views.room_detail, name='room_detail'),
    path('<int:pk>/update/', views.room_update, name='room_update'),
    path('<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('types/', views.room_type_list, name='room_type_list'),
    path('types/create/', views.room_type_create, name='room_type_create'),
    path('types/<int:pk>/update/', views.room_type_update, name='room_type_update'),
    path('types/<int:pk>/delete/', views.room_type_delete, name='room_type_delete'),
    path('equipment/', views.manage_equipment, name='manage_equipment'),
    path('equipment/<int:pk>/update/', views.equipment_update, name='equipment_update'),
    path('equipment/<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
    path('availability/', views.search_availability, name='search_availability'),
]