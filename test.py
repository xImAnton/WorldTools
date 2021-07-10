import worldtools
import time


def squarerange(x):
    for i in range(x):
        for j in range(x):
            yield i, j


w = worldtools.World("D:\\data\\minecraft\\saves\\Target")

start_time = time.time()
for position in squarerange(8):
    w.get_chunk(position).get_heightmap(worldtools.HeightMap.HIGHEST_SOLID).get_blocks()
print(f"Took {(time.time() - start_time) * 1000} Milliseconds")


"""
w = worldtools.World("D:\\data\\minecraft\\saves\\TEEST")
b = (18, 256, 52)
c = w.get_chunk_for_block(b)
print(c.generate_heightmap())
print(c.data)

restorer = worldtools.ChunkRestorer("D:\\data\\minecraft\\saves\\Target", "D:\\data\\minecraft\\saves\\Backup")
restorer.add_chunk((0, 0))
restorer.perform()
"""
