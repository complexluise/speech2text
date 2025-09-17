#Requires -Version 5.0
<#
.SYNOPSIS
    Splits an audio file into multiple parts of a specified duration.

.DESCRIPTION
    This script uses ffmpeg to split an audio file into smaller segments.
    The output files will be saved in the same directory as the input file,
    with a suffix like '_part_1.wav', '_part_2.wav', etc.

.PARAMETER InputFile
    The absolute or relative path to the source audio file (e.g., .m4a, .mp3, .wav).

.PARAMETER SplitTime
    The duration for each split part, in HH:mm:ss format (e.g., '00:05:00' for 5 minutes).
    Default is 5 minutes.
.EXAMPLE
    ./split_audio.ps1 -InputFile .\my-long-audio.m4a -SplitTime 00:10:00

.EXAMPLE
    ./split_audio.ps1 -InputFile C:\audio\songs\track1.m4a
#>
param(
    [Parameter(Mandatory = $true, Position = 0, HelpMessage = "Path to the input audio file.")]
    [string]$InputFile,

    [Parameter(Mandatory = $false, Position = 1, HelpMessage = "Duration for each split part (HH:mm:ss).")]
    [string]$SplitTime = "00:05:00"
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

# 3. Determine the output file path format
$inputFileObject = Get-Item $resolvedInputFile
$baseName = $inputFileObject.BaseName
$directory = $inputFileObject.DirectoryName
$outputFileTemplate = Join-Path -Path $directory -ChildPath "${baseName}_part_%03d.wav"

# 4. Execute the ffmpeg command to split the audio
Write-Host "Input:      $resolvedInputFile"
Write-Host "Split Time: $SplitTime"
Write-Host "Output:     $directory"
Write-Host "Splitting audio file..."

# -f segment: Specifies the segment muxer
# -segment_time: Duration of each segment
# -reset_timestamps 1: Resets timestamps at the beginning of each segment
# %03d: Creates a sequence of numbers with 3 digits (001, 002, ...)
$ffmpegCommand = "ffmpeg -i `"$resolvedInputFile`" -f segment -segment_time $SplitTime -ar 16000 -ac 1 `"$outputFileTemplate`" -y"

Invoke-Expression -Command $ffmpegCommand -ErrorAction Stop

Write-Host "\n[SUCCESS] Audio file split successfully in: $directory" -ForegroundColor Green
