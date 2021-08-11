import worldtools
import time
import random
"""

def squarerange(x):
    for i in range(x):
        for j in range(x):
            yield i, j


w = worldtools.World("D:\\data\\minecraft\\saves\\Target", enable_caching=True)

start_time = time.time()
for position in squarerange(16):
    w.get_chunk(position).get_heightmap(worldtools.HeightMap.HIGHEST_SOLID).get_blocks()
print(f"Took {(time.time() - start_time) * 1000} Milliseconds")


w = worldtools.World("D:\\data\\minecraft\\saves\\TEEST")
b = (18, 256, 52)
c = w.get_chunk_for_block(b)
print(c.generate_heightmap())
print(c.data)
"""

restorer = worldtools.ChunkRestorer("D:\\data\\minecraft\\saves\\server\\world", "D:\\data\\minecraft\\saves\\server\\backup")

for i in range(8):
    restorer.add_chunk((random.randint(-7, 7), random.randint(-7, 7)))

restorer.perform()
