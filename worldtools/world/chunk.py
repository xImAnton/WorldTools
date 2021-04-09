from __future__ import annotations

from typing import Tuple, TYPE_CHECKING, List
from ..exceptions import ChunkNotFoundException, SectionNotPresentException
from ..nbt import NBTParser
from io import BytesIO
import zlib
import gzip
import numpy

if TYPE_CHECKING:
    from .region import Region


class Chunk:
    @staticmethod
    def decompress(data: bytes, method: int):
        if method == 1:
            data = gzip.decompress(data)
        elif method == 2:
            data = zlib.decompress(data)
        return data

    def __init__(self, chunk: Tuple[int, int], region: Region):
        self.chunk: Tuple[int, int] = chunk
        self.region: Region = region

        loc = region.get_chunk_location(chunk)
        if loc is None:
            raise ChunkNotFoundException(
                f"Chunk {chunk} is not present in Region File {self.region.world.get_region_file(self.region.region)}",
                chunk)
        offset, sector_length = loc
        data = BytesIO(self.region.data[offset:offset + sector_length])
        bytes_length = int.from_bytes(data.read(4), "big")
        compression_method = int.from_bytes(data.read(1), "big")

        self.data = NBTParser.parse(Chunk.decompress(data.read(bytes_length), compression_method), False)

    def get_section(self, y):
        for sec in range(len(self.data["Level"]["Sections"])):
            if self.data["Level"]["Sections"][sec]["Y"] == y:
                return ChunkSection(self, sec)
        raise SectionNotPresentException(f"Section y={y} is not present in chunk {self.chunk}", (self.chunk[0], y, self.chunk[1]))

    def generate_heightmap(self):
        heightmap = {}
        for i in range(16):
            for h in range(16):
                heightmap[(i, h)] = None
        for y in reversed(range(17)):
            try:
                s = self.get_section(y)
                # TODO: Think of algorith, finish
            except SectionNotPresentException:
                continue


class ChunkSection:
    def __init__(self, chunk: Chunk, index: int):
        self.chunk: Chunk = chunk
        self.index: int = index
        if "Palette" not in self.chunk.data["Level"]["Sections"][index].keys():
            raise SectionNotPresentException(f"Section y={index} is not present in chunk {self.chunk.chunk}", (self.chunk.chunk[0], index, self.chunk.chunk[1]))
        self.palette = self.chunk.data["Level"]["Sections"][index]["Palette"]
        self.block_states: BlockStates = BlockStates(self.chunk.data["Level"]["Sections"][index]["BlockStates"])

    def get_block(self, position: Tuple[int, int, int]):
        return self.palette[self.block_states.get_palette_index_for_block(position)]


