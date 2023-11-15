import carla
import io

# Read the .osm data
f = io.open("original-BorregasAve.osm", mode="r", encoding="utf-8")
osm_data = f.read()
f.close()

# Define the desired settings. In this case, default values.
settings = carla.Osm2OdrSettings()

settings.generate_traffic_lights = True
# settings.all_junctions_with_traffic_lights = True

# Set OSM road types to export to OpenDRIVE
settings.set_osm_way_types(["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential"])
# Convert to .xodr
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# save opendrive file
f = open("./original-BorregasAve.xodr", 'w')
f.write(xodr_data)
f.close()