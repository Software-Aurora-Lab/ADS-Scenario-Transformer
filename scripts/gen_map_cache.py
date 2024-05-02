import sys
import pickle
from ads_scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from modules.map.proto.map_pb2 import Map


def gen_map_cache(map_path, output_path):
    apollo_parser = ApolloMapParser(filepath=map_path)

    with open(output_path, 'wb') as f:
        pickle.dump(apollo_parser.get_map(), f)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gen_map_cache.py <map_path> <output_path>")
        sys.exit(1)
    map_path = sys.argv[1]
    output_path = sys.argv[2]
    gen_map_cache(map_path, output_path)
