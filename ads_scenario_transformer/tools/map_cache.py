from typing import Optional
from ads_scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from ads_scenario_transformer.tools.vector_map_parser import VectorMapParser


class MapCache:
    apollo_map_parser: Optional[ApolloMapParser] = None
    vector_map_parser: Optional[VectorMapParser] = None

    @staticmethod
    def get_apollo_map_parser(apollo_hd_map_path: str) -> ApolloMapParser:
        if not MapCache.apollo_map_parser:
            MapCache.apollo_map_parser = ApolloMapParser(
                filepath=apollo_hd_map_path)
        return MapCache.apollo_map_parser

    @staticmethod
    def get_vector_map_parser(vector_map_path: str) -> VectorMapParser:
        if not MapCache.vector_map_parser:
            MapCache.vector_map_parser = VectorMapParser(
                vector_map_path=vector_map_path)
        return MapCache.vector_map_parser
