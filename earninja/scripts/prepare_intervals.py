from exercises.music_theory_utils import (
    INTERVAL_NAMES,
    INTERVAL_TYPES,
    NUM_NOTES_IN_OCTAVE,
    get_num_semitones,
)
from exercises.models import Interval, IntervalInstance
from exercises.tasks import update_interval_instance_audio


def run(*args):
    lowest_octave = int(args[0])
    highest_octave = int(args[1])

    for interval_type in range(len(INTERVAL_TYPES)):
        for interval_name in INTERVAL_NAMES:
            interval, _ = Interval.objects.get_or_create(
                num_semitones=get_num_semitones(interval_name),
                interval_type=interval_type,
                defaults={"name": interval_name}
            )
            print(f"Generating objects and audio files for {interval}...")
            for start_note in range(lowest_octave * NUM_NOTES_IN_OCTAVE, (highest_octave + 1) * NUM_NOTES_IN_OCTAVE):
                interval_instance, created = IntervalInstance.objects.get_or_create(
                    start_note=start_note,
                    interval=interval
                )
                if created: update_interval_instance_audio(interval_instance.id)
