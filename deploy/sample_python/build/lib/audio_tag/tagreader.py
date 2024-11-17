"""Module to get tag information from audio files

Returns:
    None:
"""
import argparse
from tinytag import TinyTag # pylint: disable=F0401

def get_track(tag):
    """This function gets the name of the artist

    Args:
        tag (tinytag object): Tag object from tinytag

    Returns:
        string: returns the name of the artist
    """
    return tag.artist

def get_duration(tag):
    """This function gets the duration of the song

    Args:
        tag (tinytag object): Tag object from tinytag

    Returns:
        string: returns the duration of the song
    """
    return round(tag.duration, 2)

def get_album(tag):
    """This function gets the album name

    Args:
        tag (tinytag object): Tag object from tinytag

    Returns:
        string: returns the album name
    """
    return tag.album

def get_genre(tag):
    """This function gets the genre of the song

    Args:
        tag (tinytag object): Tag object from tinytag

    Returns:
        string: returns the genre of the song
    """
    return tag.genre

def get_title(tag):
    """This function gets the title of the song

    Args:
        tag (tinytag object): Tag object from tinytag

    Returns:
        string: returns the title of the song
    """
    return tag.title

PARSER = argparse.ArgumentParser(description='Get music meta-data')

PARSER.add_argument('filename', nargs='?', type=str, default='music_example.mp3', \
    help='File name with extension. \
Supported extensions are MP3 (ID3 v1, v1.1, v2.2, v2.3+),\
     Wave/RIFF, OGG, OPUS, FLAC, WMA, MP4/M4A/M')
ARGS = PARSER.parse_args()

TAG = TinyTag.get(ARGS.filename)

TRACK = get_track(TAG)
DURATION = get_duration(TAG)
ALBUM = get_album(TAG)
GENRE = get_genre(TAG)
TITLE = get_title(TAG)

print('This track is by %s.' % TRACK)
print('It is %f seconds long.' % DURATION)
print('It is from album %s.' % ALBUM)
print('The genre of the song is %s.' % GENRE)
print('The title of the song is %s.' % TITLE)
