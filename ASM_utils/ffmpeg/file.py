import datetime as dt
from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from ASM_utils.ffmpeg.ffmpeg import MediaOutput


class AudioFileSink(MediaOutput):
    FILE_EXT_MAP = {
        'libmp3lame': '.mp3'
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
        opts = []
        for key, value in self._audio_flags.items():
            if not isinstance(value, list):
                opts.append('-' + key)
                opts.append(value)
            else:
                for val in value:
                    opts.append(f'-{key}')
                    opts.append(val)

        if self._path is None:
            raise RuntimeError("Path not specified")

        if 'codec:a' in self._audio_flags:
            codec = str(self._audio_flags['codec:a'])
            expected_extension = self.FILE_EXT_MAP[codec]
            if expected_extension != self._path.suffix:
                raise RuntimeError(f'Mismatched codec ({codec}) and extension: ({expected_extension})')
        
        opts.append(self._path.as_posix())
        return opts


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