# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-09-23

### Added

- **LinkedIn Integration**: Full support for posting to LinkedIn personal profiles

  - OAuth 2.0 authentication via LinkedIn Developer API
  - Text-only posts with character limit support (3,000 chars)
  - API status checking and credential verification
  - Diagnostic tool integration

- **Self-Contained Package Distribution**

  - Complete Python package with `pyproject.toml` configuration
  - All dependencies, templates, static files, and scripts included
  - Package can be installed independently with `pip install -e .`
  - Module execution support: `python -m socmed_poster`
  - Automated installation script: `install.py`

- **Instagram Upload Alignment**
  - Unified file upload behavior across Facebook, Twitter, and Instagram
  - Consistent image/video file type validation
  - Standardized error handling and user feedback

### Enhanced

- **Web Interface**

  - Added LinkedIn platform tab with professional icon (💼)
  - Platform-specific character limits and media restrictions
  - Real-time status checking for all four platforms

- **API Routes**

  - Extended `/api/status` endpoint to include LinkedIn credentials
  - Comprehensive health checking across all platforms
  - Detailed error reporting and authentication status

- **Diagnostic Tool**
  - Added LinkedIn API reachability testing
  - LinkedIn credential verification
  - Updated summary reporting for all platforms

### Technical

- **Package Structure**

  - Self-contained `socmed_poster/` directory with all files
  - Package-relative imports using `..scripts.*` notation
  - Complete documentation and configuration templates
  - Distribution files: `MANIFEST.in`, `setup.cfg`, `.env.example`

- **Dependencies**
  - All required packages specified in `pyproject.toml`
  - Minimum Python 3.11 requirement
  - Standard social media API libraries (tweepy, requests, etc.)

### Fixed

- File upload validation consistency across platforms
- Template file inclusion in package distribution
- Import path resolution for package vs. repository execution

## [0.0.1] - 2025-09-22

### Added

- Initial release with Facebook, Twitter, and Instagram support
- Flask web interface with Tailwind CSS
- Command-line script execution
- Basic diagnostic tooling
- Environment-based configuration

---

## Upgrade Guide

### From 0.0.1 to 0.1.0

1. **LinkedIn Setup** (Optional):

   ```bash
   # Add to your .env file:
   LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
   LINKEDIN_PERSON_ID=your_linkedin_person_id
   ```

2. **Package Installation**:

   ```bash
   # Install as package for better distribution
   pip install -e .

   # Or use automated installer
   cd socmed_poster
   python install.py
   ```

3. **Updated Usage**:

   ```bash
   # New module execution method
   python -m socmed_poster

   # Original method still works
   python app.py
   ```

No breaking changes - all existing functionality preserved.
