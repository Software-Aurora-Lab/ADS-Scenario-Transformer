from openscenario_msgs import FileHeader
from scenario_transfer.builder import Builder


class FileHeaderBuilder(Builder):

    def __init__(self):
        pass

    def get_result(self) -> FileHeader:
        return FileHeader()
