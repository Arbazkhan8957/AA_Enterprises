# main_app/urls.py
from django.contrib import admin
from django.urls import path
from . import views
from .views import contact_view
from .views import register_view, login_view, logout_view, dashboard_view, home_view
from django.contrib.auth import views as auth_views
from django.conf import settings
from .views import CustomPasswordChangeView
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path("", home_view, name="home"),
    # path('products/', include('products.urls')),
    
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path('about/', views.about, name='about'),
    path('products/', views.product_list, name='products'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path("contact/", contact_view, name="contact"),
    path('brands/', views.brands, name='brands'),
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    path('password/change/', auth_views.PasswordChangeView.as_view(template_name='change_password.html'), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='change_password_done.html'), name='password_change_done'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
]

# Serving media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)