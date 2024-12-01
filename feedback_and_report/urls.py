from django.urls import path
from . import views

urlpatterns = [
    path("", views.HandleFeedbackAndReport.as_view(), name="handle_feedback_and_report")
]