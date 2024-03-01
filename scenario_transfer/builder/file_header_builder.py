from datetime import datetime
from typing import Dict, Optional
from openscenario_msgs import FileHeader
from scenario_transfer.builder import Builder


class FileHeaderBuilder(Builder):
    """
    - Check usage at test_builder.py
    
    message FileHeader {
        required uint32 revMajor = 1;                   // 1..1
        required uint32 revMinor = 2;                   // 1..1
        required string date = 3;                       // 1..1, YYYY-MM-DDThh:mm:ss
        required string description = 4;                // 1..1
        required string author = 5;                     // 1..1
    }
    """

    product: FileHeader

    def __init__(self, dict: Optional[Dict] = None):

        if dict:
            self.product = FileHeader(**dict)
        else:
            self.product = FileHeader(
                revMajor=1,
                revMinor=1,
                date=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                description="Default FileHeader",
                author="ADS Scenario Tranferer")

    def get_result(self) -> FileHeader:
        return self.product
