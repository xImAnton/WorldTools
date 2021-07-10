from typing import List, Tuple, Dict
from ..world.world import World
from ..world.region import Region


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
                target_region.set_chunk(chunk, backup_region.get_raw_chunk(chunk))
            target_region.flush()
