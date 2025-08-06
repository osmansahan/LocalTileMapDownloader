"""
Tile Writer Module
Handles writing tiles to filesystem with comprehensive error handling
"""

import os
import shutil
import json
import logging
from typing import List, Tuple, Dict, Any, Optional
from tqdm import tqdm
from pathlib import Path


class TileWriter:
    """Handles writing tiles to filesystem with comprehensive error handling"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.logger = self._setup_logger()
        
        # Desteklenen dosya formatları
        self.supported_formats = {
            'mbtiles': ['.pbf', '.jpg', '.jpeg', '.png']
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for tile writer"""
        logger = logging.getLogger('TileWriter')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def write_tiles(self, tiles_by_zoom: Dict[int, List[Tuple[int, int, Any]]], 
                   region_name: str, source_type: str) -> int:
        """Write tiles to filesystem with error handling"""
        total_tiles = 0
        failed_tiles = 0
        
        try:
            region_dir = os.path.join(self.output_dir, region_name)
            os.makedirs(region_dir, exist_ok=True)
            
            for zoom, tiles in tiles_by_zoom.items():
                if not tiles:
                    self.logger.warning(f"Zoom {zoom} için tile bulunamadı")
                    continue
                
                print(f"\nProcessing zoom {zoom}...")
                
                zoom_dir = os.path.join(region_dir, str(zoom))
                os.makedirs(zoom_dir, exist_ok=True)
                
                pbar = tqdm(tiles, desc=f"Zoom {zoom}", unit="tiles")
                
                for tile_info in pbar:
                    try:
                        tile_column, tile_row, tile_data = tile_info
                        
                        x_dir = os.path.join(zoom_dir, str(tile_column))
                        os.makedirs(x_dir, exist_ok=True)
                        
                        if self._write_single_tile(x_dir, tile_row, tile_data, source_type):
                            total_tiles += 1
                        else:
                            failed_tiles += 1
                            
                    except Exception as e:
                        self.logger.error(f"Tile yazma hatası: {e}")
                        failed_tiles += 1
                        continue
            
            # Create tile index after writing tiles
            self.create_tile_index(region_name, tiles_by_zoom.keys())
            
            if failed_tiles > 0:
                self.logger.warning(f"{failed_tiles} tile yazılamadı")
            
            return total_tiles
            
        except Exception as e:
            self.logger.error(f"Tile yazma işlemi başarısız: {e}")
            return 0
    
    def _write_single_tile(self, x_dir: str, tile_row: int, tile_data: Any, source_type: str) -> bool:
        """Write a single tile with proper error handling"""
        try:
            # Write binary data
            extension = self._get_extension_for_source_type(source_type)
            tile_path = os.path.join(x_dir, f"{tile_row}.{extension}")
            
            # Ensure tile_data is bytes
            if isinstance(tile_data, str):
                tile_data = tile_data.encode('utf-8')
            elif not isinstance(tile_data, bytes):
                self.logger.warning(f"Geçersiz tile veri tipi: {type(tile_data)}")
                return False
            
            with open(tile_path, 'wb') as f:
                f.write(tile_data)
            return True
                
        except Exception as e:
            self.logger.error(f"Tekil tile yazma hatası: {e}")
            return False
    
    def _get_extension_for_source_type(self, source_type: str) -> str:
        """Get appropriate file extension for source type"""
        extension_map = {
            'mbtiles': 'jpg'  # Default for MBTiles
        }
        return extension_map.get(source_type, 'jpg')
    
    def create_directory_structure(self, region_name: str, zoom_levels: List[int]) -> None:
        """Create directory structure for tiles"""
        try:
            region_dir = os.path.join(self.output_dir, region_name)
            os.makedirs(region_dir, exist_ok=True)
            
            for zoom in zoom_levels:
                zoom_dir = os.path.join(region_dir, str(zoom))
                os.makedirs(zoom_dir, exist_ok=True)
                
        except Exception as e:
            self.logger.error(f"Dizin yapısı oluşturma hatası: {e}")
    
    def get_output_path(self, region_name: str, zoom: int, x: int, y: int, extension: str) -> str:
        """Get the output path for a specific tile"""
        return os.path.join(self.output_dir, region_name, str(zoom), str(x), f"{y}.{extension}")
    
    def create_tile_index(self, region_name: str, zoom_levels) -> None:
        """Create JSON index of available tiles with error handling"""
        try:
            region_dir = os.path.join(self.output_dir, region_name)
            
            for zoom in zoom_levels:
                zoom_dir = os.path.join(region_dir, str(zoom))
                if not os.path.exists(zoom_dir):
                    continue
                    
                tiles = []
                for x_dir in os.listdir(zoom_dir):
                    x_path = os.path.join(zoom_dir, x_dir)
                    if os.path.isdir(x_path):
                        try:
                            x = int(x_dir)
                            for file in os.listdir(x_path):
                                if any(file.endswith(ext) for ext in 
                                       self.supported_formats['mbtiles']):
                                    y = int(file.split('.')[0])
                                    tiles.append({'x': x, 'y': y})
                        except ValueError:
                            self.logger.warning(f"Geçersiz dizin adı: {x_dir}")
                            continue
                
                if tiles:
                    index_path = os.path.join(zoom_dir, 'tiles.json')
                    with open(index_path, 'w', encoding='utf-8') as f:
                        json.dump({
                            'zoom': zoom, 
                            'tiles': tiles,
                            'total_tiles': len(tiles)
                        }, f, indent=2, ensure_ascii=False)
                        
        except Exception as e:
            self.logger.error(f"Tile indeksi oluşturma hatası: {e}")
    

    
    def get_tile_statistics(self, region_name: str) -> Dict[str, Any]:
        """Get statistics about written tiles"""
        try:
            region_dir = os.path.join(self.output_dir, region_name)
            if not os.path.exists(region_dir):
                return {}
            
            stats = {
                'region': region_name,
                'total_zoom_levels': 0,
                'total_tiles': 0,
                'zoom_levels': {},
                'file_formats': {}
            }
            
            for item in os.listdir(region_dir):
                item_path = os.path.join(region_dir, item)
                if os.path.isdir(item_path) and item.isdigit():
                    zoom = int(item)
                    stats['total_zoom_levels'] += 1
                    
                    zoom_stats = self._get_zoom_statistics(item_path)
                    stats['zoom_levels'][zoom] = zoom_stats
                    stats['total_tiles'] += zoom_stats['tiles']
                    
                    # Format istatistikleri
                    for fmt, count in zoom_stats['formats'].items():
                        stats['file_formats'][fmt] = stats['file_formats'].get(fmt, 0) + count
            
            return stats
            
        except Exception as e:
            self.logger.error(f"İstatistik alma hatası: {e}")
            return {}
    
    def _get_zoom_statistics(self, zoom_dir: str) -> Dict[str, Any]:
        """Get statistics for a specific zoom level"""
        stats = {
            'tiles': 0,
            'formats': {},
            'x_range': {'min': None, 'max': None},
            'y_range': {'min': None, 'max': None}
        }
        
        try:
            for x_dir in os.listdir(zoom_dir):
                x_path = os.path.join(zoom_dir, x_dir)
                if os.path.isdir(x_path):
                    x = int(x_dir)
                    
                    # X aralığını güncelle
                    if stats['x_range']['min'] is None or x < stats['x_range']['min']:
                        stats['x_range']['min'] = x
                    if stats['x_range']['max'] is None or x > stats['x_range']['max']:
                        stats['x_range']['max'] = x
                    
                    for file in os.listdir(x_path):
                        if any(file.endswith(ext) for ext in 
                               self.supported_formats['raster'] + self.supported_formats['vector']):
                            y = int(file.split('.')[0])
                            fmt = file.split('.')[-1]
                            
                            # Y aralığını güncelle
                            if stats['y_range']['min'] is None or y < stats['y_range']['min']:
                                stats['y_range']['min'] = y
                            if stats['y_range']['max'] is None or y > stats['y_range']['max']:
                                stats['y_range']['max'] = y
                            
                            stats['tiles'] += 1
                            if fmt not in stats['formats']:
                                stats['formats'][fmt] = 0
                            stats['formats'][fmt] += 1
                            
        except Exception as e:
            self.logger.error(f"Zoom istatistik hatası: {e}")
        
        return stats 
    
 