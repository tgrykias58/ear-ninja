from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from exercises.models import IntervalsExerciseSettings
from exercises.music_theory_utils import get_interval_choices


class IntervalsExerciseSettingsForm(forms.ModelForm):
    allowed_intervals = forms.MultipleChoiceField(
        choices=get_interval_choices(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = IntervalsExerciseSettings
        fields = ["lowest_octave", "highest_octave"]
    
    def clean(self):
        cleaned_data = super().clean()
        lowest_octave = cleaned_data.get("lowest_octave")
        highest_octave = cleaned_data.get("highest_octave")

        if lowest_octave > highest_octave:
            raise ValidationError(
                _("Lowest octave has to be less than or equal to highest octave"),
                code="lowest_octave_larger_than_highest_octave"
            )
