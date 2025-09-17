#Requires -Version 5.0
<#
.SYNOPSIS
    Creates a 5-minute sample from an audio file using ffmpeg.

.DESCRIPTION
    This script takes an input audio file and uses ffmpeg to create a 5-minute sample
    from the beginning of the file. It copies the audio stream without re-encoding
    for speed and quality preservation.

.PARAMETER InputFile
    The absolute or relative path to the source audio file (e.g., .m4a, .mp3, .wav).

.PARAMETER OutputFile
    Optional. The path for the output sample file. If not provided, a default name
    will be generated (e.g., 'input-file_sample.m4a').

.EXAMPLE
    ./create_sample.ps1 -InputFile .\my-long-audio.m4a

.EXAMPLE
    ./create_sample.ps1 -InputFile C:\audio\songs\track1.m4a -OutputFile C:\audio\samples\track1_sample.m4a
#>
param(
    [Parameter(Mandatory = $true, Position = 0, HelpMessage = "Path to the input audio file.")]
    [string]$InputFile,

    [Parameter(Mandatory = $false, Position = 1, HelpMessage = "Path for the output sample file.")]
    [string]$OutputFile
)

# 1. Check if ffmpeg is available
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "ffmpeg command not found. Please ensure ffmpeg is installed and its location is in your system's PATH."
    exit 1
}

# 2. Resolve and validate the input file path
$resolvedInputFile = Resolve-Path -Path $InputFile -ErrorAction SilentlyContinue
if (-not $resolvedInputFile) {
    Write-Error "Input file not found at path: $InputFile"
    exit 1
}

# 3. Determine the output file path
if ([string]::IsNullOrEmpty($OutputFile)) {
    $inputFileObject = Get-Item $resolvedInputFile
    $baseName = $inputFileObject.BaseName
    $extension = $inputFileObject.Extension
    $directory = $inputFileObject.DirectoryName
    $OutputFile = Join-Path -Path $directory -ChildPath "${baseName}_sample${extension}"
} else {
    $OutputFile = Resolve-Path -Path $OutputFile -ErrorAction SilentlyContinue
    if (!$OutputFile) {
        # If a relative path was provided that doesn't exist, create it relative to current location
        $OutputFile = Join-Path -Path (Get-Location) -ChildPath $OutputFile
    }
}

# 4. Define the sample duration
$duration = "00:05:00" # 5 minutes

# 5. Execute the ffmpeg command
Write-Host "Input:  $resolvedInputFile"
Write-Host "Output: $OutputFile"
Write-Host "Creating 5-minute audio sample..."

# Use -c copy to avoid re-encoding. It's much faster.
# Use -y to overwrite the output file without prompting.
$ffmpegCommand = "ffmpeg -i `"$resolvedInputFile`" -ss 00:00:00 -t $duration -c copy `"$OutputFile`" -y"

Invoke-Expression -Command $ffmpegCommand -ErrorAction Stop

Write-Host "`n[SUCCESS] Sample created successfully: $OutputFile" -ForegroundColor Green
