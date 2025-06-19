# SimpleSim Version Incrementation Strategy

## Overview
SimpleSim uses semantic versioning with an automated version bump system. The current version is displayed in the sidebar of the application.

## Version Format: `MAJOR.MINOR.PATCH`

### 🔧 PATCH (0.0.1) - Small Changes
- **Usage**: Bug fixes, small improvements, config changes
- **Examples**: 
  - Fix button alignment
  - Update text colors
  - Small configuration adjustments
  - Minor styling tweaks

### ✨ MINOR (0.1.0) - New Features  
- **Usage**: New features, UI improvements, significant enhancements
- **Examples**:
  - Add new simulation features
  - Improve user interface
  - Add new data visualization
  - Configuration preservation features

### 🚀 MAJOR (1.0.0) - Breaking Changes
- **Usage**: Breaking changes, major architecture changes
- **Examples**:
  - Complete UI redesign
  - API breaking changes
  - Major database schema changes
  - Architecture overhauls

## How to Use

### Quick Command Line
```bash
# For small fixes
.\scripts\version-bump.bat patch "Fix button alignment"

# For new features  
.\scripts\version-bump.bat minor "Add simulation configuration display"

# For breaking changes
.\scripts\version-bump.bat major "Complete UI redesign"
```

### Advanced PowerShell
```powershell
# With custom message
.\scripts\version-bump.ps1 -Type minor -Message "Simulation configuration preservation"

# Dry run (see what would happen)
.\scripts\version-bump.ps1 -Type patch -DryRun

# Skip automatic push
.\scripts\version-bump.ps1 -Type minor -NoPush
```

## What Happens Automatically

1. **Version Update**: Updates `frontend/package.json`
2. **Git Commit**: Creates commit with standardized message
3. **Git Tag**: Creates annotated tag (e.g., `v1.1.0`)
4. **Push to GitLab**: Pushes commit and tags to `open-production/simplesim`
5. **UI Update**: Version displays automatically in sidebar

## Current Version: 1.1.0

### Recent Changes:
- **v1.1.0**: Simulation configuration preservation and improved lever UX
- **v1.0.0**: Initial release with lever functionality and deployment scripts

## Guidelines

- **Use PATCH** for quick fixes and small improvements
- **Use MINOR** for new features that don't break existing functionality  
- **Use MAJOR** sparingly, only for significant breaking changes
- Always include a descriptive message explaining the change
- The version is automatically displayed in the application sidebar 