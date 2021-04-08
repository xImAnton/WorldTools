from flexbackup.backup import ChunkRestorer


restorer = ChunkRestorer("D:\\data\\minecraft\\saves\\Wertvolle Welt", "D:\\data\\minecraft\\saves\\Backup")
restorer.add_chunk((-10, 8))
restorer.perform()
