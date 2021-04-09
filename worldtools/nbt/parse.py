from typing import Union
from os.path import isfile
from .types import *
from io import BytesIO
import gzip


class NBTParser:
    """
    static class for parsing minecraft NBT files
    """
    @staticmethod
    def parse(data: Union[str, bytes]):
        """
        Parses the specified file or data to Minecraft NBT
        :param data: Path to a file or byte data
        :return:
        """
        if isfile(data):
            with open(data, "rb") as f:
                data = f.read()
        elif isinstance(data, str):
            raise TypeError("data must be a file path or bytes")
        return NBTParser._parse(gzip.decompress(data))

    @staticmethod
    def _parse(data: bytes):
        root_compound = Compound.unpack(BytesIO(data))
        return root_compound
