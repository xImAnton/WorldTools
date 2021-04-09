from __future__ import annotations

from typing import Tuple, Optional
from os.path import join as joinpath
from os.path import isfile
from .region import Region


class World:
    """
    represents a minecraft world or a backed up world
    """
    def __init__(self, path: str):
        self.path: str = path

    def get_region(self, chunk: Tuple[int, int]) -> Region:
        """
        gets the Region the specified chunk is in
        :param chunk: the chunk the Region is searched for
        :return: the Region the specified chunks is in
        """
        return Region(World.get_region_coordinates(chunk), self)

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
