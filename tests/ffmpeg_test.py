import datetime as dt
import json
import pathlib
import shlex
import subprocess
import sys

import ASM_utils.ffmpeg.audio as audio
import ASM_utils.ffmpeg.ffmpeg as ffmpeg
import ASM_utils.ffmpeg.rtp as rtp
from ASM_utils.ffmpeg.file import (AudioFileSink, SegmentedAudioFileSink,
                                   SegmentedVideoFileSink)


def test_videoRTSPSink():
    folder = pathlib.Path("/", "tmp", "videoRTSPSink")
    folder.mkdir(parents=True, exist_ok=True)
    cmd = (f'/usr/bin/ffmpeg -i rtsp://rtsp.stream/pattern -c copy -flags +global_header'
            f' -f segment -segment_time 500 -strftime 1 -t 12 '
            f'-reset_timestamps 1 {folder.joinpath("%Y.%m.%d.%H.%M.%S.mp4").as_posix()} '
        )
    cmd2 = f'{sys.executable} -m ASM_utils.ffmpeg.split_log {folder.joinpath("stats.log").as_posix()} {folder.joinpath("info.log").as_posix()}'
    
    ffmpeg_p = subprocess.Popen(shlex.split(cmd), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logger_p = subprocess.Popen(shlex.split(cmd2), stdin=ffmpeg_p.stdout, stdout=None)
    logger_p.wait(timeout=15)

def test_videoRTSPSinkFastFail():
    folder = pathlib.Path("/", "tmp", "videoRTSPSink")
    folder.mkdir(parents=True, exist_ok=True)
    cmd = (f'/usr/bin/ffmpeg -i rtsp://rtsp.stream/pattern1 -c copy -flags +global_header'
            f' -f segment -segment_time 500 -strftime 1 -t 12 '
            f'-reset_timestamps 1 {folder.joinpath("%Y.%m.%d.%H.%M.%S.mp4").as_posix()} '
        )
    cmd2 = f'{sys.executable} -m ASM_utils.ffmpeg.split_log {folder.joinpath("stats.log").as_posix()} {folder.joinpath("info.log").as_posix()}'
    
    ffmpeg_p = subprocess.Popen(shlex.split(cmd), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logger_p = subprocess.Popen(shlex.split(cmd2), stdin=ffmpeg_p.stdout, stdout=None)
    logger_p.wait(timeout=1)


def test_audioHWSource():
    test_time = 15
    sample_rate = 48000
    port = 8500
    num_channels = 1

    test_file_path = pathlib.Path('test_artifacts', 'test_audioHWSource.mp3')
    if test_file_path.exists():
        test_file_path.unlink()
    test_file_path.parent.mkdir(parents=True, exist_ok=True)

    server_params = ['ffmpeg', '-i', f'tcp://127.0.0.1:{port}?listen', '-acodec', 'copy', test_file_path.as_posix()]
     
    rx_ffmpeg = subprocess.Popen(server_params)
    assert(rx_ffmpeg.poll() is None)
    
    audio_source = audio.HWAudioSource('default', num_channels=num_channels)
    audio_sink = rtp.RTPAudioStream('127.0.0.1', port)
    audio_sink.configure_audio(codec='libmp3lame', rate=sample_rate)
    ffmpeg_config = ffmpeg.FFMPEGInstance(
        input_obj=audio_source, output_obj=audio_sink)
    ffmpeg_config.set_time(test_time)
    ffmpeg_cmd = ffmpeg_config.get_command()
    print(' '.join(ffmpeg_cmd))
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

def test_audioServer():
    test_time = 15
    sample_rate = 48000
    port = 8500
    num_channels = 1
    ip_addr = '127.0.0.1'

    test_file_path = pathlib.Path('test_artifacts', 'test_audioServer.mp3')
    if test_file_path.exists():
        test_file_path.unlink()
    test_file_path.parent.mkdir(parents=True, exist_ok=True)

    stream_source = rtp.RTPAudioStream(ip_addr, port)
    stream_sink = AudioFileSink(path=test_file_path)
    server_config = ffmpeg.FFMPEGInstance(input_obj=stream_source, output_obj=stream_sink)
     
    server_cmd = server_config.get_command()
    rx_ffmpeg = subprocess.Popen(server_cmd)
    assert(rx_ffmpeg.poll() is None)
    
    audio_source = audio.HWAudioSource('default', num_channels=num_channels)
    audio_sink = rtp.RTPAudioStream(ip_addr, port)
    audio_sink.configure_audio(codec='libmp3lame', rate=sample_rate)
    client_config = ffmpeg.FFMPEGInstance(
        input_obj=audio_source, output_obj=audio_sink)
    client_config.set_time(test_time)
    subprocess.check_call(client_config.get_command())
    assert(rx_ffmpeg.wait(test_time) == 0)

def test_segment_output():
    test_time = 12
    num_channels = 1
    sample_rate = 48000
    test_data_dir = pathlib.Path('test_artifacts')
    test_data_dir.mkdir(parents=True, exist_ok=True)

    test_file_path = test_data_dir.joinpath('test_segment_output_%Y.%m.%d.%H.%M.%S.mp3')
    
    for test_file in test_data_dir.glob('test_segment_output_*.mp3'):
        test_file.unlink()

    audio_source = audio.HWAudioSource('default', num_channels=num_channels)
    stream_sink = SegmentedAudioFileSink(path=test_file_path, segment_length=dt.timedelta(seconds=5))
    stream_sink.configure_audio(codec='libmp3lame', rate=sample_rate)
    ffmpeg_config = ffmpeg.FFMPEGInstance(input_obj=audio_source, output_obj=stream_sink)
    ffmpeg_config.set_time(test_time)
     
    ffmpeg_cmd = ffmpeg_config.get_command()
    subprocess.check_call(ffmpeg_cmd)
    generated_files = list(test_data_dir.glob('test_segment_output_*.mp3'))
    assert(len(generated_files) == 3)
