from django.urls import path
from . import views


urlpatterns = [
    
    # App views
    path("", views.index, name="index_login"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    # API endpoints
    path("api/register/", views.register_api_view, name="auth-api-register"),
    path("api/login/", views.login_api_view, name="auth-api-login"),
    path("api/logout/", views.logout_api_view, name="auth-api-logout")
    
]