class BlockStates:
    def __init__(self, state):
        self.states = BlockStates.longarray_to_palette_indices(state)

    def get_palette_index_for_block(self, position: Tuple[int, int, int]):
        position = position[1] * 256 + position[2] * 16 + position[0]
        return self.states[position]

    @staticmethod
    def longarray_to_palette_indices(long_array: List[int]) -> numpy.ndarray:
        """
        FUNCTION FROM https://github.com/overviewer/Minecraft-Overviewer/blob/86963c5de9b237baab3b7be5b017500075357b17/overviewer_core/world.py#L1222
        HUGE THANKS <3, I HAD NO IDEA HOW TO SOLVE THIS IN PYTHON

        converts a Python List of Longs to numpy array of shorts
        :param long_array: the longs array to convert
        :return: numpy array of BlockStates
        """
        bits_per_value = (len(long_array) * 64) / 4096
        if bits_per_value < 4 or 12 < bits_per_value:
            raise ValueError("error reading BlockStates")
        b = numpy.frombuffer(numpy.asarray(long_array, dtype=numpy.uint64), dtype=numpy.uint8)

        b = b.astype(numpy.uint16)
        if bits_per_value == 8:
            return b

        result = numpy.zeros((4096,), dtype=numpy.uint16)
        if bits_per_value == 4:
            result[0::2] = b & 0x0f
            result[1::2] = (b & 0xf0) >> 4
        elif bits_per_value == 5:
            result[0::8] = b[0::5] & 0x1f
            result[1::8] = ((b[1::5] & 0x03) << 3) | ((b[0::5] & 0xe0) >> 5)
            result[2::8] = (b[1::5] & 0x7c) >> 2
            result[3::8] = ((b[2::5] & 0x0f) << 1) | ((b[1::5] & 0x80) >> 7)
            result[4::8] = ((b[3::5] & 0x01) << 4) | ((b[2::5] & 0xf0) >> 4)
            result[5::8] = (b[3::5] & 0x3e) >> 1
            result[6::8] = ((b[4::5] & 0x07) << 2) | ((b[3::5] & 0xc0) >> 6)
            result[7::8] = (b[4::5] & 0xf8) >> 3
        elif bits_per_value == 6:
            result[0::4] = b[0::3] & 0x3f
            result[1::4] = ((b[1::3] & 0x0f) << 2) | ((b[0::3] & 0xc0) >> 6)
            result[2::4] = ((b[2::3] & 0x03) << 4) | ((b[1::3] & 0xf0) >> 4)
            result[3::4] = (b[2::3] & 0xfc) >> 2
        elif bits_per_value == 7:
            result[0::8] = b[0::7] & 0x7f
            result[1::8] = ((b[1::7] & 0x3f) << 1) | ((b[0::7] & 0x80) >> 7)
            result[2::8] = ((b[2::7] & 0x1f) << 2) | ((b[1::7] & 0xc0) >> 6)
            result[3::8] = ((b[3::7] & 0x0f) << 3) | ((b[2::7] & 0xe0) >> 5)
            result[4::8] = ((b[4::7] & 0x07) << 4) | ((b[3::7] & 0xf0) >> 4)
            result[5::8] = ((b[5::7] & 0x03) << 5) | ((b[4::7] & 0xf8) >> 3)
            result[6::8] = ((b[6::7] & 0x01) << 6) | ((b[5::7] & 0xfc) >> 2)
            result[7::8] = (b[6::7] & 0xfe) >> 1
        # bits_per_value == 8 is handled above
        elif bits_per_value == 9:
            result[0::8] = ((b[1::9] & 0x01) << 8) | b[0::9]
            result[1::8] = ((b[2::9] & 0x03) << 7) | ((b[1::9] & 0xfe) >> 1)
            result[2::8] = ((b[3::9] & 0x07) << 6) | ((b[2::9] & 0xfc) >> 2)
            result[3::8] = ((b[4::9] & 0x0f) << 5) | ((b[3::9] & 0xf8) >> 3)
            result[4::8] = ((b[5::9] & 0x1f) << 4) | ((b[4::9] & 0xf0) >> 4)
            result[5::8] = ((b[6::9] & 0x3f) << 3) | ((b[5::9] & 0xe0) >> 5)
            result[6::8] = ((b[7::9] & 0x7f) << 2) | ((b[6::9] & 0xc0) >> 6)
            result[7::8] = (b[8::9] << 1) | ((b[7::9] & 0x80) >> 7)
        elif bits_per_value == 10:
            result[0::4] = ((b[1::5] & 0x03) << 8) | b[0::5]
            result[1::4] = ((b[2::5] & 0x0f) << 6) | ((b[1::5] & 0xfc) >> 2)
            result[2::4] = ((b[3::5] & 0x3f) << 4) | ((b[2::5] & 0xf0) >> 4)
            result[3::4] = (b[4::5] << 2) | ((b[3::5] & 0xc0) >> 6)
        elif bits_per_value == 11:
            result[0::8] = ((b[1::11] & 0x07) << 8) | b[0::11]
            result[1::8] = ((b[2::11] & 0x3f) << 5) | ((b[1::11] & 0xf8) >> 3)
            result[2::8] = ((b[4::11] & 0x01) << 10) | (b[3::11] << 2) | ((b[2::11] & 0xc0) >> 6)
            result[3::8] = ((b[5::11] & 0x0f) << 7) | ((b[4::11] & 0xfe) >> 1)
            result[4::8] = ((b[6::11] & 0x7f) << 4) | ((b[5::11] & 0xf0) >> 4)
            result[5::8] = ((b[8::11] & 0x03) << 9) | (b[7::11] << 1) | ((b[6::11] & 0x80) >> 7)
            result[6::8] = ((b[9::11] & 0x1f) << 2) | ((b[8::11] & 0xfc) >> 2)
            result[7::8] = (b[10::11] << 3) | ((b[9::11] & 0xe0) >> 5)
        elif bits_per_value == 12:
            result[0::2] = ((b[1::3] & 0x0f) << 8) | b[0::3]
            result[1::2] = (b[2::3] << 4) | ((b[1::3] & 0xf0) >> 4)

        return result
