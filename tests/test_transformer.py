import unittest
import pytest

from apollo_msgs import PointENU
from openscenario_msgs import LanePosition

from scenario_transfer import PointENUTransformer

@pytest.mark.universal
class TestTransformer(unittest.TestCase):
    def test_transform(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        t = PointENUTransformer()
        res = t.transform(source = point)


if __name__ == '__main__':
    unittest.main()