from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View

from .forms import DataFileUploadForm
from .services import process_file_upload, get_aggregated_stats


class FileUploadView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:login")

    def post(self, request, *args, **kwargs):
        form = DataFileUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "Оберіть файл xls або csv.")
            return redirect("users:dashboard")

        success, msg, is_error = process_file_upload(request.user, form.cleaned_data["file"])
        if is_error:
            messages.error(request, msg)
        else:
            messages.success(request, msg)
        return redirect("users:dashboard")


class AggregatedStatsView(LoginRequiredMixin, TemplateView):
    template_name = "data_processing/aggregated_stats.html"
    login_url = reverse_lazy("users:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_aggregated_stats())
        return context
