import subprocess
from pathlib import Path

from django.conf import settings

from mingus.containers import NoteContainer, Note, Bar
from mingus.midi.midi_file_out import write_NoteContainer, write_Bar
from pydub import AudioSegment


class AudioSaver:
    def __init__(self, audio_path):
        self.audio_path = Path(audio_path)
        self._load_settings()
    
    def save_interval_instance_audio(self, start_note, interval_name, interval_type):
        self._ensure_audio_dir_exists()
        if interval_type == 0:
            interval_mingus_object = self._get_harmonic_interval(start_note, interval_name)
        elif interval_type == 1:
            interval_mingus_object = self._get_melodic_interval(start_note, interval_name, ascending=True)
        elif interval_type == 2:
            interval_mingus_object = self._get_melodic_interval(start_note, interval_name, ascending=False)
        self._save_midi(interval_mingus_object)
        self._midi_to_wav()
        self._wav_to_mp3()
    
    def delete_files(self):
        for suffix in [".mid", ".wav", ".mp3"]:
            self.audio_path.with_suffix(suffix).unlink(missing_ok=True)

    def _load_settings(self):
        self.num_db_louder = settings.NUM_DB_LOUDER
        self.gain = settings.FLUIDSYNTH_GAIN
        self.sample_rate = settings.FLUIDSYNTH_SAMPLE_RATE
        self.soundfont_path = settings.SOUNDFONT_PATH
        self.fluidsynth_path = settings.FLUIDSYNTH_PATH
    
    def _ensure_audio_dir_exists(self):
        self.audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_harmonic_interval(self, start_note, interval_name):
        start_note = Note().from_int(start_note)
        return NoteContainer().from_interval(start_note, interval_name)
    
    def _get_melodic_interval(self, start_note, interval_name, ascending):
        start_note = Note().from_int(start_note)
        container = NoteContainer().from_interval(start_note, interval_name)
        if len(container.notes) == 1:
            note_1, note_2 = container.notes[0], container.notes[0]
        elif ascending:
            note_1, note_2 = container.notes
        else:
            note_2, note_1 = container.notes
        bar = Bar()
        bar.place_notes(note_1, 4)
        bar.place_notes(note_2, 4)
        return bar
    
    def _save_midi(self, interval_mingus_object):
        path = self.audio_path.with_suffix(".mid")
        if isinstance(interval_mingus_object, NoteContainer):
            write_NoteContainer(path, interval_mingus_object)
        elif isinstance(interval_mingus_object, Bar):
            write_Bar(path, interval_mingus_object)
    
    def _midi_to_wav(self):
        midi_file = self.audio_path.with_suffix(".mid")
        wav_file = self.audio_path.with_suffix(".wav")
        subprocess.call(
            [self.fluidsynth_path, '-niq', '-g', str(self.gain), self.soundfont_path, midi_file, '-F', wav_file, '-r', str(self.sample_rate)], 
        )
    
    def _wav_to_mp3(self):
        sound = AudioSegment.from_file(self.audio_path.with_suffix(".wav"), format="wav")
        sound += self.num_db_louder
        sound.export(self.audio_path.with_suffix(".mp3"), format='mp3')
