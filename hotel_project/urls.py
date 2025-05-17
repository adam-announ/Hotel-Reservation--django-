from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from accounts.views import dashboard_router
from accounts.views import dashboard_router, logout_view 
from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('rooms/', include('rooms.urls')),
    path('reservations/', include('reservations.urls')),
    path('reports/', include('reports.urls')),
    path('dashboard/', dashboard_router, name='dashboard'),
    path('logout/', logout_view, name='logout'),


    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)