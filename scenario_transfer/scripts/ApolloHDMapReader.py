import argparse
from pathlib import Path

from apollo_msgs import Map


class ApolloHDMapReader:
    """
    Create parsed Apollo HD map file.

    Usage: poetry run python3 -m scenario_transfer.scripts.ApolloHDMapReader ./samples/map/BorregasAve/base_map.bin

    """

    def parse_binary_to_txt(self, source_path: str):

        map_path = source_path  # "./samples/map/BorregasAve/base_map.bin"
        map = Map()
        with open(map_path, 'rb') as file:
            map.ParseFromString(file.read())

        output_path = Path(source_path).with_suffix('.txt')
        with open(output_path, 'w') as file:
            file.write(str(map))

        print("Result file at:", output_path.resolve())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('sourcepath', help='Input file path')

    args = parser.parse_args()
    reader = ApolloHDMapReader()
    reader.parse_binary_to_txt(source_path=args.sourcepath)


if __name__ == '__main__':
    main()
