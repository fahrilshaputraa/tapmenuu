"""
URL configuration for core project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('accounts/', include('allauth.urls')),
    path('onboarding/', views.onboarding_step1, name='onboarding_step1'),
    path('onboarding/theme/', views.onboarding_step2, name='onboarding_step2'),
    path('onboarding/team/', views.onboarding_step3, name='onboarding_step3'),
    path('dashboard/', include('dashboard.urls')),
    path('menu/', views.book_menu, name='book_menu'),
    path('payments/', include('payments.urls')),
    path('', include('menus.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
