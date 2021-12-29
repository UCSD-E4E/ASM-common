import json
import os
import pathlib
import subprocess

import ASM_utils.ffmpeg.audio as audio
import ASM_utils.ffmpeg.ffmpeg as ffmpeg
import ASM_utils.ffmpeg.rtp as rtp
import ASM_utils.ffmpeg.video as video


def test_audioHWSource():
    test_time = 15
    sample_rate = 48000
    port = 8500
    num_channels = 1

    test_file_path = pathlib.Path('test_artifacts', 'test.mp3')
    if test_file_path.exists():
        test_file_path.unlink()
    test_file_path.parent.mkdir(parents=True, exist_ok=True)

    server_params = ['ffmpeg', '-i', f'tcp://127.0.0.1:{port}?listen', '-acodec', 'copy', '-flags',
         '+global_header', '-reset_timestamps', '1', test_file_path.as_posix()]
     
    rx_ffmpeg = subprocess.Popen(server_params)
    assert(rx_ffmpeg.poll() is None)
    
    audio_source = audio.HWAudioSource('default', num_channels=num_channels)
    audio_sink = rtp.RTPStream('127.0.0.1', port)
    audio_sink.configure_audio(codec='libmp3lame', rate=sample_rate)
    ffmpeg_config = ffmpeg.FFMPEGInstance(
        input_obj=audio_source, output_obj=audio_sink)
    ffmpeg_config.set_time(test_time)
    ffmpeg_cmd = ffmpeg_config.get_command()
    print(ffmpeg_cmd)
    subprocess.check_call(ffmpeg_cmd)
    assert(rx_ffmpeg.wait(test_time) == 0)

    test_file_params_json = subprocess.check_output(
        ['ffprobe', '-i', test_file_path.as_posix(), '-hide_banner', '-show_format', '-show_streams', '-v', 'fatal', '-of', 'json']).decode()
    test_file_params = json.loads(test_file_params_json)
    active_stream = test_file_params['streams'][0]
    assert(active_stream['codec_name'] == 'mp3')
    assert(int(active_stream['sample_rate']) == sample_rate)
    assert(int(active_stream['channels']) == num_channels)
    assert(abs(float(active_stream['duration']) - test_time) < 0.1)
