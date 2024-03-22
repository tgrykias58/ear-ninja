from django.views import View
from django.shortcuts import render


class ChooseExerciseView(View):
    def get(self, request):
        return render(request, 'exercises/choose_exercise.html')
    
class IntervalsQuestionView(View):
    def get(self, request):
        return render(request, 'exercises/coming_soon.html', {"exercise_name": "Intervals"})

class ScaleDegreesQuestionView(View):
    def get(self, request):
        return render(request, 'exercises/coming_soon.html', {"exercise_name": "Scale Degrees"})
