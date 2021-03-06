from abc import ABC, abstractmethod
from typing import List, Optional


class AudioStream(ABC):
    @abstractmethod
    def configure_audio(self, *,
                        rate:int = None,
                        codec:str = None,
                        bitrate:int = None,
                        num_channels: int = None) -> None:
        pass
    
class VideoStream(ABC):
    @abstractmethod
    def configure_video(self, *,
                        rate:int = None,
                        codec:str = None,
                        bitrate:int = None,
                        ) -> None:
        pass

class MediaInput(ABC):
    @abstractmethod
    def create_ffmpeg_source_opts(self) -> List[str]:
        pass

class MediaOutput(ABC):
    @abstractmethod
    def create_ffmpeg_sink_opts(self) -> List[str]:
        pass

class FFMPEGInstance:
    def __init__(self, *, input_obj: Optional[MediaInput] = None, output_obj: Optional[MediaOutput] = None):
        self.__input = input_obj
        self.__output = output_obj
        self.__time: Optional[int] = None

    def get_args(self) -> List[str]:
        opts = []
        if self.__input is None:
            raise RuntimeError("No input configuration")
        opts.extend(self.__input.create_ffmpeg_source_opts())
        if self.__time is not None:
            opts.extend(['-t', f'{self.__time}'])
        if self.__output is None:
            raise RuntimeError("No output configuration")
        
        if isinstance(self.__output, VideoStream) and not isinstance(self.__input, VideoStream):
            raise RuntimeError("No video source!")
        if isinstance(self.__output, AudioStream) and not isinstance(self.__input, AudioStream):
            raise RuntimeError("No audio source!")
        
        opts.extend(self.__output.create_ffmpeg_sink_opts())
        return opts

    def get_command(self) -> List[str]:
        cmd = ['ffmpeg']
        cmd.extend(self.get_args())
        return cmd

    def set_input(self, input_obj: MediaInput):
        self.__input = input_obj

    def set_output(self, output_obj: MediaOutput):
        self.__output = output_obj

    def set_time(self, time_s:int):
        self.__time = time_s
