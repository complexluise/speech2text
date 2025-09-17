#Requires -Version 5.0
<#
.SYNOPSIS
    Processes each audio file in a directory using the speech2text tool.

.DESCRIPTION
    This script iterates through all .wav files in the specified directory
    and runs the speech2text command for each file.

.PARAMETER InputDir
    The path to the directory containing the audio files to process.
    Default is '.\data'.

.EXAMPLE
    ./process_audio.ps1

.EXAMPLE
    ./process_audio.ps1 -InputDir C:\my_audio_parts
#>
param(
    [Parameter(Mandatory = $false, Position = 0, HelpMessage = "Path to the directory with audio files.")]
    [string]$InputDir = ".\data"
)

# 1. Resolve and validate the input directory path
$resolvedInputDir = Resolve-Path -Path $InputDir -ErrorAction SilentlyContinue
if (-not $resolvedInputDir) {
    Write-Error "Input directory not found at path: $InputDir"
    exit 1
}

# 2. Get all .wav files in the directory
$audioFiles = Get-ChildItem -Path $resolvedInputDir -Filter *.wav

if ($audioFiles.Count -eq 0) {
    Write-Host "No .wav files found in $resolvedInputDir"
    exit 0
}

# 3. Process each audio file
Write-Host "Found $($audioFiles.Count) audio files to process in $resolvedInputDir"

foreach ($file in $audioFiles) {
    $filePath = $file.FullName
    Write-Host "`nProcessing file: $filePath" -ForegroundColor Yellow

    # Assumes the virtual environment is in the standard '.venv' directory
    $venvPath = Join-Path $PSScriptRoot ".venv"
    $pythonPath = Join-Path $venvPath "Scripts\\python.exe"

    if (-not (Test-Path $pythonPath)) {
        Write-Error "Python executable not found at $pythonPath. Please ensure the virtual environment is created and located at '$venvPath'."
        exit 1
    }

    $command = "$pythonPath -m speech2text transcribe `"$filePath`""

    try {
        Invoke-Expression -Command $command -ErrorAction Stop
        Write-Host "[SUCCESS] Finished processing: $filePath" -ForegroundColor Green
    }
    catch {
        Write-Error "[FAILURE] Failed to process: $filePath"
        Write-Error $_
    }
}

Write-Host "`nAll files processed." -ForegroundColor Green
