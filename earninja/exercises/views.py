from django.views import View
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from exercises.models import (
    IntervalsExercise,
    IntervalAnswer,
    IntervalsExerciseSettings,
)
from exercises.forms import IntervalsExerciseSettingsForm
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


class IntervalsSettingsView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = IntervalsExerciseSettings
    form_class = IntervalsExerciseSettingsForm
    template_name = "exercises/intervals_settings.html"
    success_url = reverse_lazy('exercises:intervals_question')

    def test_func(self):
        settings = self.get_object()
        return settings.exercise.user == self.request.user

    def form_valid(self, form):
        redirect_url = super().form_valid(form)
        settings = self.get_object()
        updater = IntervalsExerciseUpdater(settings.exercise)
        updater.set_allowed_intervals(
            form.cleaned_data['allowed_intervals'],
            form.cleaned_data['interval_type'],
        )
        # generate new question using new settings
        updater.generate_new_question()
        updater.save_audio_files()
        return redirect_url


class ScaleDegreesQuestionView(View):
    def get(self, request):
        return render(request, 'exercises/coming_soon.html', {"exercise_name": "Scale Degrees"})
