# install-pyenv-win.ps1

# Set pyenv installation directory
$pyenvRoot = "$env:USERPROFILE\.pyenv"

# Clone the pyenv-win repo
if (-Not (Test-Path $pyenvRoot)) {
    Write-Host "Cloning pyenv-win..."
    git clone https://github.com/pyenv-win/pyenv-win.git $pyenvRoot
} else {
    Write-Host "pyenv-win already installed at $pyenvRoot"
}

# Define paths to add
$binPath = "$pyenvRoot\pyenv-win\bin"
$shimsPath = "$pyenvRoot\pyenv-win\shims"

# Get existing user PATH
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", "User")

# Add paths if not already present
if ($currentPath -notlike "*$binPath*") {
    $currentPath += ";$binPath"
}
if ($currentPath -notlike "*$shimsPath*") {
    $currentPath += ";$shimsPath"
}

# Update environment variable
[System.Environment]::SetEnvironmentVariable("Path", $currentPath, "User")

Write-Host "`n✅ pyenv-win installed successfully!"
Write-Host "Please restart your terminal or run: `$env:Path = [System.Environment]::GetEnvironmentVariable('Path','User')"
