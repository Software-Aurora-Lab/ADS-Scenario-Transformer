import os
import xml.etree.ElementTree as ET


class OpenScenarioAttributesNameMapper:

    def parse_definition(self):

        current_file_path = os.path.abspath(__file__)
        parent_directory = os.path.dirname(current_file_path)

        definition_path = parent_directory + "/openscenario_definition.xml"
        
        tree = ET.parse(definition_path)
        root = tree.getroot()

        res_dict = {}
        for child in root:
            if "name" in child.attrib:
                key = child.attrib["name"]
                res_dict[key] = []

                for decendant in child:
                    for ele in decendant:
                        if "name" in ele.attrib:
                            res_dict[key].append(ele.attrib["name"])

                    if "name" in decendant.attrib:
                        res_dict[key].append(decendant.attrib["name"])

        return res_dict