#!/usr/bin/env python
"""
Find tile and edge details for reference features.

For each of fids 399, 99, 15: load their coordinates from reference geojsons,
find which calibration tile(s) they intersect, and calculate distance to each
edge (N/S/E/W) of the tile polygon.
"""

import json
import math
from pathlib import Path
from glob import glob

import shapely.geometry


def distance_point_to_edge(point_coords: tuple, edge_coords: tuple) -> float:
    """
    Calculate perpendicular distance from a point to a line segment (edge).
    
    Args:
        point_coords: (lon, lat) tuple
        edge_coords: ((lon1, lat1), (lon2, lat2)) tuple for edge endpoints
    
    Returns:
        Distance in degrees
    """
    x0, y0 = point_coords
    (x1, y1), (x2, y2) = edge_coords
    
    # Vector from start to end of edge
    edge_len_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
    
    if edge_len_sq == 0:
        # Edge is a point, return distance to that point
        return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
    
    # Project point onto line, clamped to segment
    t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / edge_len_sq))
    
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    
    return math.sqrt((x0 - proj_x) ** 2 + (y0 - proj_y) ** 2)


def get_tile_edges(tile_coords: list) -> dict:
    """
    Extract N, S, E, W edges from a tile polygon.
    
    Args:
        tile_coords: List of [lon, lat] coordinates forming the polygon
    
    Returns:
        Dictionary with 'N', 'S', 'E', 'W' keys, each containing edge coordinates
    """
    # Find bounding values
    lons = [c[0] for c in tile_coords]
    lats = [c[1] for c in tile_coords]
    
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    
    # North edge (highest lat)
    north_coords = [(c[0], c[1]) for c in tile_coords if abs(c[1] - max_lat) < 1e-6]
    north_edge = (min(north_coords), max(north_coords))
    
    # South edge (lowest lat)
    south_coords = [(c[0], c[1]) for c in tile_coords if abs(c[1] - min_lat) < 1e-6]
    south_edge = (min(south_coords), max(south_coords))
    
    # East edge (highest lon)
    east_coords = [(c[0], c[1]) for c in tile_coords if abs(c[0] - max_lon) < 1e-6]
    east_edge = (min(east_coords, key=lambda c: c[1]), max(east_coords, key=lambda c: c[1]))
    
    # West edge (lowest lon)
    west_coords = [(c[0], c[1]) for c in tile_coords if abs(c[0] - min_lon) < 1e-6]
    west_edge = (min(west_coords, key=lambda c: c[1]), max(west_coords, key=lambda c: c[1]))
    
    return {
        'N': north_edge,
        'S': south_edge,
        'E': east_edge,
        'W': west_edge,
    }


def extract_point_from_geometry(geom_dict):
    """Extract a single point coordinate from various geometry types."""
    geom_type = geom_dict['type']
    coords = geom_dict['coordinates']
    
    if geom_type == 'Point':
        return tuple(coords)
    elif geom_type == 'MultiPoint':
        # Use first point from MultiPoint
        return tuple(coords[0]) if coords else None
    else:
        return None


def main():
    base_path = Path('/home/shawn/Code/map-reader-llm')
    
    # Load calibration bounds
    cal_bounds_path = base_path / 'inputs/vectors/bounds/calibration_bounds.geojson'
    with open(cal_bounds_path) as f:
        cal_bounds = json.load(f)
    
    # Load all reference files
    ref_files = sorted(glob(str(base_path / 'inputs/vectors/references/reference_*.geojson')))
    
    # Collect all references by fid
    references = {}
    for ref_file in ref_files:
        with open(ref_file) as f:
            ref_data = json.load(f)
        
        for feature in ref_data.get('features', []):
            fid = feature['properties'].get('fid')
            if fid in [399, 99, 15]:
                references[fid] = feature
    
    # Process each target fid
    target_fids = [399, 99, 15]
    
    for fid in target_fids:
        if fid not in references:
            print(f"\nFID {fid}: NOT FOUND")
            continue
        
        ref_feature = references[fid]
        ref_coords = extract_point_from_geometry(ref_feature['geometry'])
        
        if not ref_coords:
            print(f"\nFID {fid}: Could not extract coordinates")
            continue
        
        print(f"\n{'='*70}")
        print(f"FID {fid}")
        print(f"{'='*70}")
        print(f"Reference coordinates (lon, lat): {ref_coords}")
        
        # Find intersecting tiles
        ref_point = shapely.geometry.Point(ref_coords)
        intersecting_tiles = []
        
        for tile_feature in cal_bounds['features']:
            tile_geom = shapely.geometry.shape(tile_feature['geometry'])
            if tile_geom.intersects(ref_point):
                intersecting_tiles.append(tile_feature)
        
        if not intersecting_tiles:
            print("No intersecting calibration tiles found")
            continue
        
        print(f"Intersecting tiles: {len(intersecting_tiles)}")
        
        for tile_feature in intersecting_tiles:
            tile_props = tile_feature['properties']
            tile_filename = tile_props.get('tile_name', 'unknown')
            
            tile_geom = shapely.geometry.shape(tile_feature['geometry'])
            tile_coords = list(tile_geom.exterior.coords[:-1])  # Remove duplicate last coord
            
            edges = get_tile_edges(tile_coords)
            
            # Calculate distances to each edge
            distances = {}
            for direction in ['N', 'S', 'E', 'W']:
                dist = distance_point_to_edge(ref_coords, edges[direction])
                distances[direction] = dist
            
            # Find closest edge
            closest_edge = min(distances, key=distances.get)
            
            print(f"\n  Tile: {tile_filename}")
            print(f"    Distance to North: {distances['N']:.6f}°")
            print(f"    Distance to South: {distances['S']:.6f}°")
            print(f"    Distance to East:  {distances['E']:.6f}°")
            print(f"    Distance to West:  {distances['W']:.6f}°")
            print(f"    Closest edge: {closest_edge} ({distances[closest_edge]:.6f}°)")


if __name__ == '__main__':
    main()
