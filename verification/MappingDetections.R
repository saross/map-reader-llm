library(sf)
library(terra)
library(mapview)

detected <- read_sf("../outputs/test_detections.geojson") 
st_crs(detected) <- 32635
mapview(detected)

tile <- rast("../outputs/tiles/K-35-062-2_Rakovski/K-35-062-2_Rakovski_x1344_y0.png")
map <- rast("../inputs/K-35-062-2_Rakovski.tif")

mapview(tile) + mapview(detected, col.regions = "blue")

plot(map)
plot()