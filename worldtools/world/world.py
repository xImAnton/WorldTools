from __future__ import annotations

from typing import Tuple, Optional
from os.path import join as joinpath
from os.path import isfile
from .region import Region
from .chunk import Chunk, ChunkSection
from ..nbt.types import Compound


class World:
    """
    represents a minecraft world or a backed up world
    """
    def __init__(self, path: str, enable_caching: bool = True):
        self.path: str = path
        self.caching: bool = enable_caching
        if self.caching:
            self.region_cache = {}

    def get_region(self, chunk: Tuple[int, int], use_cache: bool = True) -> Region:
        """
        gets the Region the specified chunk is in
        :param chunk: the chunk the Region is searched for
        :param use_cache: whether to use a cached value
        :return: the Region the specified chunks is in
        """
        position = self.get_region_coordinates(chunk)
        if self.caching and use_cache:
            if position not in self.region_cache:
                self.region_cache[position] = Region(World.get_region_coordinates(chunk), self)
            return self.region_cache[position]
        return Region(World.get_region_coordinates(chunk), self)

    def get_chunk(self, chunk: Tuple[int, int], use_cache: bool = True) -> Chunk:
        return self.get_region(chunk, use_cache=use_cache).get_chunk(chunk)

    def get_chunk_for_block(self, position: Tuple[int, int, int], region_cache: bool = True, chunk_cache: bool = True) -> Chunk:
        return self.get_chunk((position[0] // 16, position[2] // 16), region_cache=region_cache, chunk_cache=chunk_cache)

    def get_chunk_section_for_block(self, position: Tuple[int, int, int]) -> ChunkSection:
        return self.get_chunk_section((position[0] // 16, position[1] // 16, position[2] // 16))

    def get_block(self, position: Tuple[int, int, int]) -> Compound:
        chunk = self.get_chunk_section_for_block(position)
        return chunk.get_block((position[0] % 16, position[1] % 16, position[2] % 16))

    def get_chunk_section(self, section: Tuple[int, int, int]) -> ChunkSection:
        return self.get_chunk((section[0], section[2])).get_section(section[1])

    @staticmethod
    def get_region_coordinates(chunk: Tuple[int, int]) -> Tuple[int, int]:
        """
        calculated the region coordinates for the given chunk
        from https://minecraft.fandom.com/wiki/Region_file_format#Region_file_location
        :param chunk: the chunk the Region is searched for
        :return: the region coordinates of the chunk
        """
        return chunk[0] >> 5, chunk[1] >> 5

    def get_region_file(self, region: Tuple[int, int]) -> Optional[str]:
        """
        gets the path to a region file
        :param region: the region coordinates
        :return: the path of the region file
        """
        p = joinpath(self.path, "region", f"r.{region[0]}.{region[1]}.mca")
        if not isfile(p):
            return None
        return p
