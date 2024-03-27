import subprocess
from pathlib import Path

from django.conf import settings

from mingus.containers import NoteContainer, Note
from mingus.midi.midi_file_out import write_NoteContainer
from pydub import AudioSegment


class AudioSaver:
    def __init__(self, audio_path):
        self.audio_path = Path(audio_path)
        self._load_settings()
    
    def save_interval_instance_audio(self, start_note, interval_name):
        self._ensure_audio_dir_exists()
        interval_container = self._get_interval_container(start_note, interval_name)
        self._save_midi(interval_container)
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
    
    def _get_interval_container(self, start_note, interval_name):
        start_note = Note().from_int(start_note)
        return NoteContainer().from_interval(start_note, interval_name)
    
    def _save_midi(self, mingus_containter):
        write_NoteContainer(self.audio_path.with_suffix(".mid"), mingus_containter)
    
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
