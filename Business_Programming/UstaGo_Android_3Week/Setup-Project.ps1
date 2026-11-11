param(
    [Parameter(Mandatory=$true)][string]$TemplatePath,
    [ValidateSet("Week1", "Week2", "Week3")][string]$Week = "Week1",
    [Parameter(Mandatory=$true)][string]$Destination
)
$ErrorActionPreference = "Stop"
$source = Join-Path $PSScriptRoot "projects/$Week"
if (Test-Path $Destination) { throw "Destination already exists. Choose a new folder to preserve your work." }
foreach ($file in @("gradlew", "gradlew.bat", "gradle/wrapper/gradle-wrapper.jar")) {
    if (!(Test-Path (Join-Path $TemplatePath $file))) { throw "Missing template wrapper file: $file" }
}
New-Item -ItemType Directory -Path $Destination | Out-Null
Get-ChildItem -Force $source | Copy-Item -Destination $Destination -Recurse -Force
foreach ($file in @("gradlew", "gradlew.bat", "gradle/wrapper/gradle-wrapper.jar")) {
    Copy-Item (Join-Path $TemplatePath $file) (Join-Path $Destination $file) -Force
}
Write-Host "Prepared $Week at $Destination. Open this folder in Android Studio, choose JDK 17 and sync."
