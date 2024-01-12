# Original source code from https://github.com/Software-Aurora-Lab/scenoRITA-7.0/tree/786937f82bc936691640fb5616ceccbb497891a7/src/mylib/kdtree
"""modules/common/math/aaboxkdtree2d.h"""

from dataclasses import dataclass


@dataclass
class KDTreeParams:
    # The maximum depth of the kdtree.
    max_depth: int = -1
    # The maximum number of items in one leaf node.
    max_leaf_size: int = -1
    # The maximum dimension  size of leaf node.
    max_leaf_dimension: float = -1.0