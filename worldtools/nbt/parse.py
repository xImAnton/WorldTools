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
    def parse(data: Union[str, bytes, BytesIO], decompress=True):
        """
        Parses the specified file or data to Minecraft NBT
        :param data: Path to a file or byte data
        :param decompress: whether to decompress the specified data
        :return: root compound of given binary data
        """
        if isinstance(data, BytesIO):
            return NBTParser._parse(data)
        if isfile(data):
            with open(data, "rb") as f:
                data = f.read()
        elif isinstance(data, str):
            raise TypeError("data must be a file path or bytes")
        if decompress:
            data = gzip.decompress(data)
        return NBTParser._parse(BytesIO(data))

    @staticmethod
    def _parse(data: BytesIO):
        root_compound = Compound.unpack(data)
        return root_compound[""]
