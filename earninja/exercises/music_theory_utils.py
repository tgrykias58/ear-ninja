from mingus.containers import NoteContainer, Note


def get_num_semitones(interval_name):
    interval_container = NoteContainer().from_interval(Note(), interval_name)
    if len(interval_container) == 1:
        return 0
    low_note, high_note = interval_container.notes
    return low_note.measure(high_note)