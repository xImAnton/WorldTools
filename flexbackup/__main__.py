from flexbackup.world import ChunkRestorer


restorer = ChunkRestorer("D:\\data\\minecraft\\saves\\Wertvolle Welt", "D:\\data\\minecraft\\saves\\Backup")
restorer.add_chunk((-8, 8))
restorer.perform()
