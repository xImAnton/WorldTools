class ChunkNotFoundException(Exception):
    """
    raised when a mentioned chunk is not present in the current world
    """
    def __init__(self, msg, chunk):
        super(ChunkNotFoundException, self).__init__(msg)
        self.chunk = chunk
