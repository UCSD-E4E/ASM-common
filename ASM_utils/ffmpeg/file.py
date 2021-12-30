import datetime as dt
from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from ASM_utils.ffmpeg.ffmpeg import AudioStream, MediaOutput, VideoStream


class AudioFileSink(MediaOutput, AudioStream):
    FILE_EXT_MAP = {
        'libmp3lame': '.mp3',
        'mpegts': '.mp4'
    }
    def __init__(self, *, path: PathLike = None) -> None:
        super().__init__()
        if path is not None:
            self._path: Optional[Path] = Path(path)
        else:
            self._path = None
        self._audio_flags: Dict[str, Union[str, List[str]]] = {}
    
    def setPath(self, path: PathLike) -> None:
        self._path = Path(path)

    def configure_audio(self, *,
                    rate:int = None,
                    codec:str = None,
                    bitrate:int = None,
                    num_channels: int = None) -> None:
        if rate is not None:
            self._audio_flags['ar'] = f'{rate}'
        if codec is not None:
            self._audio_flags['codec:a'] = codec
        if bitrate is not None:
            self._audio_flags['b:a'] = f'{bitrate}'
        if num_channels is not None:
            self._audio_flags['ac'] = f'{num_channels}'

    def create_ffmpeg_sink_opts(self) -> List[str]:
        if self._path is None:
            raise RuntimeError("Path not specified")
        opts = []
        for key, value in self._audio_flags.items():
            if not isinstance(value, list):
                opts.append('-' + key)
                opts.append(value)
            else:
                for val in value:
                    opts.append(f'-{key}')
                    opts.append(val)

        self.verify_codec()
        
        opts.append(self._path.as_posix())
        return opts

    def verify_codec(self):
        if self._path is None:
            raise RuntimeError("Path not specified")
        if 'codec:a' in self._audio_flags:
            codec = str(self._audio_flags['codec:a'])
            expected_extension = self.FILE_EXT_MAP[codec]
            if expected_extension != self._path.suffix:
                raise RuntimeError(f'Mismatched codec ({codec}) and extension: ({expected_extension})')

class VideoFileSink(AudioFileSink, VideoStream):
    def __init__(self, *, path: PathLike = None) -> None:
        super().__init__(path=path)
        self._video_flags: Dict[str, Union[str, List[str]]] = {}

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

    def create_ffmpeg_sink_opts(self) -> List[str]:
        if self._path is None:
            raise RuntimeError("Path not specified")
        opts = super().create_ffmpeg_sink_opts()[:-1]
        for key, value in self._video_flags.items():
            if not isinstance(value, list):
                opts.append('-' + key)
                opts.append(value)
            else:
                for val in value:
                    opts.append(f'-{key}')
                    opts.append(val)

        opts.append(self._path.as_posix())
        return opts

    def verify_codec(self):
        if self._path is None:
            raise RuntimeError("Path not specified")
        if 'codec:v' in self._video_flags:
            codec = str(self._video_flags['codec:v'])
            expected_extension = self.FILE_EXT_MAP[codec]
            if expected_extension != self._path.suffix:
                raise RuntimeError(f'Mismatched codec ({codec}) and extension: ({expected_extension})')

        if 'codec:a' in self._audio_flags and len(self._video_flags) == 0:
            codec = str(self._audio_flags['codec:a'])
            expected_extension = self.FILE_EXT_MAP[codec]
            if expected_extension != self._path.suffix:
                raise RuntimeError(f'Mismatched codec ({codec}) and extension: ({expected_extension})')

class SegmentedAudioFileSink(AudioFileSink):
    def __init__(self, *, path: PathLike = None, segment_length: dt.timedelta = None) -> None:
        super().__init__(path=path)
        self._audio_flags.update({
            'strftime': '1',
            'reset_timestamps': '1',
            'flags': '+global_header',
            'f': 'segment'
            })
        if segment_length is not None:
            self._audio_flags['segment_time'] = f'{int(segment_length.total_seconds())}'
        dt.datetime.now().strftime(str(path))

    def set_segment_length(self, segment_length: dt.timedelta) -> None:
        self._audio_flags['segment_time'] = f'{int(segment_length.total_seconds())}'

    def create_ffmpeg_sink_opts(self) -> List[str]:
        if 'segment_time' not in self._audio_flags:
            raise RuntimeError("Segment length not specified")
        return super().create_ffmpeg_sink_opts()

class SegmentedVideoFileSink(SegmentedAudioFileSink, VideoFileSink):
    pass