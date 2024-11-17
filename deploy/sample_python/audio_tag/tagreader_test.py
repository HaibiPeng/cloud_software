from audio_tag.tagreader import get_album, get_duration, get_genre, get_title, get_track
from tinytag import TinyTag


def test_get_album():
    tag = TinyTag.get('music_example.mp3')
    assert  get_album(tag) == 'AS220 Foo Fest 2018 Sampler'

def test_get_track():
    tag = TinyTag.get('music_example.mp3')
    assert  get_track(tag) == 'Rah Digga'

def test_get_duration():
    tag = TinyTag.get('music_example.mp3')
    assert  get_duration(tag) == 194.12

def test_get_genre():
    tag = TinyTag.get('music_example.mp3')
    assert  get_genre(tag) == 'Compilation'

def test_get_title():
    tag = TinyTag.get('music_example.mp3')
    assert  get_title(tag) == 'Angela Davis (Produced by J-Pilot)'



