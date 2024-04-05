from django.views import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin

from exercises.models import IntervalsExercise
from exercises.intervals_exercise_updater import IntervalsExerciseUpdater


class ChooseExerciseView(View):
    def get(self, request):
        return render(request, 'exercises/choose_exercise.html')
    
class IntervalsQuestionView(LoginRequiredMixin, View):
    def get(self, request):
        exercise = IntervalsExercise.objects.filter(user=request.user).first()
        return render(request, 'exercises/intervals_question.html', context={"exercise": exercise})
    
    @method_decorator(csrf_protect)
    def post(self, request):
        # generate new question when "next" or "start" button is clicked
        exercise, created = IntervalsExercise.objects.get_or_create(user=request.user)
        updater = IntervalsExerciseUpdater(exercise)
        if created: updater.set_default_settings()
        updater.generate_new_question()
        updater.save_audio_files()
        return redirect('exercises:intervals_question')
    

class ScaleDegreesQuestionView(View):
    def get(self, request):
        return render(request, 'exercises/coming_soon.html', {"exercise_name": "Scale Degrees"})
