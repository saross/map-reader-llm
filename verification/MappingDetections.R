library(sf)
library(terra)
library(mapview)

# Load detected mound bboxes
detected <- read_sf("../outputs/results/detections-2025-12-11-3-pro.geojson") 

# Check if metadata is present?
detected
st_crs(detected) # SHOULD BE 32635

# Are we in BG?
mapview(detected)
 
# Check viewing of a single tile - skip for scaled up solution below
# unique(detected$source_tile)
# tile <- rast("../outputs/tiles/K-35-062-2_Rakovski/K-35-062-2_Rakovski_x1344_y0.png")
# map <- rast("../inputs/K-35-062-2_Rakovski.tif")
# mapview(tile) + mapview(detected, col.regions = "blue")


# View all the results
library(purrr)

# Get the unique tile names referenced by the detections
tiles <- unique(detected$source_tile)

# Get tiles directory path
tile_dir <- "../outputs/tiles/K-35-052-4_32635"

# Load rasters from tiles dir using filepaths
rasters <- map(
  tiles,
  ~ rast(file.path(tile_dir, .x))
)

# Check all is working
names(rasters) <- tiles
rasters[['K-35-052-4_32635_x0_y2688.png']]

# Match mound bboxes and source tiles
tile_name <- tiles[1]
r1 <- rasters[[tile_name]]

poly_r1 <- detected[detected$source_tile == tile_name, ]

# View mound bboxes over source tiles

# # Mapview renders the maps a bit too yellow
# mapview(r1) + mapview(poly_r1, col.regions = "blue")
# 
# # Plot is better colored, but not interactive
# plot(r1); plot(poly_r1$geometry, col = "white", add = T)


# FINAL Interactive view for all the tiles and associated detected mound bboxes
views <- imap(
  rasters,
  ~ mapview(.x) + 
    mapview(detected[detected$source_tile == .y, ], col.regions = "blue")
)

# Change the number in parentheses from 1- n to view the relevant tile 
# and associated mound bboxes
views[[5]]
