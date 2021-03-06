from typing import Dict, List, Optional

from ASM_utils.ffmpeg.ffmpeg import AudioStream, MediaInput, MediaOutput, VideoStream


class RTPBaseStream(MediaOutput, MediaInput):
    def __init__(self, hostname:str, port:Optional[int] = 554, protocol:str = 'tcp', format:str = 'mpegts'):
        super().__init__()
        self.__protocol = protocol
        self.__hostname = hostname
        self.__port = port
        self._audio_flags:Dict[str, str] = {}
        self._video_flags:Dict[str, str] = {'f': format}

    def create_ffmpeg_sink_opts(self) -> List[str]:
        opts = []
        for key, value in self._audio_flags.items():
            opts.append('-' + key)
            opts.append(value)
        for key, value in self._video_flags.items():
            opts.append('-' + key)
            opts.append(value)
        if self.__port is None:
            raise RuntimeError("Port not set")
        opts.append(f'{self.__protocol}://{self.__hostname}:{self.__port}')
        return opts
    
    def create_ffmpeg_source_opts(self) -> List[str]:
        opts = []
        for key, value in self._audio_flags.items():
            opts.append('-' + key)
            opts.append(value)
        for key, value in self._video_flags.items():
            opts.append('-' + key)
            opts.append(value)
        if self.__port is None:
            raise RuntimeError("Port not set")
        opts.append('-i')
        opts.append(f'{self.__protocol}://{self.__hostname}:{self.__port}?listen')
        return opts

    def set_port(self, port:int) -> None:
        self.__port = port

class RTPAudioStream(RTPBaseStream, AudioStream):
    def configure_audio(self, *,
                        rate:int = None,
                        codec:str = None,
                        bitrate:int = None,
                        num_channels: int = None):
        if rate is not None:
            self._audio_flags['ar'] = f'{rate}'
        if codec is not None:
            self._audio_flags['codec:a'] = codec
        if bitrate is not None:
            self._audio_flags['b:a'] = f'{bitrate}'
        if num_channels is not None:
            self._audio_flags['ac'] = f'{num_channels}'

class RTPVideoStream(RTPAudioStream, VideoStream):
    def configure_video(self, *,
                        rate:int = None,
                        codec:str = None,
                        bitrate:int = None,
                        ):
        if rate is not None:
            self._video_flags['r:v'] = f'{rate}'
        if codec is not None:
            self._video_flags['codec:v'] = codec
        if bitrate is not None:
            self._video_flags['b:v'] = f'{bitrate}'