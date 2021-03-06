import re
import subprocess
from typing import Dict, List, Optional

from ASM_utils.ffmpeg.ffmpeg import AudioStream, MediaInput


class HWAudioSource(MediaInput, AudioStream):
    def __init__(self, id:str, *,num_channels:int=1, sample_rate:int=48000) -> None:
        self.__id = id
        if self.__id not in self.get_input_devices():
            raise RuntimeError("Invalid ID")
        self.__num_channels = num_channels
        self.__sample_rate = sample_rate
        self.__codec: Optional[str] = None
        self.__bitrate = 768000

    def configure_audio(self, *,
                        rate:int = None,
                        codec:str = None,
                        bitrate:int = None,
                        num_channels:int = None,
                        ) -> None:
        pass
        # TODO the following does not currently work - should it?
        # if rate:
        #     self.__sample_rate = rate
        # if codec:
        #     self.__codec = codec
        # if bitrate:
        #     self.__bitrate = bitrate
        # if num_channels:
        #     self.__num_channels = num_channels

    @staticmethod
    def get_input_devices() -> Dict[str, str]:
        arecord_output = subprocess.check_output(['arecord', '-L']).decode('ascii', 'ignore')
        card_regex = r"^(?P<device>[^\s]*)\n\s*(?P<desc>.*)"
        matches = re.finditer(card_regex, arecord_output, re.MULTILINE)
        cards = {match.group('device'): match.group('desc') for match in matches}

        return cards

    def create_ffmpeg_source_opts(self) -> List[str]:
        opts = ['-f', 'alsa', 
                '-channels', f'{self.__num_channels}',
                '-sample_rate', f'{self.__sample_rate}']
        # if self.__codec:
        #     opts.extend(['-codec:a', self.__codec])
        opts.extend(['-i', self.__id])
        return opts

