from __future__ import annotations

import struct
import time
from typing import Tuple, Optional, TYPE_CHECKING
from ..exceptions import ChunkNotFoundException
from ..util import ceil
from .chunk import Chunk

if TYPE_CHECKING:
    from .world import World


class Region:
    """
    represents a minecraft region file of a minecraft world
    https://minecraft.fandom.com/wiki/Region_file_format
    """
    def __init__(self, region: Tuple[int, int], world: World):
        self.region: Tuple[int, int] = region
        self.world: World = world

        if not self.world.get_region_file(self.region):
            raise FileNotFoundError(f"there is no region {region[0]}, {region[1]} in world {world}")

        with open(self.world.get_region_file(self.region), "rb") as f:
            self.data: bytes = f.read()

    @staticmethod
    def get_offset_offset(chunk: Tuple[int, int]) -> int:
        """
        calculates the byte offset where the offset for the specified chunks data is
        :param chunk: the chunk
        :return: the byte offset of the offset data
        """
        return 4 * ((chunk[0] & 31) + (chunk[1] & 31) * 32)

    def get_chunk_location(self, chunk: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        gets the location of the chunk data for the specified chunk
        :param chunk: a chunk
        :return: tuple of the byte offset and the length of the data
        """
        location_offset: int = Region.get_offset_offset(chunk)
        offset_data = self.data[location_offset:location_offset + 4]
        offset: int = int.from_bytes(offset_data[:3], "big", signed=False)
        sector_length: int = int.from_bytes(offset_data[3:], "big", signed=False)
        if not (offset and sector_length):
            return None
        offset *= 2 ** 12
        sector_length *= 2 ** 12
        return offset, sector_length

    def get_raw_chunk(self, chunk: Tuple[int, int]) -> bytes:
        """
        reads the raw chunk data for a chunk from the region file
        :param chunk: the chunk coordinates
        :return: the raw chunk bytes
        """
        loc = self.get_chunk_location(chunk)
        if loc is None:
            raise ChunkNotFoundException(
                f"Chunk {chunk} is not present in Region File {self.world.get_region_file(self.region)}",
                chunk)
        offset, sector_length = loc
        return self.data[offset:offset + sector_length]

    def set_chunk(self, chunk: Tuple[int, int], data: bytes) -> None:
        """
        sets a chunk in the region file
        changed don't get written until Region#flush is called.
        :param chunk: the chunk coordinates to modify
        :param data: the new chunk data
        """
        loc = self.get_chunk_location(chunk)
        if loc is None:
            raise ChunkNotFoundException(f"Chunk {chunk} is not present in Region File {self.world.get_region_file(self.region)}", chunk)
        offset, _ = loc
        # set timestamp
        self.data = self.data[:offset + 4096] + struct.pack(">I", int(time.time())) + self.data[offset + 4100:]
        # set chunk data
        self.data = self.data[:offset] + data + self.data[offset + len(data):]
        # set sector length
        sector_count = int(1 + ((len(data) - 1) / 4096)).to_bytes(1, "big", signed=False)
        self.data = self.data[:Region.get_offset_offset(chunk) + 3] + sector_count + self.data[Region.get_offset_offset(chunk) + 4:]

    def get_chunk(self, chunk: Tuple[int, int]) -> Chunk:
        """
        reads the chunk data for the specified chunk from the region file and parses it into a Chunk object
        :param chunk: the chunk to read
        :return: the parsed Chunk
        """
        return Chunk(chunk, self)

    def flush(self) -> None:
        """
        writes all changes to the region file
        """
        with open(self.world.get_region_file(self.region), "wb") as f:
            f.write(self.data)
        print(f"Wrote file {self.world.get_region_file(self.region)}")
