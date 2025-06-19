# SimpleSim Version Bump Script
# Handles version increments: patch (0.0.1), minor (0.1.0), major (1.0.0)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("patch", "minor", "major")]
    [string]$Type,
    
    [string]$Message = "",
    [switch]$NoPush,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "=== SimpleSim Version Bump ===" -ForegroundColor Yellow

# Get project root directory
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PackageJsonPath = Join-Path $ProjectRoot "frontend\package.json"

function Get-CurrentVersion {
    if (!(Test-Path $PackageJsonPath)) {
        throw "package.json not found at $PackageJsonPath"
    }
    
    $packageJson = Get-Content $PackageJsonPath | ConvertFrom-Json
    return $packageJson.version
}

function Update-Version {
    param($NewVersion)
    
    if ($DryRun) {
        Write-Host "DRY RUN: Would update version to $NewVersion" -ForegroundColor Yellow
        return
    }
    
    # Update package.json
    $packageJson = Get-Content $PackageJsonPath | ConvertFrom-Json
    $packageJson.version = $NewVersion
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content $PackageJsonPath
    
    Write-Host "Updated package.json version to $NewVersion" -ForegroundColor Green
}

function Bump-Version {
    param($CurrentVersion, $BumpType)
    
    $versionParts = $CurrentVersion -split '\.'
    if ($versionParts.Length -ne 3) {
        throw "Invalid version format: $CurrentVersion. Expected format: x.y.z"
    }
    
    $major = [int]$versionParts[0]
    $minor = [int]$versionParts[1]
    $patch = [int]$versionParts[2]
    
    switch ($BumpType) {
        "patch" {
            $patch++
            $newVersion = "$major.$minor.$patch"
            $changeType = "Patch"
            $description = "Bug fixes, small improvements"
        }
        "minor" {
            $minor++
            $patch = 0
            $newVersion = "$major.$minor.$patch"
            $changeType = "Minor"
            $description = "New features, enhancements"
        }
        "major" {
            $major++
            $minor = 0
            $patch = 0
            $newVersion = "$major.$minor.$patch"
            $changeType = "Major"
            $description = "Breaking changes, major releases"
        }
    }
    
    return @{
        Version = $newVersion
        ChangeType = $changeType
        Description = $description
    }
}

function Commit-VersionChange {
    param($OldVersion, $NewVersion, $ChangeType, $CustomMessage)
    
    if ($DryRun) {
        Write-Host "DRY RUN: Would commit version change" -ForegroundColor Yellow
        return
    }
    
    Set-Location $ProjectRoot
    
    # Add the changed files
    git add frontend/package.json
    
    # Create commit message
    if ($CustomMessage) {
        $commitMessage = "chore: bump version to v$NewVersion - $CustomMessage"
    } else {
        $commitMessage = "chore: bump version to v$NewVersion"
    }
    
    # Commit the version change
    git commit -m $commitMessage
    
    # Create a git tag
    $tagMessage = "v$NewVersion - $ChangeType Release"
    git tag -a "v$NewVersion" -m $tagMessage
    
    Write-Host "Committed version bump and created tag v$NewVersion" -ForegroundColor Green
}

function Push-Changes {
    param($NewVersion)
    
    if ($DryRun) {
        Write-Host "DRY RUN: Would push changes and tags" -ForegroundColor Yellow
        return
    }
    
    if ($NoPush) {
        Write-Host "Skipping push (use git push and git push --tags when ready)" -ForegroundColor Yellow
        return
    }
    
    try {
        # Push to GitLab
        git push gitlab master
        git push gitlab --tags
        Write-Host "Pushed changes and tags to GitLab" -ForegroundColor Green
    } catch {
        Write-Host "Failed to push to GitLab: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Manual push: git push gitlab master; git push gitlab --tags" -ForegroundColor Yellow
    }
}

function Show-VersionInfo {
    param($OldVersion, $NewVersion, $ChangeType, $Description)
    
    Write-Host "`n=== Version Bump Summary ===" -ForegroundColor Yellow
    Write-Host "Previous Version: v$OldVersion" -ForegroundColor Gray
    Write-Host "New Version:      v$NewVersion" -ForegroundColor Green
    Write-Host "Change Type:      $ChangeType" -ForegroundColor Cyan
    Write-Host "Description:      $Description" -ForegroundColor Gray
    
    if ($Message) {
        Write-Host "Custom Message:   $Message" -ForegroundColor Magenta
    }
    
    Write-Host "`n=== Usage Guidelines ===" -ForegroundColor Yellow
    Write-Host "PATCH: Bug fixes, small improvements, config changes" -ForegroundColor Gray
    Write-Host "MINOR: New features, UI improvements, significant enhancements" -ForegroundColor Gray  
    Write-Host "MAJOR: Breaking changes, major architecture changes" -ForegroundColor Gray
}

# Main execution
try {
    $currentVersion = Get-CurrentVersion
    $versionInfo = Bump-Version -CurrentVersion $currentVersion -BumpType $Type
    
    Show-VersionInfo -OldVersion $currentVersion -NewVersion $versionInfo.Version -ChangeType $versionInfo.ChangeType -Description $versionInfo.Description
    
    if ($DryRun) {
        Write-Host "`nDRY RUN MODE - No changes will be made" -ForegroundColor Yellow
        exit 0
    }
    
    # Confirm the change
    $confirmation = Read-Host "`nProceed with version bump? (y/N)"
    if ($confirmation -notmatch "^[Yy]$") {
        Write-Host "Version bump cancelled" -ForegroundColor Red
        exit 1
    }
    
    # Execute the version bump
    Update-Version -NewVersion $versionInfo.Version
    Commit-VersionChange -OldVersion $currentVersion -NewVersion $versionInfo.Version -ChangeType $versionInfo.ChangeType -CustomMessage $Message
    Push-Changes -NewVersion $versionInfo.Version
    
    Write-Host "`nVersion bump completed successfully!" -ForegroundColor Green
    Write-Host "New version: v$($versionInfo.Version)" -ForegroundColor Cyan
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 