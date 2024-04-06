from django.views import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin

from exercises.models import (
    IntervalsExercise,
    IntervalAnswer,
)
from exercises.intervals_exercise_updater import IntervalsExerciseUpdater


class ChooseExerciseView(View):
    def get(self, request):
        return render(request, 'exercises/choose_exercise.html')
    
class IntervalsQuestionView(LoginRequiredMixin, View):
    def get(self, request):
        exercise = IntervalsExercise.objects.filter(user=request.user).first()
        context = {
            "exercise": exercise,
            "answers": exercise.answers.order_by("interval__num_semitones") if exercise else None
        }
        return render(request, 'exercises/intervals_question.html', context=context)
    
    @method_decorator(csrf_protect)
    def post(self, request):
        # generate new question when "next" or "start" button is clicked
        exercise, created = IntervalsExercise.objects.get_or_create(user=request.user)
        updater = IntervalsExerciseUpdater(exercise)
        if created:
            updater.set_default_settings()
            updater.reset_score()
        updater.generate_new_question()
        updater.save_audio_files()
        return redirect('exercises:intervals_question')

class IntervalsAnsweredView(LoginRequiredMixin, View):
    def get(self, request):
        exercise = IntervalsExercise.objects.get(user=request.user)
        user_answer = IntervalAnswer.objects.get(
            exercise=exercise, 
            interval_instance_id=request.session["user_answer_id"]
        )
        context = {
            "exercise": exercise,
            "user_answer": user_answer,
            "correct_answer": exercise.answers.get(intervalanswer__is_correct=True),
            "answers": exercise.answers.order_by("interval__num_semitones"),
        }
        return render(request, 'exercises/intervals_answered.html', context=context)

    @method_decorator(csrf_protect)
    def post(self, request):
        exercise = IntervalsExercise.objects.get(user=request.user)
        request.session["user_answer_id"] = request.POST["answer_id"]
        user_answer = exercise.answers.get(id=request.POST["answer_id"])
        IntervalsExerciseUpdater(exercise).update_score(user_answer)
        return redirect('exercises:intervals_answered')


class ScaleDegreesQuestionView(View):
    def get(self, request):
        return render(request, 'exercises/coming_soon.html', {"exercise_name": "Scale Degrees"})
