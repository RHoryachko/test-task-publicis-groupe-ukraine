from django.urls import path
from . import views

app_name = "data_processing"

urlpatterns = [
    path("upload/", views.FileUploadView.as_view(), name="upload"),
    path("stats/", views.AggregatedStatsView.as_view(), name="stats"),
]
