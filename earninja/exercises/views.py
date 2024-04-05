from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from exercises.models import IntervalsExercise


class ChooseExerciseView(View):
    def get(self, request):
        return render(request, 'exercises/choose_exercise.html')
    
class IntervalsQuestionView(LoginRequiredMixin, View):
    def get(self, request):
        exercise = IntervalsExercise.objects.filter(user=request.user).first()
        return render(request, 'exercises/intervals_question.html', context={"exercise": exercise})

class ScaleDegreesQuestionView(View):
    def get(self, request):
        return render(request, 'exercises/coming_soon.html', {"exercise_name": "Scale Degrees"})
