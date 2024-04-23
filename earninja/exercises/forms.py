from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from exercises.models import IntervalsExerciseSettings
from exercises.music_theory_utils import (
    get_interval_choices,
    get_interval_type_choices,
)

class IntervalsExerciseSettingsForm(forms.ModelForm):
    allowed_intervals = forms.MultipleChoiceField(
        choices=get_interval_choices(),
        widget=forms.CheckboxSelectMultiple,
        label="Choose which intervals to practice"
    )
    interval_type = forms.ChoiceField(
        choices=get_interval_type_choices(),
    )

    class Meta:
        model = IntervalsExerciseSettings
        fields = ["lowest_octave", "highest_octave"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['allowed_intervals'].initial = self._get_allowed_intervals()
        self.fields['interval_type'].initial = self._get_interval_type()
    
    def clean(self):
        cleaned_data = super().clean()
        lowest_octave = cleaned_data.get("lowest_octave")
        highest_octave = cleaned_data.get("highest_octave")

        if lowest_octave > highest_octave:
            raise ValidationError(
                _("Lowest octave has to be less than or equal to highest octave"),
                code="lowest_octave_larger_than_highest_octave"
            )
    
    def _get_interval_type(self):
        # currently only one interval type at a time is supported
        return self.instance.allowed_intervals.first().interval_type

    def _get_allowed_intervals(self):
        # this assumes that names of intervals in the database
        # match names of intervals from music_theory_utils.get_interval_choices()
        return [interval.name for interval in self.instance.allowed_intervals.all()]
