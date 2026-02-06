from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class UserLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("users:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "users/dashboard.html"
    login_url = reverse_lazy("users:login")
