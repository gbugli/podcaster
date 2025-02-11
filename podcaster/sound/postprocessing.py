from pydub import AudioSegment
from podcaster.sound.equalization import Equalizer
from datetime import date
import os

def post_process(song_path, date_obj=None, topics=None, audio_path=None, output_path=None, format="wav"):

    if song_path.endswith('mp3'):
        song = AudioSegment.from_mp3(song_path)
    elif song_path.endswith('wav'):
        song = AudioSegment.from_wav(song_path)
    else:
        raise NotImplementedError('Only supporting mp3 and wav files')
    
    if not date_obj:
        date_obj = date.today()

    if not audio_path:
        audio_path = f'audios/multi_host'
    
    date_path = f'{date_obj.year}/{date_obj.month}/{date_obj.day}'
    date_str = date_obj.strftime('%Y%m%d')

    long_podcast = AudioSegment.silent(duration=4000)
    indexes = []

    equalizer = Equalizer()

    for topic in topics:
        section_path = os.path.join(audio_path, date_path, f'{date_str}.{topic}.mp3')

        # podcast = eq.equalize(section_path)
        podcast = AudioSegment.from_mp3(section_path)
        silence = AudioSegment.silent(duration=4000)

        long_podcast += podcast
        start_i = len(long_podcast)
        long_podcast += silence
        end_i = len(long_podcast)
        indexes.append((start_i, end_i,))

    long_song = song

    while len(long_song) < len(long_podcast):
        long_song = long_song * 2

    long_song = long_song[:len(long_podcast)]

    five_seconds = 5 * 1000
    first_five_seconds = long_song[:five_seconds]
    beginning  = first_five_seconds - 10
    beginning = beginning.fade_out(2000)

    middle = []
    for j, idxs in enumerate(indexes):
        if j == 0:
            m = long_song[five_seconds:idxs[0]] - 35
        else:
            m = long_song[indexes[j-1][1]:idxs[0]] - 35

        soft_m = m.fade_in(3000)
        middle.append(soft_m)

        p = long_song[idxs[0]:idxs[1]]
        p = p - 12
        soft_p = p.fade_in(1500).fade_out(1000)

        middle.append(soft_p)

    awesome = beginning + sum(middle)
    final = long_podcast.overlay(awesome, position=0)
    
    eq_final = equalizer.equalize(final)
    if not output_path:
        output_path = 'podcasts'

    os.makedirs(output_path, exist_ok=True)

    eq_final.export(f"{output_path}/{date_str}.podcast.eq.{format}", format=format)
    return eq_final
