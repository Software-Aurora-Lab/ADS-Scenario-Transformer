import lanelet2

dir = "4552b7ac-4fba-4420-88b8-ae14289bf5ac"
filename = "BorregasAve"
origin = lanelet2.io.Origin(37.400,-122.023)

map = lanelet2.io.load(f"./{dir}/{filename}.osm", origin)

outputfile = f"{filename}-lanelet2.osm"
lanelet2.io.write(outputfile, map, origin)

