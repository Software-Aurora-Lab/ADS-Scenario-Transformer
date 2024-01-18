from enum import Enum
from pathlib import Path

from apollo_msgs import Map


class ApolloMapIOHandler:
    """
    MapIOHandler is a class that handles 
    1. the loading of the map from the binary
    2. the saving of the map to the file
    """

    class FileFormat(Enum):
        PICKLE = ".pickle"
        TEXT = ".txt"

    def load_map(self, map_path: str) -> Map:
        map_path = map_path
        map = Map()
        with open(map_path, 'rb') as file:
            map.ParseFromString(file.read())
        return map

    def write_map(self, map_path: str, format: FileFormat):
        map = self.load_map(map_path)

        output_path = Path(map_path).with_suffix(format.value)

        if format == MapIOManager.FileFormat.PICKLE:
            with open(output_path, 'wb') as file:
                pickle.dump(map, file)
        elif format == MapIOManager.FileFormat.TEXT:
            with open(output_path, 'w') as file:
                file.write(str(map))

        print(f"Map object has been saved to {output_path}")
