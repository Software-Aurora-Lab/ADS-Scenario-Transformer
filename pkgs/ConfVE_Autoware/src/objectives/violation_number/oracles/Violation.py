from dataclasses import dataclass
from typing import Dict


@dataclass
class Violation:
    main_type: str
    features: Dict
    key_label: str
