from django.urls import path

from . import views

app_name = "exercises"
urlpatterns = [
    path("", views.ChooseExerciseView.as_view(), name="choose_exercise"),
    path("intervals/question", views.IntervalsQuestionView.as_view(), name="intervals_question"),
    path("scale-degrees/question", views.ScaleDegreesQuestionView.as_view(), name="scale_degrees_question"),
]