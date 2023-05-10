import os, sys
import argparse
from pathlib import Path

from crdesigner.map_conversion.map_conversion_interface import opendrive_to_commonroad

from lxml import etree
from commonroad.common.file_reader import CommonRoadFileReader
from crdesigner.map_conversion.lanelet2.cr2lanelet import CR2LaneletConverter
from crdesigner.map_conversion.map_conversion_interface import commonroad_to_lanelet

from commonroad.scenario.scenario import Tag
from commonroad.common.file_writer import CommonRoadFileWriter, OverwriteExistingFile
from commonroad.planning.planning_problem import PlanningProblemSet
from crdesigner.map_conversion.opendrive.opendrive_parser.parser import parse_opendrive
from crdesigner.map_conversion.opendrive.opendrive_conversion.network import Network
from crdesigner.configurations.get_configs import get_configs

def odr_to_lanelet2(odrPath, fileName):
    opendriveFilePath = odrPath
    lanelet2Path = Path.cwd() / f"{fileName}-lanelet2.osm"
    CRPath = Path.cwd() / f"{fileName}.xml"
    scenario = None
    try:
        scenario = opendrive_to_commonroad(str(opendriveFilePath))
    except Exception as exception:
        print(f"Fail to convert opendrive to commonroad {opendriveFilePath}")
        print(f"exception {exception}")
        pass

    proj = ""
    config = get_configs()

    if not scenario:
        return
    
    writer = CommonRoadFileWriter(
                scenario=scenario,
                planning_problem_set=PlanningProblemSet(),
                author=config.file_header.author,
                affiliation=config.file_header.affiliation,
                source=config.file_header.source,
                tags={Tag.URBAN},
            )
    writer.write_to_file(CRPath, OverwriteExistingFile.ALWAYS)
    try:
        commonroad_to_lanelet(CRPath, lanelet2Path, proj)
    except Exception:
        print(f"Fail to convert commonroad to lanelet2 {opendriveFilePath}")
        pass

def odr_to_apollo(dirPath, fileName):
    opendriveFilePath = dirPath / f"{fileName}.xodr"
    apolloPath = dirPath / f"{fileName}.txt"

    try:
        os.system(f"imap -d -f -i {opendriveFilePath} -o {apolloPath}")
    except Exception:
        print(f"Fail to convert opendrive to apollo {opendriveFilePath}")
        return
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "")
    parser.add_argument('-d','--xodr', help='xodr path', required=True)

    args = parser.parse_args()
    
    if args.xodr:
        odrPath = Path(args.xodr)
        fileName = odrPath.stem
        
        odr_to_lanelet2(odrPath = odrPath, fileName=fileName)
        