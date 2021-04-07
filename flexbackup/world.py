from __future__ import annotations

from typing import List, Tuple, Dict, Optional
from os.path import join as joinpath
from os.path import isfile
from .util import ceil


class ChunkNotFoundException(Exception):
    """
    raised when a mentioned chunk is not present in the current world
    """
    def __init__(self, msg, chunk):
        super(ChunkNotFoundException, self).__init__(msg)
        self.chunk = chunk


class ChunkRestorer:
    """
    class to transfer chunks from one world to another
    """
    def __init__(self, target_world: str, backup_world: str):
        self.target_world: World = World(target_world)
        self.backup_world: World = World(backup_world)
        self.actions: List[Tuple[int, int]] = []

    def add_chunk(self, chunk: Tuple[int, int]) -> None:
        """
        adds a chunk for transmission
        :param chunk: the chunk to transfer
        """
        self.actions.append(chunk)

    def _sort_actions_by_regions(self) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
        regions: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        for chunk in self.actions:
            region_file: Tuple[int, int] = World.get_region_coordinates(chunk)
            if region_file not in regions.keys():
                regions[region_file] = []
            regions[region_file].append(chunk)
        return regions

    def perform(self) -> None:
        """
        performs all set chunk backup restorations
        """
        for region, chunks in self._sort_actions_by_regions().items():
            target_region = Region(region, self.target_world)
            backup_region = Region(region, self.backup_world)
            for chunk in chunks:
                target_region.set_chunk(chunk, backup_region.get_chunk(chunk))
            target_region.flush()


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

    def get_chunk(self, chunk: Tuple[int, int]) -> Optional[bytes]:
        """
        reads the chunk data for the specified chunk from the region file
        :param chunk: the chunk to read
        :return: the (compressed) chunk data
        """
        loc = self.get_chunk_location(chunk)
        if loc is None:
            return None
        offset, sector_length = loc
        chunk_data = self.data[offset:offset + sector_length]
        return chunk_data

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
        offset, sector_length = loc
        # set chunk data
        self.data = self.data[:offset] + data + self.data[offset + sector_length:]
        sector_length = (ceil(len(data), 4096) // 4096).to_bytes(1, "big", signed=False)
        # set sector length
        self.data = self.data[:Region.get_offset_offset(chunk) + 3] + sector_length + self.data[Region.get_offset_offset(chunk) + 4:]

    def flush(self) -> None:
        """
        writes all changes to the region file
        """
        with open(self.world.get_region_file(self.region), "wb") as f:
            f.write(self.data)
        print(f"Wrote file {self.world.get_region_file(self.region)}")
