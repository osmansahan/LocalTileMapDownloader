"""
Configuration Manager Module
Handles loading and validation of configuration files
"""

import yaml
import sys
import os
from typing import Dict, Any, List, Tuple
from pathlib import Path


class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.errors = []
        self.warnings = []
        
        if self.config:
            self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config is None:
                    self.errors.append("Config dosyası boş veya geçersiz")
                    return {}
                return config
        except FileNotFoundError:
            self.errors.append(f"Config dosyası bulunamadı: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            self.errors.append(f"YAML ayrıştırma hatası: {e}")
            return {}
        except Exception as e:
            self.errors.append(f"Beklenmeyen hata: {e}")
            return {}
    
    def _validate_config(self) -> None:
        """Comprehensive configuration validation"""
        self._validate_required_sections()
        self._validate_sources()
        self._validate_regions()
        self._validate_defaults()
        self._check_file_paths()
    
    def _validate_required_sections(self) -> None:
        """Validate required configuration sections"""
        required_sections = ['sources', 'predefined_regions', 'defaults']
        
        for section in required_sections:
            if section not in self.config:
                self.errors.append(f"Eksik gerekli bölüm: {section}")
            elif not isinstance(self.config[section], dict):
                self.errors.append(f"Geçersiz {section} bölümü: dict olmalı")
    
    def _validate_sources(self) -> None:
        """Validate sources configuration"""
        sources = self.config.get('sources', {})
        
        if not sources:
            self.warnings.append("Hiç kaynak tanımlanmamış")
            return
        
        required_source_fields = ['path', 'name', 'type']
        
        for source_id, source_config in sources.items():
            if not isinstance(source_config, dict):
                self.errors.append(f"Geçersiz kaynak yapılandırması: {source_id}")
                continue
            
            # Check required fields
            for field in required_source_fields:
                if field not in source_config:
                    self.errors.append(f"Kaynak {source_id} eksik alan: {field}")
            
            # Validate type
            valid_types = ['mbtiles']
            source_type = source_config.get('type')
            if source_type and source_type not in valid_types:
                self.errors.append(f"Geçersiz kaynak tipi: {source_type} (geçerli: {valid_types})")
            
            # Validate bounds
            bounds = source_config.get('bounds')
            if bounds:
                if not isinstance(bounds, list) or len(bounds) != 4:
                    self.errors.append(f"Kaynak {source_id} geçersiz bounds: 4 elemanlı liste olmalı")
                else:
                    min_lon, min_lat, max_lon, max_lat = bounds
                    if not all(isinstance(x, (int, float)) for x in bounds):
                        self.errors.append(f"Kaynak {source_id} bounds sayısal değerler olmalı")
                    elif min_lon >= max_lon or min_lat >= max_lat:
                        self.errors.append(f"Kaynak {source_id} geçersiz bounds: min < max olmalı")
            
            # Validate zoom levels
            min_zoom = source_config.get('min_zoom')
            max_zoom = source_config.get('max_zoom')
            if min_zoom is not None and max_zoom is not None:
                if not (0 <= min_zoom <= max_zoom <= 22):
                    self.errors.append(f"Kaynak {source_id} geçersiz zoom seviyeleri: 0-22 arası olmalı")
    
    def _validate_regions(self) -> None:
        """Validate predefined regions configuration"""
        regions = self.config.get('predefined_regions', {})
        
        if not regions:
            self.warnings.append("Hiç bölge tanımlanmamış")
            return
        
        for region_id, region_config in regions.items():
            if not isinstance(region_config, dict):
                self.errors.append(f"Geçersiz bölge yapılandırması: {region_id}")
                continue
            
            # Check required fields
            required_fields = ['name', 'bbox', 'center', 'default_zoom', 'max_zoom']
            for field in required_fields:
                if field not in region_config:
                    self.errors.append(f"Bölge {region_id} eksik alan: {field}")
            
            # Validate bbox format
            bbox = region_config.get('bbox')
            if bbox:
                if not isinstance(bbox, list) or len(bbox) != 4:
                    self.errors.append(f"Geçersiz bbox formatı: {region_id} (4 koordinat gerekli)")
                else:
                    # Check coordinate order: [min_lon, min_lat, max_lon, max_lat]
                    min_lon, min_lat, max_lon, max_lat = bbox
                    if not all(isinstance(x, (int, float)) for x in bbox):
                        self.errors.append(f"Geçersiz koordinat değerleri: {region_id}")
                    elif min_lon >= max_lon or min_lat >= max_lat:
                        self.errors.append(f"Geçersiz bbox koordinatları: {region_id}")
            
            # Validate center format
            center = region_config.get('center')
            if center:
                if not isinstance(center, list) or len(center) != 2:
                    self.errors.append(f"Geçersiz center formatı: {region_id} (2 koordinat gerekli)")
            
            # Validate zoom levels
            default_zoom = region_config.get('default_zoom')
            max_zoom = region_config.get('max_zoom')
            if default_zoom is not None and max_zoom is not None:
                if not (0 <= default_zoom <= max_zoom <= 22):
                    self.errors.append(f"Geçersiz zoom seviyeleri: {region_id}")
    
    def _validate_defaults(self) -> None:
        """Validate default settings"""
        defaults = self.config.get('defaults', {})
        
        # Validate output directory
        output_dir = defaults.get('output_dir')
        if output_dir and not isinstance(output_dir, str):
            self.errors.append("Geçersiz output_dir: string olmalı")
        
        # Validate zoom levels
        min_zoom = defaults.get('min_zoom')
        max_zoom = defaults.get('max_zoom')
        if min_zoom is not None and max_zoom is not None:
            if not (0 <= min_zoom <= max_zoom <= 22):
                self.errors.append("Geçersiz varsayılan zoom seviyeleri")
        
        # Validate formats
        valid_tile_formats = ['jpg', 'png', 'webp']
        valid_vector_formats = ['pbf', 'mvt']
        
        tile_format = defaults.get('tile_format')
        if tile_format and tile_format not in valid_tile_formats:
            self.errors.append(f"Geçersiz tile_format: {tile_format}")
        
        vector_format = defaults.get('vector_format')
        if vector_format and vector_format not in valid_vector_formats:
            self.errors.append(f"Geçersiz vector_format: {vector_format}")
    
    def _check_file_paths(self) -> None:
        """Check if configured file paths exist"""
        sources = self.config.get('sources', {})
        
        for source_id, source_config in sources.items():
            if isinstance(source_config, dict):
                path = source_config.get('path')
                if path and not os.path.exists(path):
                    self.warnings.append(f"Kaynak dosyası bulunamadı: {path}")
    
    def get_sources(self) -> Dict[str, Any]:
        """Get all sources configuration"""
        return self.config.get('sources', {})
    
    def get_regions(self) -> Dict[str, Any]:
        """Get all regions configuration"""
        return self.config.get('predefined_regions', {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default settings"""
        return self.config.get('defaults', {})
    
    def get_source(self, source_id: str) -> Dict[str, Any]:
        """Get specific source configuration"""
        sources = self.config.get('sources', {})
        return sources.get(source_id, {})
    
    def get_region(self, region_id: str) -> Dict[str, Any]:
        """Get specific region configuration"""
        regions = self.config.get('predefined_regions', {})
        return regions.get(region_id, {})
    
    def validate_source_bounds(self, source_id: str, bbox: List[float], min_zoom: int, max_zoom: int) -> Tuple[bool, List[str]]:
        """Validate if the requested region and zoom levels are within source bounds"""
        errors = []
        source = self.get_source(source_id)
        
        if not source:
            errors.append(f"Kaynak bulunamadı: {source_id}")
            return False, errors
        
        # Check bounds
        source_bounds = source.get('bounds')
        if source_bounds:
            min_lon, min_lat, max_lon, max_lat = bbox
            src_min_lon, src_min_lat, src_max_lon, src_max_lat = source_bounds
            
            if min_lon < src_min_lon or max_lon > src_max_lon or min_lat < src_min_lat or max_lat > src_max_lat:
                errors.append(f"İstenen bölge kaynak sınırlarının dışında!")
                errors.append(f"Kaynak sınırları: {src_min_lon}°E, {src_min_lat}°N - {src_max_lon}°E, {src_max_lat}°N")
                errors.append(f"İstenen bölge: {min_lon}°E, {min_lat}°N - {max_lon}°E, {max_lat}°N")
                errors.append(f"Bu bölge için uygun kaynak bulunamadı. Mevcut kaynaklar:")
                
                # Mevcut kaynakları listele
                sources = self.get_sources()
                for sid, sconfig in sources.items():
                    if isinstance(sconfig, dict):
                        s_bounds = sconfig.get('bounds', 'Tanımlanmamış')
                        s_name = sconfig.get('name', 'Bilinmeyen')
                        errors.append(f"   • {sid}: {s_name} - {s_bounds}")
        
        # Check zoom levels
        source_min_zoom = source.get('min_zoom')
        source_max_zoom = source.get('max_zoom')
        
        if source_min_zoom is not None and min_zoom < source_min_zoom:
            errors.append(f"Minimum zoom seviyesi çok düşük: {min_zoom} (kaynak minimum: {source_min_zoom})")
        
        if source_max_zoom is not None and max_zoom > source_max_zoom:
            errors.append(f"Maksimum zoom seviyesi çok yüksek: {max_zoom} (kaynak maksimum: {source_max_zoom})")
        
        return len(errors) == 0, errors
    
    def validate_config(self) -> bool:
        """Check if configuration is valid"""
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Get validation errors"""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Get validation warnings"""
        return self.warnings
    
    def print_validation_report(self) -> None:
        """Print configuration validation report"""
        print("Yapılandırma Doğrulama Raporu")
        print("=" * 40)
        
        if self.errors:
            print(f"\nHatalar ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\nUyarılar ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\nYapılandırma geçerli!")
        
        # Print sources info
        sources = self.get_sources()
        if sources:
            print(f"\nKaynaklar ({len(sources)}):")
            for source_id, source_config in sources.items():
                if isinstance(source_config, dict):
                    name = source_config.get('name', 'Bilinmeyen')
                    bounds = source_config.get('bounds', 'Tanımlanmamış')
                    min_zoom = source_config.get('min_zoom', 'Tanımlanmamış')
                    max_zoom = source_config.get('max_zoom', 'Tanımlanmamış')
                    print(f"  • {source_id}: {name}")
                    print(f"    Sınırlar: {bounds}")
                    print(f"    Zoom: {min_zoom} - {max_zoom}")
        
        # Print regions info
        regions = self.get_regions()
        if regions:
            print(f"\nÖnceden Tanımlı Bölgeler ({len(regions)}):")
            for region_id, region_config in regions.items():
                if isinstance(region_config, dict):
                    name = region_config.get('name', 'Bilinmeyen')
                    bbox = region_config.get('bbox', 'Tanımlanmamış')
                    print(f"  • {region_id}: {name} - {bbox}")
    
    def create_output_directories(self) -> None:
        """Create output directories"""
        defaults = self.get_defaults()
        output_dir = defaults.get('output_dir', 'tiles')
        
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            self.errors.append(f"Çıktı dizini oluşturulamadı: {e}")
    
    def get_safe_config(self) -> Dict[str, Any]:
        """Get safe configuration copy"""
        return self.config.copy() if self.config else {} 