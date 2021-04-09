from __future__ import annotations

from typing import Optional, Type
from struct import unpack
from io import BytesIO


class NBTBase:
    """
    Interface for all NBT Components

    Documentation:
      - https://minecraft.fandom.com/wiki/NBT_format
    """
    DATATYPE_ID = -1

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        """
        Unpacks the current NBT Component Type from the passed stream
        :param data: the byte stream to read from
        :return: a instance of the current NBT Component
        """
        pass

    def pack(self) -> bytes:
        """
        Packs the current Component to binary data
        :return: the packed bytes
        """
        return b'\x00'

    @staticmethod
    def get_type(i: int) -> Optional[Type[NBTBase]]:
        """
        Searches for a NBT type with the specified ID
        :param i: the id to find the Type for
        :return: the NBT Component class if one could be found, else None
        """
        for t in NBTBase.__subclasses__():
            if t.DATATYPE_ID == i:
                return t
        return None


class End(NBTBase):
    """
    Type used for indicating the End of a NBT Compound
    Is sometimes used to fill Empty Lists
    """
    DATATYPE_ID = 0

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        return End()


class Byte(NBTBase, int):
    """
    Represents a single Byte
    """
    DATATYPE_ID = 1

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        return Byte(int.from_bytes(data.read(1), "big", signed=True))


class Short(int, NBTBase):
    """
    Represents a Short (2 bytes, Signed)
    """
    DATATYPE_ID = 2

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        return Short(unpack(">h", data.read(2))[0])


class Int(int, NBTBase):
    """
    Represents an Integer (4 Bytes, Signed)
    """
    DATATYPE_ID = 3

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        return Int(unpack(">i", data.read(4))[0])


class Long(int, NBTBase):
    """
    Represents a Long (8 Bytes, Signed)
    """
    DATATYPE_ID = 4

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        return Long(unpack(">q", data.read(8))[0])


class Float(float, NBTBase):
    """
    Represents a 4 byte floating point number (IEEE 754-2008)
    """
    DATATYPE_ID = 5

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        return Float(unpack(">f", data.read(4))[0])


class Double(float, NBTBase):
    """
    Represents a 8 byte floating point number (IEEE 754-2008)
    """
    DATATYPE_ID = 6

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        return Double(unpack(">d", data.read(8))[0])


class ByteArray(list, NBTBase):
    """
    Represents an Array of Bytes
    """
    DATATYPE_ID = 7

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        length = Int.unpack(data)
        return ByteArray(bytearray(data.read(length)))


class String(str, NBTBase):
    """
    Represents a simple UTF-8 String
    """
    DATATYPE_ID = 8

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        length = unpack(">h", data.read(2))[0]
        return String(data.read(length).decode("utf-8"))


class List(list, NBTBase):
    """
    Represents a List of other NBT Types
    """
    DATATYPE_ID = 9

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        datatype = NBTBase.get_type(Byte.unpack(data))
        if datatype is None:
            return List([])
        length = Int.unpack(data)
        ls = []
        for i in range(length):
            ls.append(datatype.unpack(data))
        return List(ls)


class Compound(dict, NBTBase):
    """
    Represents a mapping from String Keys to NBT Types
    """
    DATATYPE_ID = 10

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        out = {}
        while True:
            type_id = Byte.unpack(data)
            if type_id == 0:
                break
            name = String.unpack(data)
            item = NBTBase.get_type(type_id).unpack(data)
            out[name] = item
        return Compound(out)


class IntArray(list, NBTBase):
    """
    Represents an Array of Integers
    """
    DATATYPE_ID = 11

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        length = Int.unpack(data)
        out = []
        for i in range(length):
            out.append(Int.unpack(data))
        return IntArray(out)


class LongArray(list, NBTBase):
    """
    Represents an Array of Longs
    """
    DATATYPE_ID = 12

    @staticmethod
    def unpack(data: BytesIO) -> NBTBase:
        length = Int.unpack(data)
        out = []
        for i in range(length):
            out.append(Long.unpack(data))
        return IntArray(out)
