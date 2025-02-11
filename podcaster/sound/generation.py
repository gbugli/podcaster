from google.cloud import texttospeech
import os
from pydub import AudioSegment
from io import BytesIO
import re
import numpy as np
from datetime import date
from time import perf_counter, sleep
from google.api_core.exceptions import ResourceExhausted
from podcaster.config import config

def generate_raw_audio(topic, date_obj=None, audio_path=None, scripts_path=None, logger=None):

    if not date_obj:
        date_obj = date.today()

    client = texttospeech.TextToSpeechClient()
    date_str = date_obj.strftime('%Y%m%d')
    topic_len = 0

    if logger:
        logger.info(f'Generating audio for: {topic}')

    if not scripts_path:
        scripts_path = f'scripts/multi_host'

    date_path = f'{date_obj.year}/{date_obj.month}/{date_obj.day}'

    script_path = os.path.join(scripts_path, date_path, f'{date_str}.{topic}.md')
    if not os.path.exists(script_path):
        raise FileNotFoundError(f'{script_path} does not exist')

    with open(script_path, 'r') as f:
        script = f.read()

    pattern = r'```json(.*?)```'
    match = re.search(pattern, script, re.DOTALL)
    script_json = match.group(1).strip()

    script_json = eval(script_json)
    final_audio = None

    hosts = config.get('hostsPersonas')
    hosts_name = np.array([host['name'] for host in hosts])
    hosts_voice = np.array([host['voice'] for host in hosts])

    t0 = perf_counter()
    for section in script_json['turns']:
        if not section.get('text', None):
            continue

        topic_len += len(section["text"])
        synthesis_input = texttospeech.SynthesisInput(text=section["text"])

        if section['speaker'] in hosts_name:
            section['speaker'] = hosts_voice[np.where(section['speaker'] == hosts_name)]

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name=f"en-US-Journey-{section['speaker']}"
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        try:
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
        except ResourceExhausted:
            sleep(60)
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

        sound = AudioSegment.from_mp3(BytesIO(response.audio_content))

        final_audio = final_audio + sound if final_audio else sound

        if final_audio:
            final_audio += AudioSegment.silent(duration=min(1000, int(section["pause"])))

    if not audio_path:
        audio_path = f'audios/multi_host'

    audio_path = os.path.join(audio_path, f'{date_obj.year}/{date_obj.month}/{date_obj.day}')
    os.makedirs(audio_path, exist_ok=True)

    export = final_audio.export(f"{audio_path}/{date_str}.{topic}.mp3", format="mp3")
    if logger:
        logger.info(f'Generated audio for {topic}. Time to generate: {perf_counter()-t0}; Lenght of script: {topic_len}')

    return final_audio