#!/usr/bin/env python3
"""
Local Tile Downloader - Extract tiles from various local file formats
Supports MBTiles, XYZ directories, PNG/JPG files, GeoTIFF, etc.
"""

import os
import argparse
from config_manager import ConfigManager
from extractors import TileExtractorFactory
from tile_writer import TileWriter


class LocalTileDownloader:
    """Main class for local tile downloading operations"""
    
    def __init__(self, output_dir: str = "tiles"):
        self.output_dir = output_dir
        self.config_manager = ConfigManager()
        
        # Config validasyonu
        if not self.config_manager.validate_config():
            print("Config dosyasında hatalar bulundu:")
            for error in self.config_manager.get_errors():
                print(f"  - {error}")
            raise ValueError("Config dosyası geçersiz")
        
        # Uyarıları göster
        warnings = self.config_manager.get_warnings()
        if warnings:
            print("Config uyarıları:")
            for warning in warnings:
                print(f"  - {warning}")
        
        # Çıktı dizinlerini oluştur
        self.config_manager.create_output_directories()
        
        self.tile_writer = TileWriter(output_dir)
    
    def download_region(self, region_name: str, source_name: str, 
                       min_zoom: int, max_zoom: int) -> None:
        """Download tiles for a specific predefined region"""
        print(f"Bölge: {region_name}")
        
        # Get region coordinates
        regions = self.config_manager.get_regions()
        if region_name not in regions:
            raise ValueError(f"Bölge '{region_name}' config'de bulunamadı")
        
        region = regions[region_name]
        bbox = region['bbox']
        print(f"Koordinatlar: {bbox}")
        
        # Download using the region's bbox
        self.download_area(bbox, source_name, min_zoom, max_zoom, region_name)
    
    def download_area(self, bbox: list, source_name: str, 
                     min_zoom: int, max_zoom: int, region_name: str = "custom") -> None:
        """Download tiles for a specific area defined by bounding box"""
        print(f"Bölge: {region_name}")
        print(f"Koordinatlar: {bbox}")
        
        # Validate source bounds
        is_valid, errors = self.config_manager.validate_source_bounds(source_name, bbox, min_zoom, max_zoom)
        if not is_valid:
            print("Kaynak sınırları hatası:")
            for error in errors:
                print(f"  {error}")
            raise ValueError("İstenen bölge kaynak sınırlarının dışında")
        
        # Get source configuration
        sources = self.config_manager.get_sources()
        if source_name not in sources:
            raise ValueError(f"Kaynak '{source_name}' config'de bulunamadı")
        
        source = sources[source_name]
        source_path = source['path']
        source_type = source['type']
        
        print(f"Zoom: {min_zoom} - {max_zoom}")
        print(f"Kaynak: {source_path}")
        
        # Create extractor
        factory = TileExtractorFactory()
        extractor = factory.create_extractor(source_type, source_path)
        
        # Extract tiles
        tiles_by_zoom = {}
        for zoom in range(min_zoom, max_zoom + 1):
            print(f"Zoom {zoom} işleniyor...")
            tiles = extractor.extract_tiles(bbox, zoom)
            tiles_by_zoom[zoom] = tiles
        
        # Write tiles
        total_tiles = self.tile_writer.write_tiles(tiles_by_zoom, region_name, source_type)
        
        if total_tiles > 0:
            print(f"\nBaşarıyla {total_tiles} tile oluşturuldu!")
            print(f"Kaydedildi: {os.path.join(self.output_dir, region_name)}")
        else:
            print(f"\nHiç tile oluşturulamadı!")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Local Tile Map Downloader")
    
    # Special commands that don't need region/coordinates
    parser.add_argument("--validate-config", action="store_true", help="Validate configuration file")
    parser.add_argument("--list-sources", action="store_true", help="List available sources")
    parser.add_argument("--list-regions", action="store_true", help="List available regions")
    
    # Region or coordinates
    parser.add_argument("--region", help="Predefined region name")
    parser.add_argument("--min-lon", type=float, help="Minimum longitude")
    parser.add_argument("--min-lat", type=float, help="Minimum latitude")
    parser.add_argument("--max-lon", type=float, help="Maximum longitude")
    parser.add_argument("--max-lat", type=float, help="Maximum latitude")
    
    # Other arguments
    parser.add_argument("--source", help="Source name")
    parser.add_argument("--min-zoom", type=int, help="Minimum zoom level (default: source minimum)")
    parser.add_argument("--max-zoom", type=int, help="Maximum zoom level (default: source maximum)")
    parser.add_argument("--region-name", default="custom", help="Region name for output")
    
    args = parser.parse_args()
    
    # Config validasyonu
    if args.validate_config:
        config_manager = ConfigManager()
        config_manager.print_validation_report()
        return
    
    # Kaynakları listele
    if args.list_sources:
        config_manager = ConfigManager()
        sources = config_manager.get_sources()
        print("Mevcut Kaynaklar:")
        print("=" * 50)
        for source_id, source_config in sources.items():
            if isinstance(source_config, dict):
                name = source_config.get('name', 'Bilinmeyen')
                bounds = source_config.get('bounds', 'Tanımlanmamış')
                min_zoom = source_config.get('min_zoom', 'Tanımlanmamış')
                max_zoom = source_config.get('max_zoom', 'Tanımlanmamış')
                format_type = source_config.get('format', 'N/A')
                size_mb = source_config.get('size_mb', 'N/A')
                
                print(f"\n{source_id}")
                print(f"   Ad: {name}")
                print(f"   Format: {format_type}")
                print(f"   Boyut: {size_mb} MB")
                print(f"   Sınırlar: {bounds}")
                print(f"   Zoom: {min_zoom} - {max_zoom}")
        return
    
    # Bölgeleri listele
    if args.list_regions:
        config_manager = ConfigManager()
        regions = config_manager.get_regions()
        print("Önceden Tanımlı Bölgeler:")
        print("=" * 50)
        for region_id, region_config in regions.items():
            if isinstance(region_config, dict):
                name = region_config.get('name', 'Bilinmeyen')
                bbox = region_config.get('bbox', 'Tanımlanmamış')
                default_zoom = region_config.get('default_zoom', 'Tanımlanmamış')
                max_zoom = region_config.get('max_zoom', 'Tanımlanmamış')
                
                print(f"\n{region_id}")
                print(f"   Ad: {name}")
                print(f"   Koordinatlar: {bbox}")
                print(f"   Varsayılan Zoom: {default_zoom}")
                print(f"   Maksimum Zoom: {max_zoom}")
        return
    
    # Gerekli parametreleri kontrol et
    if not args.source:
        print("Eksik parametreler!")
        print("Gerekli parametreler: --source")
        print("\nÖrnek kullanım:")
        print("# Bölge kullanarak:")
        print("python local_tile_downloader.py --region ankara --source osm_turkey")
        print("\n# Koordinat kullanarak:")
        print("python local_tile_downloader.py --min-lon 32.5 --min-lat 39.7 --max-lon 33.2 --max-lat 40.1 --source osm_turkey")
        return
    
    try:
        # Downloader'ı başlat
        downloader = LocalTileDownloader()
        
        # Varsayılan zoom değerlerini kaynak sınırlarından al
        config_manager = ConfigManager()
        sources = config_manager.get_sources()
        
        if args.source not in sources:
            print(f"Kaynak '{args.source}' bulunamadı!")
            return 1
        
        source = sources[args.source]
        default_min_zoom = source.get('min_zoom', 0)
        default_max_zoom = source.get('max_zoom', 18)
        
        # Zoom değerlerini ayarla
        min_zoom = args.min_zoom if args.min_zoom is not None else default_min_zoom
        max_zoom = args.max_zoom if args.max_zoom is not None else default_max_zoom
        
        # Region veya coordinates kullanımı
        if args.region:
            # Predefined region kullan
            downloader.download_region(args.region, args.source, min_zoom, max_zoom)
        else:
            # Custom coordinates kullan
            if not all([args.min_lon, args.min_lat, args.max_lon, args.max_lat]):
                print("Koordinat kullanımı için tüm koordinat parametreleri gerekli!")
                print("Gerekli parametreler: --min-lon, --min-lat, --max-lon, --max-lat")
                return
            
            # Bounding box oluştur
            bbox = [args.min_lon, args.min_lat, args.max_lon, args.max_lat]
            
            # Koordinatları doğrula
            if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
                print("Geçersiz koordinatlar!")
                print("min_lon < max_lon ve min_lat < max_lat olmalı")
                return
            
            # Tile'ları indir
            downloader.download_area(bbox, args.source, min_zoom, max_zoom, args.region_name)
        
    except Exception as e:
        print(f"Hata: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 