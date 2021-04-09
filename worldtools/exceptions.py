from typing import Tuple


class ChunkNotFoundException(Exception):
    """
    raised when a mentioned chunk is not present in the current world
    """
    def __init__(self, msg, chunk: Tuple[int, int]):
        super(ChunkNotFoundException, self).__init__(msg)
        self.chunk: Tuple[int, int] = chunk


class SectionNotPresentException(Exception):
    def __init__(self, msg, section: Tuple[int, int, int]):
        super(SectionNotPresentException, self).__init__(msg)
        self.section: Tuple[int, int, int] = section
