# Photo Date Rescue

## Overview
A browser-based tool that automatically fixes broken metadata and incorrect timestamps in Google Photos downloads and Apple Photos exports. The application restores original creation dates and produces clean, chronologically organized photo libraries.

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

## Current State (MVP - Phase 2)
The application provides:
- ZIP file upload with drag-and-drop interface (with metadata option validation)
- Automatic detection of Google Photos downloads vs Apple Photos exports
- Google Photos download JSON parsing and EXIF correction
- Apple Photos metadata extraction and fixing
- **NEW: XMP metadata extraction** (timestamps and orientation)
- **NEW: Filename-based date parsing fallback** (YYYYMMDD, YYYY-MM-DD formats)
- **NEW: Four-tier file classification system** (fixed, restored_from_filename, renamed_only, skipped)
- **NEW: Needs_Review folder** for files with no extractable metadata
- **NEW: User-configurable missing metadata handling** (keep/rename vs skip entirely)
- Chronological organization by year
- Batch processing with real-time progress tracking
- Processing summary with detailed statistics (4 separate counters)
- Automatic file deletion after download (privacy guarantee)
- 2GB file size limit

## Recent Changes
- 2025-12-08: Integrated shared header/footer from main website
  - Added sticky site-header with brand, navigation, and CTA button
  - Added site-footer with copyright and links to main website
  - Added CSS variables for lavender theme consistency
  - Replaced old in-page header with new design matching photodaterescue.com
  - Responsive navigation (hides on mobile, shows CTA button)
  - All nav links point to main website sections

- 2025-11-17: Branding update and final UX refinements
  - **Rebranded to "Photo Date Rescue"** - More user-friendly, memorable name
  - **Updated terminology** - "Google Photos downloads" instead of "Takeout" throughout
  - **Advanced settings defaults changed** - "Allow fallback to Last Modified timestamp" now ON by default
  - **Updated summary labels** - More descriptive explanations for each category:
    * "Fixed with full metadata (EXIF or XMP → EXIF)"
    * "Fixed from filename (date guessed from filename pattern)"
    * "Removed (no valid date)" instead of "Skipped"
  - **Simplified copy** - "Remove files with no valid date" instead of lengthy description

- 2025-11-17: Major UX overhaul - Simplified interface with smart defaults
  - **Removed required dropdown** - Users can now upload immediately without configuration
  - **Smart default behavior** - Automatically handles all files intelligently (EXIF → XMP → Filename → Keep)
  - **Advanced Settings panel** - Optional collapsible settings for power users
  - **Cleaner filenames** - Now uses `YYYYMMDD_HHMMSS.jpg` format, only adds `_2`, `_3` on actual collisions
  - **No more validation alerts** - Drop zone always active, no browser alert() popups
  - All changes preserve existing privacy guarantees and security features

- 2025-11-17: Enhanced filename date extraction for WhatsApp and common formats
  - Added detection for WhatsApp patterns: IMG-YYYYMMDD-WA####.*, IMG_YYYYMMDD_####.*
  - Added catch-all for any 8-digit date (YYYYMMDD) in filename
  - Files with filename dates now properly classified as "restored_from_filename"
  - Uses 12:00:00 as safe placeholder when only date available (no time)
  - WhatsApp photos and similar formats no longer go to Needs_Review
  - Only truly undatable files (no EXIF, XMP, or filename date) go to Needs_Review or are skipped

- 2025-11-17: UX enhancement - Consistent terminology and tooltips
  - Updated headline: "Fix broken photo dates" (more user-friendly than "timestamps")
  - Changed "Google Photos Takeout" → "Google Photos Download" across entire app
  - Added hover tooltips with ⓘ icons on BOTH upload screen and results screen
  - Tooltips show alternative names users might recognize (Google Takeout ZIP, Photos.app Export, etc.)
  - Consistent terminology across all pages for clarity
  - Clean UI design with smooth fade-in hover transitions

- 2025-11-17: Phase 2 implementation - Advanced metadata handling
  - Added required dropdown for metadata handling options (keep/rename vs skip)
  - Implemented XMP metadata extraction (timestamps + orientation)
  - Added filename-to-EXIF parsing fallback (YYYYMMDD, YYYY-MM-DD formats)
  - Four-tier classification system with detailed counters
  - Needs_Review folder for renamed_only files
  - Upload validation (both click and drag-and-drop) requires metadata option first
  - Results screen shows: fixed, restored from filename, renamed only, skipped counts

- 2025-11-17: Initial MVP implementation with security hardening
  - Flask backend with upload/processing endpoints
  - Frontend UI with Tailwind CSS
  - Google Photos download JSON parser (photoTakenTime, creationTime)
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
1. **Google Photos Download Support**
   - Parses JSON sidecars for timestamps
   - Applies correct dates to EXIF data
   - Handles photoTakenTime and creationTime fields

2. **Apple Photos Support**
   - Extracts existing EXIF metadata
   - Falls back to file modification times
   - Preserves original quality

3. **Advanced Metadata Extraction** (Phase 2)
   - Four-tier metadata extraction hierarchy:
     1. JSON sidecars (Google Photos downloads) or existing EXIF
     2. XMP metadata (timestamps and orientation)
     3. Filename parsing (YYYYMMDD, YYYY-MM-DD formats)
     4. User-selected handling (keep/rename or skip)
   - Intelligent date validation (1970-2100 range)
   - Orientation extraction from XMP data

4. **File Classification & Organization**
   - **Fixed**: Files with successfully restored metadata
   - **Restored from Filename**: Files with dates parsed from filenames
   - **Renamed Only**: Files placed in Needs_Review folder (no extractable metadata)
   - **Skipped**: Files excluded from output (when user selects "skip" option)
   - Organizes photos into year-based folders
   - Renames files with timestamp format: YYYYMMDD_HHMMSS_N
   - Creates clean ZIP for download

5. **Privacy & Security**
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
