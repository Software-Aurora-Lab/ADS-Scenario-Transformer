import pytest
from scenario_transfer.tools.apollo_map_parser import ApolloMapParser


def test_apollo_map_lane_to_utm(apollo_map_parser):

    (point1,
     heading1) = apollo_map_parser.get_coordinate_and_heading(
         lane_id="lane_26", s=26.2)
    assert point1.x == 586969.5290636807
    assert point1.y == 4141286.5458221673
    assert heading1 == -1.9883158777364047

    (point2,
     heading2) = apollo_map_parser.get_coordinate_and_heading(
         lane_id="lane_30", s=0.0)
    assert point2.x == 587040.39095115662
    assert point2.y == 4141553.0670471191
    assert heading2 == -1.807509475733681