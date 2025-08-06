# Local Tile Map Downloader

A Python tool for extracting vector and raster tiles from MBTiles format map files for specific geographic regions.

## Features

- **MBTiles Support**: OSM vector and satellite raster tiles
- **Regional Extraction**: Tile generation for specific geographic regions
- **Multiple Sources**: Turkey, Africa, and South America maps
- **Coordinate Conversion**: Lat/Lon ↔ Tile coordinates
- **Progress Tracking**: Monitor tile generation process
- **Error Handling**: Warnings for missing files and format errors
- **Boundary Validation**: Source boundaries and zoom level verification
- **Flexible Usage**: Both predefined regions and custom coordinates

## Installation

### Requirements
- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/osmansahan/LocalTileMapDownloader.git
   cd LocalTileMapDownloader
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download MBTiles files**
   
   Download all MBTiles files from Google Drive:
   
   📦 [Download from Google Drive](https://drive.google.com/drive/folders/YOUR_FOLDER_ID)
   
               **Files included:**
     
     - `osm-2020-02-10-v3.11_europe_turkey.mbtiles` (772 MB) 🔄 Coming soon
     - `satellite-2017-11-02_europe_turkey.mbtiles` (1500 MB) 🔄 Coming soon
     - `osm-2020-02-10-v3.11_africa.mbtiles` (7400 MB) 🔄 Coming soon
     - `osm-2020-02-10-v3.11_south-america.mbtiles` (7700 MB) 🔄 Coming soon
   
   **Note**: Place all files in the `mbtiles/` directory to match the paths in `config.yaml`.

4. **Check configuration**
   
   The `config.yaml` file contains sources, boundaries, and predefined regions.

## Quick Start

### Basic Commands

```bash
# Validate configuration
python local_tile_downloader.py --validate-config

# List available sources
python local_tile_downloader.py --list-sources

# List available regions
python local_tile_downloader.py --list-regions

# Help menu
python local_tile_downloader.py --help
```

### First Examples

```bash
# Using predefined region
python local_tile_downloader.py --region ankara --source osm_turkey

# Using custom coordinates
python local_tile_downloader.py --min-lon 32.5 --min-lat 39.7 --max-lon 33.2 --max-lat 40.1 --source osm_turkey
```

## Usage

### Usage Methods

1. **Predefined Regions**
   ```bash
   python local_tile_downloader.py --region <region_name> --source <source> [--min-zoom <level>] [--max-zoom <level>]
   ```

2. **Custom Coordinates**
   ```bash
   python local_tile_downloader.py --min-lon <min_lon> --min-lat <min_lat> --max-lon <max_lon> --max-lat <max_lat> --source <source> [--min-zoom <level>] [--max-zoom <level>] [--region-name <name>]
   ```

### Parameters

- `--region`: Predefined region name (ankara, istanbul, turkey_full, etc.)
- `--min-lon`: Minimum longitude
- `--min-lat`: Minimum latitude
- `--max-lon`: Maximum longitude
- `--max-lat`: Maximum latitude
- `--source`: Source to use (osm_turkey, satellite_turkey, osm_africa, osm_south_america)
- `--min-zoom`: Minimum zoom level (default: source minimum)
- `--max-zoom`: Maximum zoom level (default: source maximum)
- `--region-name`: Region name for output (default: custom)

**Note**: If you don't specify zoom levels, the tool will automatically use the source's default zoom range. You can override this by specifying custom zoom levels within the source boundaries.

## Example Commands

### Using Predefined Regions

```bash
# OSM vector tiles for Ankara
python local_tile_downloader.py --region ankara --source osm_turkey

# Satellite raster tiles for Istanbul (zoom 10-13)
python local_tile_downloader.py --region istanbul --source satellite_turkey --min-zoom 10 --max-zoom 13

# OSM vector tiles for entire Turkey
python local_tile_downloader.py --region turkey_full --source osm_turkey --min-zoom 5 --max-zoom 8
```

### Using Custom Coordinates

```bash
# OSM vector tiles for Ankara
python local_tile_downloader.py --min-lon 32.5 --min-lat 39.7 --max-lon 33.2 --max-lat 40.1 --source osm_turkey

# Satellite raster tiles for Istanbul (zoom 10-13)
python local_tile_downloader.py --min-lon 28.0 --min-lat 40.8 --max-lon 29.9 --max-lat 41.5 --source satellite_turkey --min-zoom 10 --max-zoom 13

# OSM vector tiles for Africa
python local_tile_downloader.py --min-lon -20.0 --min-lat -35.0 --max-lon 55.0 --max-lat 37.0 --source osm_africa
```

## Data Sources

### Required MBTiles Files

**Important**: You need to download these MBTiles files separately and place them in the `mbtiles/` directory before using the tool.

| Source ID | Name | Format | Size | Status |
|-----------|------|--------|------|--------|
| `osm_turkey` | OpenStreetMap Turkey (Vector) | PBF | 772 MB | 🔄 Coming soon |
| `satellite_turkey` | Satellite Turkey (Raster) | JPG | 1500 MB | 🔄 Coming soon |
| `osm_africa` | OpenStreetMap Africa (Vector) | PBF | 7400 MB | 🔄 Coming soon |
| `osm_south_america` | OpenStreetMap South America (Vector) | PBF | 7700 MB | 🔄 Coming soon |

📁 [Download all files: Google Drive](https://drive.google.com/drive/folders/YOUR_FOLDER_ID)

### File Structure

After downloading, your `mbtiles/` directory should look like this:

```
mbtiles/
├── osm-2020-02-10-v3.11_europe_turkey.mbtiles
├── satellite-2017-11-02_europe_turkey.mbtiles
├── osm-2020-02-10-v3.11_africa.mbtiles
└── osm-2020-02-10-v3.11_south-america.mbtiles
```

### Source Boundaries and Zoom Levels

| Source ID | Boundary Coordinates (Min Lon, Min Lat, Max Lon, Max Lat) | Zoom Levels | Coverage |
|-----------|------------------------------------------------------------|-------------|----------|
| `osm_turkey` | 25.31°E, 35.46°N - 45.00°E, 42.55°N | 5 - 13 | Turkey |
| `satellite_turkey` | 25.31°E, 35.46°N - 45.00°E, 42.55°N | 5 - 13 | Turkey |
| `osm_africa` | 20.0°W, 35.0°S - 55.0°E, 37.0°N | 4 - 12 | Africa |
| `osm_south_america` | 85.0°W, 55.0°S - 35.0°W, 12.0°N | 4 - 12 | South America |

### Source Details

- **OSM Vector Tiles**: Road networks, buildings, names, boundaries
- **Satellite Raster Tiles**: Satellite imagery, terrain views

## Regions

### Predefined Regions

| Region ID | Region Name | Coordinates | Default Zoom | Max Zoom |
|-----------|-------------|-------------|--------------|----------|
| `turkey_full` | Full Turkey | 25.31°E, 35.46°N - 45.00°E, 42.55°N | 5 | 13 |
| `turkey_central` | Central Turkey | 30.0°E, 37.0°N - 40.0°E, 40.0°N | 7 | 13 |
| `turkey_west` | Western Turkey | 26.0°E, 36.5°N - 35.0°E, 42.2°N | 7 | 13 |
| `turkey_east` | Eastern Turkey | 35.0°E, 36.0°N - 45.0°E, 42.0°N | 7 | 13 |
| `ankara` | Ankara | 32.5°E, 39.7°N - 33.2°E, 40.1°N | 10 | 13 |
| `istanbul` | Istanbul | 28.0°E, 40.8°N - 29.9°E, 41.5°N | 9 | 13 |
| `izmir` | Izmir | 26.5°E, 38.0°N - 27.5°E, 39.0°N | 10 | 13 |
| `antalya` | Antalya | 30.0°E, 36.0°N - 32.0°E, 37.5°N | 9 | 13 |

### Zoom Levels

| Zoom Level | Coverage | Usage |
|------------|----------|-------|
| 4-6 | Continent/Country | General overview |
| 7-9 | Country/Province | City planning |
| 10-12 | Province/District | Detailed mapping |
| 13-15 | Neighborhood/Street | Very detailed |

## Output Structure

```
tiles/
├── ankara/
│   ├── 10/
│   │   ├── 584/
│   │   │   ├── 640.pbf
│   │   │   └── 641.pbf
│   │   └── 585/
│   └── 11/
├── istanbul/
│   ├── 10/
│   │   ├── 584/
│   │   │   ├── 640.jpg
│   │   │   └── 641.jpg
│   │   └── 585/
│   └── 11/
└── custom/
    └── 10/
        └── 584/
```

## Testing

### Quick Tests

```bash
# Small test using region
python local_tile_downloader.py --region ankara --source osm_turkey --min-zoom 6 --max-zoom 7

# Small test using coordinates
python local_tile_downloader.py --min-lon 32.5 --min-lat 39.7 --max-lon 33.2 --max-lat 40.1 --source osm_turkey --min-zoom 6 --max-zoom 7

# Medium test (4 zoom levels)
python local_tile_downloader.py --region istanbul --source satellite_turkey --min-zoom 8 --max-zoom 11
```

### Error Tests

```bash
# Coordinates outside source boundaries (Asia example)
python local_tile_downloader.py --min-lon 100.0 --min-lat 30.0 --max-lon 110.0 --max-lat 40.0 --source osm_turkey

# Invalid source
python local_tile_downloader.py --region ankara --source invalid_source

# Invalid zoom level
python local_tile_downloader.py --region ankara --source osm_turkey --min-zoom 25 --max-zoom 30
```

## Configuration

In the `config.yaml` file, you can define:

- **Sources**: MBTiles files, boundaries, and zoom levels
- **Predefined Regions**: Coordinate boundaries and zoom levels
- **Defaults**: Output directory and format settings

### Configuration Validation

```bash
python local_tile_downloader.py --validate-config
```

## Limitations

- MBTiles files can only generate tiles for the zoom levels and coordinates they contain
- If the selected region or zoom range is outside the MBTiles file boundaries, no tiles will be generated
- In such cases, you will receive "tile not found" warnings
- If coordinates outside source boundaries are entered, a detailed error message is provided
- For example: When coordinates from Asia are entered, the boundaries of available sources are shown

## Dependencies

- `pyyaml`: YAML configuration file processing
- `tqdm`: Progress bar
- `Pillow`: Image processing
- `sqlite3`: MBTiles database processing (Python built-in)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue on GitHub.

**Note**: This project only provides tile generation functionality. To view the generated tiles, you need to use map servers or web applications. 
