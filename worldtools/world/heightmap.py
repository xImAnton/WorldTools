from __future__ import annotations
from typing import TYPE_CHECKING
from ..exceptions import HeightmapNotFoundException

if TYPE_CHECKING:
    from .chunk import Chunk


class HeightMap:
    MOTION_BLOCKING = "MOTION_BLOCKING"
    MOTION_BLOCKING_NO_LEAVES = "MOTION_BLOCKING_NO_LEAVES"
    HIGHEST_SOLID = "OCEAN_FLOOR"
    HIGHEST_NONAIR = "WORLD_SURFACE"

    def __init__(self, chunk: Chunk, type_: str):
        self.chunk: Chunk = chunk
        self.type: str = type_
        self.map = [[0 for _ in range(16)] for _ in range(16)]
        try:
            raw = self.chunk.data["Level"]["Heightmaps"][self.type]
        except KeyError:
            raise HeightmapNotFoundException(self.type, chunk.chunk)
        block = 0
        for long in raw:
            while long:
                self.map[block % 16][block // 16] = (long & 0x1FF) - 1
                long >>= 9
                block += 1

    def get_blocks(self):
        section_cache = [None for _ in range(16)]

        out = [[] for _ in range(16)]
        for x in range(16):
            for z in range(16):
                y = self.map[x][z]
                section_index = y // 16
                if not section_cache[section_index]:
                    section_cache[section_index] = self.chunk.get_section(section_index)
                out[x].append(section_cache[section_index].get_block((x, y % 16, z)))
        return out
