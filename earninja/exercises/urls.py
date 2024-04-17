from django.urls import path

from . import views

app_name = "exercises"
urlpatterns = [
    path("", views.ChooseExerciseView.as_view(), name="choose_exercise"),
    path("intervals/question/", views.IntervalsQuestionView.as_view(), name="intervals_question"),
    path("intervals/answered/", views.IntervalsAnsweredView.as_view(), name="intervals_answered"),
    path("intervals/settings/<int:pk>/", views.IntervalsSettingsView.as_view(), name="intervals_settings"),
    path("intervals/reset-score/", views.IntervalsResetScoreView.as_view(), name="intervals_reset_score"),
    path("intervals/reset-settings/", views.IntervalsResetSettingsView.as_view(), name="intervals_reset_settings"),
    path("scale-degrees/question/", views.ScaleDegreesQuestionView.as_view(), name="scale_degrees_question"),
]