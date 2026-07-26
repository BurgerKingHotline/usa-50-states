param(
    [string]$OutputDirectory = (
        Join-Path $PSScriptRoot '..\..\gfx\interface\elections'
    )
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing

function New-Color {
    param([int]$A, [int]$R, [int]$G, [int]$B)
    return [System.Drawing.Color]::FromArgb($A, $R, $G, $B)
}

function Set-PixelSafe {
    param(
        [System.Drawing.Bitmap]$Bitmap,
        [int]$X,
        [int]$Y,
        [System.Drawing.Color]$Color
    )

    if ($X -ge 0 -and $X -lt $Bitmap.Width -and $Y -ge 0 -and $Y -lt $Bitmap.Height) {
        $Bitmap.SetPixel($X, $Y, $Color)
    }
}

function Draw-MeterFrame {
    param(
        [System.Drawing.Bitmap]$Bitmap,
        [int]$OriginX,
        [int]$Width,
        [int]$Height
    )

    $black = New-Color 255 3 5 4
    $shadow = New-Color 255 30 36 33
    $edge = New-Color 255 91 103 95
    $highlight = New-Color 255 139 151 140

    for ($x = 0; $x -lt $Width; $x++) {
        Set-PixelSafe $Bitmap ($OriginX + $x) 0 $black
        Set-PixelSafe $Bitmap ($OriginX + $x) ($Height - 1) $black
    }
    for ($y = 0; $y -lt $Height; $y++) {
        Set-PixelSafe $Bitmap $OriginX $y $black
        Set-PixelSafe $Bitmap ($OriginX + $Width - 1) $y $black
    }
    for ($x = 1; $x -lt ($Width - 1); $x++) {
        Set-PixelSafe $Bitmap ($OriginX + $x) 1 $highlight
        Set-PixelSafe $Bitmap ($OriginX + $x) ($Height - 2) $shadow
    }
    for ($y = 1; $y -lt ($Height - 1); $y++) {
        Set-PixelSafe $Bitmap ($OriginX + 1) $y $edge
        Set-PixelSafe $Bitmap ($OriginX + $Width - 2) $y $shadow
    }
}

function Draw-Meter {
    param(
        [System.Drawing.Bitmap]$Bitmap,
        [int]$OriginX,
        [int]$Width,
        [int]$Height,
        [int]$Percent
    )

    $innerLeft = $OriginX + 2
    $innerTop = 2
    $innerWidth = $Width - 4
    $innerHeight = $Height - 4
    $fillWidth = [Math]::Round($innerWidth * $Percent / 100.0)

    $troughTop = New-Color 255 26 31 28
    $troughBottom = New-Color 255 10 13 11
    $divider = New-Color 120 72 81 74
    $fillTop = New-Color 255 113 159 103
    $fillMid = New-Color 255 72 126 69
    $fillBottom = New-Color 255 38 79 43
    $stripe = New-Color 190 168 197 151

    for ($y = 0; $y -lt $innerHeight; $y++) {
        $mix = if ($innerHeight -le 1) { 0.0 } else { $y / ($innerHeight - 1.0) }
        $r = [Math]::Round($troughTop.R * (1 - $mix) + $troughBottom.R * $mix)
        $g = [Math]::Round($troughTop.G * (1 - $mix) + $troughBottom.G * $mix)
        $b = [Math]::Round($troughTop.B * (1 - $mix) + $troughBottom.B * $mix)
        $rowColor = New-Color 255 $r $g $b
        for ($x = 0; $x -lt $innerWidth; $x++) {
            Set-PixelSafe $Bitmap ($innerLeft + $x) ($innerTop + $y) $rowColor
        }
    }

    for ($x = 15; $x -lt $innerWidth; $x += 15) {
        for ($y = 0; $y -lt $innerHeight; $y++) {
            Set-PixelSafe $Bitmap ($innerLeft + $x) ($innerTop + $y) $divider
        }
    }

    for ($y = 0; $y -lt $innerHeight; $y++) {
        $rowColor = if ($y -eq 0) {
            $fillTop
        } elseif ($y -ge ($innerHeight - 2)) {
            $fillBottom
        } else {
            $fillMid
        }
        for ($x = 0; $x -lt $fillWidth; $x++) {
            Set-PixelSafe $Bitmap ($innerLeft + $x) ($innerTop + $y) $rowColor
        }
    }

    for ($x = 0; $x -lt $fillWidth; $x++) {
        $stripeY = ($innerHeight - 1) - (($x + 2) % 8)
        if ($stripeY -ge 1 -and $stripeY -lt ($innerHeight - 1)) {
            Set-PixelSafe $Bitmap ($innerLeft + $x) ($innerTop + $stripeY) $stripe
        }
    }
}

function Save-Png {
    param([System.Drawing.Bitmap]$Bitmap, [string]$Path)
    $Bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
}

function New-MeterStrip {
    param([int]$FrameWidth, [int]$FrameHeight, [string]$Path)

    $strip = [System.Drawing.Bitmap]::new(
        $FrameWidth * 101,
        $FrameHeight,
        [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
    )
    try {
        for ($frame = 0; $frame -le 100; $frame++) {
            $originX = $frame * $FrameWidth
            Draw-Meter $strip $originX $FrameWidth $FrameHeight $frame
        }
        Save-Png $strip $Path
    }
    finally {
        $strip.Dispose()
    }
}

function New-MeterFrameImage {
    param([int]$Width, [int]$Height, [string]$Path)

    $frame = [System.Drawing.Bitmap]::new(
        $Width,
        $Height,
        [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
    )
    try {
        Draw-MeterFrame $frame 0 $Width $Height
        Save-Png $frame $Path
    }
    finally {
        $frame.Dispose()
    }
}

$resolvedOutput = [System.IO.Path]::GetFullPath($OutputDirectory)
[System.IO.Directory]::CreateDirectory($resolvedOutput) | Out-Null

New-MeterStrip 150 14 (Join-Path $resolvedOutput 'bar_small_101.png')
New-MeterFrameImage 150 14 (Join-Path $resolvedOutput 'bar_small_frame.png')
New-MeterStrip 160 8 (Join-Path $resolvedOutput 'bar_national_101.png')
New-MeterFrameImage 400 20 (Join-Path $resolvedOutput 'bar_national_frame.png')

Write-Output "Generated election progress bars in $resolvedOutput"
