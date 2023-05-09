import lanelet2
from lanelet2.projection import (UtmProjector, MercatorProjector,
                                 LocalCartesianProjector, GeocentricProjector)

dir = "4552b7ac-4fba-4420-88b8-ae14289bf5ac"
filename = "BorregasAve"
origin = lanelet2.io.Origin(37.4168652058464,-122.015518188366)

projector = UtmProjector(origin)

# map = lanelet2.io.load(f"./{dir}/{filename}.osm", origin)
map = lanelet2.io.load(f"./{dir}/{filename}.osm", projector)

outputfile = f"{filename}-lanelet2.osm"
write_errors = lanelet2.io.writeRobust(outputfile, map, projector)
print(write_errors)

# lanelet2.io.write(outputfile, map, origin)

