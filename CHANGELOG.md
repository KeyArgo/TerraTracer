# Changelog

All notable changes to this project will be documented in this file.

## [v0.6] - 2023-11-27
### Added
- New functionalities, logging, and detailed documentation across various modules.
- Enhanced parsing and validation in `utils.py`.
- JSON to KML export functionality in `io_operations.py`.

### Improved
- User interaction, functionality, and error handling in `io_operations.py`, `processes.py`, and `utils.py`.
- Code readability and maintainability in `processes.py` and related modules.

### Note
- These comprehensive improvements enhance the application's user-friendliness, maintainability, data processing capabilities, and introduce new geospatial data export features.

## [v0.5.6] - 2023-11-03
### Added
- Function to assign IDs to polygon points.
- Construction sequence creation that includes tie points and monuments.

### Fixed
- Fixed the issue with the program asking for the filename twice by restructuring the filename input logic.
- Removed the potential inclusion of invalid monument data in the JSON output when no monument exists.
- Eliminated the duplication of the initial point as a placemark in KML files.

### Changed
- Modularized the `create_kml_process` function to improve maintainability.
- Updated `create_kml_process` to ask for the filename only once when exporting to both KML and JSON formats.
- Removed redundant code and consolidated file existence checks into a single location within `create_kml_process`.
- Ensured that export functions `export_kml` and `export_json` are solely responsible for exporting, not for path generation or existence checks.
- Passed `points` directly to `export_kml` function to avoid the undefined variable issue.
- The monument data is now only added to the construction sequence if it has valid latitude and longitude values.
- If the monument data is not valid (i.e., latitude or longitude is `None`), it is now removed from the data dictionary to prevent it from appearing in the output JSON.
- Renamed 'initial' to 'tie_point' in the JSON output to clarify its purpose.

### Removed
- Removed duplicated code for file path checks by centralizing the logic within `create_kml_process`.

### Refactoring
- Reorganized code to ensure a clear separation of concerns, thereby reducing the coupling between modules.

## [v0.5.5] - 2023-11-02
### Added
- `construction_sequence` in JSON for a sequenced approach to KML file recreation.
- Unique IDs for all polygon points and monuments in the JSON output.
- Improved save functionality with directory validation and filename prompts.
- Auto-closure of polygons in KML content creation for map accuracy.

### Changed
- Enhanced `create_kml_process` for consistent file naming and to avoid file overwrites.
- Refined file saving to 'saves/kml' and 'saves/json' directories for organization.
- Renamed 'initial' to 'tie_point' in the JSON output to clarify its purpose.

### Fixed
- Eliminated the duplication of the initial point as a placemark in KML files.
- Resolved the issue where the initial point was incorrectly included as a placemark in KML outputs.

## [v0.5.4] - 2023-11-01
### Added
- Enhanced menu displays for better clarity.
- Detailed descriptions for the polygon creation options and tie point selection.

### Fixed
- Resolved a bug where an unbound local error occurred due to uninitialized variables in the finalize_data function.
- Corrected the workflow to allow users the option to add additional points to a polygon without requiring it.

## [0.5.3] - 2023-10-31
### Added
- Exit mechanism allowing users to return to the main menu or stop current processes.
- Enhanced user input prompts with clear and illustrative examples.

### Changed
- Strengthened input validation across the application.
- Modified logic in several functions to support the new exit functionality.

## [0.5.2] - 2023-10-31
### Added
- Resolved `NameError` and enhanced distance calculation.

## [0.5.1] - 2023-10-31
### Added
- Enhancements to user input handling and file operations.

## [0.5] - 2023-10-29
### Added
- Enhancements and Refactoring

## [0.4.5] - 2023-10-29
### Added
- Enhancements and Bug Fixes

## [0.4] - 2023-10-28
### Added
- Error handling for invalid user input
- Updated code from version 0.3.6 to 0.4 with modular functions

### Fixed
- Resolved conflict in VERSION

## [0.3.6] - 2023-10-21
### Added
- VERSION file creation
- v0.3.6 Update

### Merged
- Experimental data files

## [0.3.5] - 2023-10-20
### Changed
- Updated TerraTracer_v0.3.5

## [0.3] - 2023-10-19
### Added
- Enhancements in v0.3

### Changed
- Renamed TerraTracer_v0.1.1.py to TerraTracer_v0.2.py
- Updated TerraTracer_v0.1.1.py with new features and enhancements

### Fixed
- Reverted unintentional changes in v0.3

## [0.1.1] - 2023-10-17
### Fixed
- Various bug fixes

### Changed
- Updated README.md
- Renamed TerraTrace_v0.1.py to TerraTracer_v0.1.py

## [0.1] - 2023-10-12
### Added
- Initial project structure and README updates

