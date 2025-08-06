"""
Tile Extractors Module
Contains MBTiles extraction implementation
"""

import os
import sqlite3
import math
import io
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from abc import ABC, abstractmethod
from PIL import Image, ImageDraw


class CoordinateConverter:
    """Handles coordinate transformations between lat/lon and tile coordinates"""
    
    @staticmethod
    def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """Convert lat/lon to tile coordinates"""
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return xtile, ytile
    
    @staticmethod
    def bbox_to_tile_range(bbox: List[float], zoom: int) -> Tuple[int, int, int, int]:
        """Convert bounding box to tile range"""
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Get tile coordinates for corners
        min_x, max_y = CoordinateConverter.lat_lon_to_tile(min_lat, min_lon, zoom)
        max_x, min_y = CoordinateConverter.lat_lon_to_tile(max_lat, max_lon, zoom)
        
        return min_x, max_x, min_y, max_y
    
    @staticmethod
    def bbox_to_tile_range_tms(bbox: List[float], zoom: int) -> Tuple[int, int, int, int]:
        """Convert bounding box to tile range for TMS coordinates"""
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Get tile coordinates for corners (XYZ)
        min_x, max_y = CoordinateConverter.lat_lon_to_tile(min_lat, min_lon, zoom)
        max_x, min_y = CoordinateConverter.lat_lon_to_tile(max_lat, max_lon, zoom)
        
        # Convert Y coordinates to TMS
        tms_min_y = (2 ** zoom - 1) - max_y
        tms_max_y = (2 ** zoom - 1) - min_y
        
        return min_x, max_x, tms_min_y, tms_max_y
    
    @staticmethod
    def tile_to_bbox(x: int, y: int, zoom: int) -> List[float]:
        """Convert tile coordinates to bounding box"""
        n = 2.0 ** zoom
        lon_west = x / n * 360.0 - 180.0
        lon_east = (x + 1) / n * 360.0 - 180.0
        lat_north = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
        lat_south = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
        return [lon_west, lat_south, lon_east, lat_north]


class SourceTypeDetector:
    """Detects the type of source file"""
    
    @staticmethod
    def detect(source_path: str) -> str:
        """Detect the type of source file"""
        path = Path(source_path)
        
        if not path.exists():
            return "unknown"
        
        # Check file extension
        suffix = path.suffix.lower()
        
        if suffix == '.mbtiles':
            return "mbtiles"
        else:
            return "unknown"


class TileExtractor(ABC):
    """Abstract base class for tile extractors"""
    
    def __init__(self, source_path: str):
        self.source_path = source_path
    
    @abstractmethod
    def extract_tiles(self, bbox: List[float], zoom: int) -> List[Tuple[int, int, Any]]:
        """Extract tiles for a specific region and zoom level"""
        pass


class MBTilesExtractor(TileExtractor):
    """Extracts tiles from MBTiles files"""
    
    def extract_tiles(self, bbox: List[float], zoom: int) -> List[Tuple[int, int, bytes]]:
        """Get tiles from MBTiles file for a specific zoom level"""
        tiles = []
        
        try:
            with sqlite3.connect(self.source_path) as conn:
                cursor = conn.cursor()
                
                # Get tile range for this zoom level (TMS coordinates)
                min_x, max_x, min_y, max_y = CoordinateConverter.bbox_to_tile_range_tms(bbox, zoom)
                
                # Query tiles
                cursor.execute("""
                    SELECT tile_column, tile_row, tile_data 
                    FROM tiles 
                    WHERE zoom_level = ? AND tile_column BETWEEN ? AND ? AND tile_row BETWEEN ? AND ?
                """, (zoom, min_x, max_x, min_y, max_y))
                
                for row in cursor.fetchall():
                    tile_column, tile_row, tile_data = row
                    # Convert TMS y coordinate to XYZ (flip y coordinate)
                    xyz_y = (2 ** zoom - 1) - tile_row
                    tiles.append((tile_column, xyz_y, tile_data))
        
        except Exception as e:
            print(f"Error reading MBTiles file {self.source_path}: {e}")
        
        return tiles


class TileExtractorFactory:
    """Factory for creating tile extractors based on source type"""
    
    _extractors = {
        'mbtiles': MBTilesExtractor
    }
    
    @classmethod
    def create_extractor(cls, source_type: str, source_path: str) -> Optional[TileExtractor]:
        """Create appropriate extractor for source type"""
        extractor_class = cls._extractors.get(source_type)
        return extractor_class(source_path) if extractor_class else None 