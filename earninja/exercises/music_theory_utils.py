from mingus.containers import NoteContainer, Note


NUM_NOTES_IN_OCTAVE = 12
INTERVAL_NAMES = ['1', 'b2', '2', 'b3', '3', '4', '#4', '5', 'b6', '6', 'b7', '7', '8']
INTERVAL_TYPES = ["harmonic", "melodic ascending", "melodic descending"]


def get_interval_container(start_note_int, interval_name):
    start_note = Note().from_int(start_note_int)
    if interval_name == '8':
        return NoteContainer([
            start_note,
            Note().from_int(start_note_int + NUM_NOTES_IN_OCTAVE)
        ])
    return NoteContainer().from_interval(start_note, interval_name)

def get_num_semitones(interval_name):
    if interval_name == '1': return 0
    if interval_name == '8': return 12
    interval_container = NoteContainer().from_interval(Note(), interval_name)
    low_note, high_note = interval_container.notes
    return low_note.measure(high_note)

def get_interval_long_name(interval_name):
    if interval_name == '1': return 'unison'
    if interval_name == '8': return 'octave'
    return NoteContainer().from_interval(Note(), interval_name).determine()[0]

def get_note_name(note_int):
    return str(Note().from_int(note_int)).replace("'", "")

def get_interval_choices():
    return [
        (interval_name, f'{get_interval_long_name(interval_name)} ({interval_name})')
        for interval_name in INTERVAL_NAMES
    ]

def get_interval_type_choices():
    return [(i, interval_type) for i, interval_type in enumerate(INTERVAL_TYPES)]
