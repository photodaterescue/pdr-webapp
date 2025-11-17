# Photo Metadata Fixer

## Overview
A browser-based tool that automatically fixes broken metadata and incorrect timestamps in Google Photos Takeout and Apple Photos exports. The application restores original creation dates and produces clean, chronologically organized photo libraries.

## Product Vision
- Simple, secure, browser-based metadata correction
- No installation required, no technical knowledge needed
- Zero storage of user photos (complete privacy guarantee)
- Automated processing with one-click workflow

## Target Users
- Families backing up memories from Google/Apple Photos
- Photographers migrating photo libraries
- Users switching between cloud providers
- Anyone frustrated by messy export metadata

## Current State (MVP - Phase 1)
The application provides:
- ZIP file upload with drag-and-drop interface
- Automatic detection of Google Takeout vs Apple Photos exports
- Google Takeout JSON parsing and EXIF correction
- Apple Photos metadata extraction and fixing
- Chronological organization by year
- Batch processing with real-time progress tracking
- Processing summary with statistics
- Automatic file deletion after download (privacy guarantee)
- 2GB file size limit

## Recent Changes
- 2025-11-17: Initial MVP implementation with security hardening
  - Flask backend with upload/processing endpoints
  - Frontend UI with Tailwind CSS
  - Google Takeout JSON parser (photoTakenTime, creationTime)
  - Apple Photos metadata handler (EXIF extraction, fallback to mtime)
  - EXIF date correction for JPEG files
  - Automatic cleanup with secure deletion on all paths
  - Progress tracking and summary display
  - ZIP-slip protection with commonpath validation
  - Secure extraction preventing path traversal attacks

## Project Architecture

### Backend (Python/Flask)
- `app.py`: Main Flask application
  - Upload endpoint (`/upload`)
  - Format detection (Google/Apple)
  - Metadata parsing and EXIF correction
  - File organization by year
  - Temporary file handling with auto-cleanup

### Frontend (HTML/JavaScript)
- `templates/index.html`: Single-page application
  - Drag-and-drop ZIP upload
  - Progress indicators
  - Processing status display
  - Summary screen with statistics
  - Download functionality

### Key Features
1. **Google Takeout Support**
   - Parses JSON sidecars for timestamps
   - Applies correct dates to EXIF data
   - Handles photoTakenTime and creationTime fields

2. **Apple Photos Support**
   - Extracts existing EXIF metadata
   - Falls back to file modification times
   - Preserves original quality

3. **File Organization**
   - Organizes photos into year-based folders
   - Renames files with timestamp format: YYYYMMDD_HHMMSS_N
   - Creates clean ZIP for download

4. **Privacy & Security**
   - All processing in temporary directories
   - Files deleted immediately after download
   - No database or persistent storage
   - Session-based processing only

## Technical Stack
- **Backend**: Python 3.11, Flask
- **Image Processing**: Pillow, piexif
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Environment**: Replit (development), stateless processing

## Dependencies
- flask: Web framework
- pillow: Image processing
- piexif: EXIF metadata manipulation

## Next Phase (Planned)
- Optional file renaming formats
- Sort by month in addition to year
- Apple Photos album reconstruction
- Large ZIP support with chunk processing
- Payment integration (£25-£50 one-off)

## User Preferences
None documented yet.

## File Structure
```
/
├── app.py                  # Flask backend
├── templates/
│   └── index.html         # Frontend UI
├── .gitignore             # Python/Flask ignores
├── replit.md              # This file
├── pyproject.toml         # Python dependencies
└── uv.lock                # Dependency lock file
```

## Running the Application
The application runs on port 5000 and binds to 0.0.0.0 for web access.
Command: `python app.py`
