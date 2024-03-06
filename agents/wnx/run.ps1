# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

if ((get-host).version.major -lt 7) {
    Write-Host "PowerShell version 7 or higher is required." -ForegroundColor Red
    exit
}


# Check for arguments and set flags
$argAll = $false
$argClean = $false
$argSetup = $false
$argFormat = $false
$argCheckFormat = $false
$argCtl = $false
$argBuild = $false
$argTest = $false
$argSign = $false
$argMsi = $false
$argOhm = $false
$argExt = $false
$argSql = $false
$argDoc = $false
$argDetach = $false

$msbuild_exe = "C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\msbuild.exe"
$arte = "$pwd/../../artefacts"
$build_dir = "$pwd/build"
$ohm_dir = "$build_dir/ohm/"
$env:ExternalCompilerOptions = "/DDECREASE_COMPILE_TIME"
$hash_file = "$arte\windows_files_hashes.txt"
$usbip_exe = "c:\common\usbip-win-0.3.6-dev\usbip.exe"
$make_exe = where.exe make | Out-String


if ("$env:arg_var_value" -eq "") {
    $env:arg_val_name = $env:arg_var_value
}
else {
    $env:arg_val_name = ""
}

function Write-Help() {
    $x = Get-Item $PSCommandPath
    $x.BaseName
    $name = "powershell -File " + $x.BaseName + ".ps1"

    Write-Host "Usage:"
    Write-Host ""
    Write-Host "$name [arguments]"
    Write-Host ""
    Write-Host "Available arguments:"
    Write-Host "  -?, -h, --help       display help and exit"
    Write-Host "  -A, --all            shortcut to -S -B -E -C -T -M:  setup, build, ctl, ohm, unit, msi, extensions"
    Write-Host "  -c, --clean          clean literally all, use with care"
    Write-Host "  --clean-artifacts    clean artifacts"
    Write-Host "  -S, --setup          check setup"
    Write-Host "  -C, --ctl            build controller"
    Write-Host "  -D, --documentation  create documentation"
    Write-Host "  -f, --format         format sources"
    Write-Host "  -F, --check-format   check for correct formatting"
    Write-Host "  -B, --build          build controller"
    Write-Host "  -M, --msi            build msi"
    Write-Host "  -O, --ohm            build ohm"
    Write-Host "  -E, --extensions     build extensions"
    Write-Host "  -T, --test           run unit test controller"
    Write-Host "  --sign file secret   sign controller with file in c:\common and secret"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host ""
    Write-Host "$name --ctl"
    Write-Host "$name --build --test"
    Write-Host "$name --build -T --sign the_file secret"
    Write-Host "$name -A"
}


if ($args.Length -eq 0) {
    Write-Host "No arguments provided. Running with default flags." -ForegroundColor Yellow
    $argAll = $true
}
else {
    for ($i = 0; $i -lt $args.Length; $i++) {
        switch ($args[$i]) {
            { $("-h", "--help") -contains "$_" } { Write-Help; return }
            { $("-A", "--all") -contains $_ } { $argAll = $true }
            { $("-c", "--clean") -contains $_ } { $argClean = $true; $argCleanArtifacts = $true }
            { $("-S", "--setup") -contains $_ } { $argSetup = $true }
            { $("-f", "--format") -contains $_ } { $argFormat = $true }
            { $("-F", "--check-format") -contains $_ } { $argCheckFormat = $true }
            { $("-C", "--controller") -contains $_ } { $argCtl = $true }
            { $("-B", "--build") -contains $_ } { $argBuild = $true }
            { $("-M", "--msi") -contains $_ } { $argMsi = $true }
            { $("-O", "--ohm") -contains $_ } { $argOhm = $true }
            { $("-Q", "--mk-sql") -contains $_ } { $argSql = $true }
            { $("-E", "--extensions") -contains $_ } { $argExt = $true }
            { $("-T", "--test") -contains $_ } { $argTest = $true }
            { $("-D", "--documentation") -contains $_ } { $argDoc = $true }
            "--clean-artifacts" { $argCleanArtifacts = $true }
            "--detach" { $argDetach = $true }
            "--var" {
                [Environment]::SetEnvironmentVariable($args[++$i], $args[++$i])
            }
            "--sign" { 
                $argSign = $true
                $argSignFile = $args[++$i]
                $argSignSecret = $args[++$i]
            }
        }
    }
}


if ($argAll) {
    $argCtl = $true
    $argBuild = $true
    $argTest = $true
    $argSetup = $true
    $argOhm = $true
    $argSql = $true
    $argExt = $true  
    $argMsi = $true
}


# Example of setting environment variables (equivalent to SETLOCAL in batch)
$env:LOGONSERVER = "YourLogonServerHere"
$env:USERNAME = "YourUsernameHere"

function Invoke-CheckApp( [String]$title, [String]$cmdline ) {
    try {
        Invoke-Expression $cmdline > $null
        if ($LASTEXITCODE -ne 0) {
            throw
        }
        Write-Host "[+] $title" -Fore Green
    }
    catch {
        Write-Host "[-] $title :$_" -Fore Red
        Exit 55
    }
}

function Get-Version {
    $first_line = Get-Content -Path "include\common\wnx_version.h" -TotalCount 1
    if ($first_line.Substring(0, 29) -eq "#define CMK_WIN_AGENT_VERSION") {
        return $first_line.Substring(30, $first_line.Length - 30)
    }

    Write-Error "wnx_version not found in include\common\wnx_version.h" -ErrorAction Stop
}

function Build-Agent {
    if ($argBuild -ne $true) {
        Write-Host "Skipping Agent build..." -ForegroundColor Yellow
        return
    }

    Write-Host "Building agent..." -ForegroundColor White
    $env:msbuild_exe = $msbuild_exe
    $env:make_exe = $make_exe.trim()
    $env:wnx_version = Get-Version
    Write-Host "Used version: $env:wnx_version"
    Write-Host make is $env:make_exe 
    Write-Host "Start build" -ForegroundColor White
    & "$PSScriptRoot\parallel.ps1"
    if ($lastexitcode -ne 0) {
        Write-Error "Failed to build Agent, error code is $LASTEXITCODE" -ErrorAction Stop
    }

    Write-Host "Success building agent" -ForegroundColor Green
}

function Build-Package([bool]$exec, [System.IO.FileInfo]$dir, [string]$name, [string]$cmd) {
    if ($exec -ne $true) {
        Write-Host "Skipping $name build..." -ForegroundColor Yellow
        return
    }

    Write-Host "Building $name..." -ForegroundColor White
    $cwd = Get-Location
    Set-Location "../../packages/$dir"
    & ./run.cmd $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error building $name, error code is $LASTEXITCODE" -ErrorAction Stop
    }
    Set-Location $cwd
    Write-Host "Success building $name :" -foreground Green
}

function Build-Ext {
    if ($argExt -ne $true) {
        Write-Host "Skipping Ext build..." -ForegroundColor Yellow
        return
    }
    Write-Host "Building Ext..." -ForegroundColor White
    $cwd = Get-Location
    Set-Location "extensions\robotmk_ext"
    & ../../scripts/cargo_build_robotmk.cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error building Ext, error code is $LASTEXITCODE" -ErrorAction Stop
    }

    Write-Host "Success building Ext" -foreground Green
    Set-Location $cwd
}

function Build-OHM() {
    if ($argOhm -ne $true) {
        Write-Host "Skipping OHM build..." -ForegroundColor Yellow
        return
    }
    Write-Host "Building OHM..." -ForegroundColor White
    & $msbuild_exe .\ohm\ohm.sln "/p:OutDir=$ohm_dir;TargetFrameworkVersion=v4.6;Configuration=Release"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error building OHM, error code is $LASTEXITCODE" -ErrorAction Stop
    }

    Write-Host "Uploading OHM" -foreground Green
    Copy-Item "$ohm_dir/OpenHardwareMonitorLib.dll" $arte -Force -ErrorAction Stop
    Copy-Item "$ohm_dir/OpenHardwareMonitorCLI.exe" $arte -Force -ErrorAction Stop
    Write-Host "Success building OHM" -foreground Green
}

function Build-MSI {
    if ($argMsi -ne $true) {
        Write-Host "Skipping Ext build..." -ForegroundColor Yellow
        return
    }
    Write-Host "Building MSI..." -ForegroundColor White
    Remove-Item "$build_dir/install/Release/check_mk_service.msi" -Force -ErrorAction SilentlyContinue

    & $msbuild_exe wamain.sln "/t:install" "/p:Configuration=Release,Platform=x86"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error building MSI, error code is $LASTEXITCODE" -ErrorAction Stop
    }
    Write-Host "Success building MSI" -foreground Green
}


function Invoke-ChangeMsiProperties([string]$file, $version) {
    $Installer = new-object -comobject WindowsInstaller.Installer
    $MSIOpenDatabaseModeTransact = 2
    $MsiFilePath = $file

    $MsiDBCom = $Installer.GetType().InvokeMember(
        "OpenDatabase",
        "InvokeMethod",
        $Null,
        $Installer,
        @($MsiFilePath, $MSIOpenDatabaseModeTransact)
    )
    $query = "UPDATE `Property` SET `Property`.`Value`='$version_base' WHERE `Property`.`Property`='ProductVersion'"
    $Insert = $MsiDBCom.GetType().InvokeMember("OpenView", "InvokeMethod", $Null, $MsiDBCom, ($query))
    $Insert.GetType().InvokeMember("Execute", "InvokeMethod", $Null, $Insert, $Null)
    $Insert.GetType().InvokeMember("Close", "InvokeMethod", $Null, $Insert, $Null)
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($Insert) | Out-Null

    $MsiDBCom.GetType().InvokeMember("Commit", "InvokeMethod", $Null, $MsiDBCom, $Null)
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($MsiDBCom) | Out-Null
}

function Set-MSI-Version {
    if ($argMsi -ne $true) {
        Write-Host "Skipping Set MSI version..." -ForegroundColor Yellow
        return
    }

    $version = Get-Version
    $version_base = $version.substring(1, $version.length - 2)
    Write-Host "Setting MSI version: $version_base" -ForegroundColor White
    Invoke-ChangeMsiProperties $build_dir\install\Release\check_mk_service.msi $version_base
    # deprecated:
    # & echo cscript.exe //nologo scripts\WiRunSQL.vbs $build_dir\install\Release\check_mk_service.msi "UPDATE `Property` SET `Property`.`Value`='$version_base' WHERE `Property`.`Property`='ProductVersion'"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error setting version MSI, error code is $LASTEXITCODE" -ErrorAction Stop
    }
    Write-Host "Success setting version MSI" -foreground Green
}

function Start-Unit-Tests {
    if ($argTest -ne $true) {
        Write-Host "Skipping Unit testing..." -ForegroundColor Yellow
        return
    }
    Write-Host "Running unit tests..." -ForegroundColor White
    & net stop WinRing0_1_2_0
    Copy-Item $build_dir/watest/Win32/Release/watest32.exe $arte -Force -ErrorAction Stop
    Copy-Item $build_dir/watest/x64/Release/watest64.exe $arte -Force -ErrorAction Stop
    & ./call_unit_tests.cmd -*_Simulation:*Component:*ComponentExt:*Flaky
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error Unit Testing, error code is $LASTEXITCODE" -ErrorAction Stop
    }
    Write-Host "Success unittests" -foreground Green
}

function Invoke-Attach {
    if ($argSign -ne $true) {
        return
    }
    & ./scripts/attach.ps1 "$usbip_exe" "yubi-usbserver.lan.checkmk.net" "1-1.2"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to attach USB token" $LASTEXITCODE -foreground Red
        return $False
    }
    Write-Host "Attached!" -ForegroundColor Green
    return $True
}


function Start-BinarySigning {
    if ($argSign -ne $true) {
        Write-Host "Skipping Signing..." -ForegroundColor Yellow
        return
    }
    Write-Host "Binary signing..." -ForegroundColor White
    & $msbuild_exe wamain.sln "/t:install" "/p:Configuration=Release,Platform=x86"
    if ($LASTEXITCODE -ne 0 ) {
        Write-Error "Build Failed, error code is $LASTEXITCODE" -ErrorAction Stop
    }

    $attached = Invoke-Attach
    if ($attached -ne $True) {
        Write-Host "Failed to attach USB token" $LASTEXITCODE -foreground Red
        return
    }
    Remove-Item $hash_file -Force

    $files_to_sign = @(
        "$build_dir/check_mk_service/x64/Release/check_mk_service64.exe",
        "$build_dir/check_mk_service/Win32/Release/check_mk_service32.exe",
        "$arte/cmk-agent-ctl.exe",
        "$arte/cmk-sql.exe",
        "$ohm_dir/OpenHardwareMonitorLib.dll",
        "$ohm_dir/OpenHardwareMonitorCLI.exe"
    )

    foreach ($file in $files_to_sign) {
        & ./scripts/sign_code.cmd $file $hash_file
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Error Signing, error code is $LASTEXITCODE" -ErrorAction Stop
        }
    }
    Write-Host "Success binary signing" -foreground Green
}


function Start-ArtifactUploading {
    if ($argMsi -ne $true) {
        Write-Host "Skipping upload to artifacts..." -ForegroundColor Yellow
        return
    }

    Write-Host "Artifact upload..." -ForegroundColor White
    $artifacts = @(
        @("$build_dir/install/Release/check_mk_service.msi", "$arte/check_mk_agent.msi"),
        @("$build_dir/check_mk_service/x64/Release/check_mk_service64.exe", "$arte/check_mk_agent-64.exe"),
        @("$build_dir/check_mk_service/Win32/Release/check_mk_service32.exe", "$arte/OpenHardwareMonitorCLI.exe"),
        @("$build_dir/ohm/OpenHardwareMonitorCLI.exe", "$arte/OpenHardwareMonitorCLI.exe"),
        @("$build_dir/ohm/OpenHardwareMonitorLib.dll", "$arte/OpenHardwareMonitorLib.dll"),
        @("./install/resources/check_mk.user.yml", "$arte/check_mk.user.yml"),
        @("./install/resources/check_mk.yml", "$arte/check_mk.yml")
    )
    foreach ($artifact in $artifacts) {
        Copy-Item $artifact[0] $artifact[1] -Force -ErrorAction Stop
    }
    Write-Host "Success artifact uploading" -foreground Green
}


function Start-MsiPatching {
    if ($argMsi -ne $true) {
        Write-Host "Skipping MSI patching..." -ForegroundColor Yellow
        return
    }

    Write-Host "MSI Patching..." -ForegroundColor White
    & "$make_exe" msi_patch
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to patch MSI " $LASTEXITCODE -ErrorAction Stop
    }
    Copy-Item $arte/check_mk_agent.msi $arte/check_mk_agent_unsigned.msi -Force
    Write-Host "Success artifact uploading" -foreground Green
}

function Invoke-Detach {
    if ($argSign -ne $true) {
        return
    }
    & $usbip_exe detach -p 00
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to detach " $LASTEXITCODE -foreground Yellow
        return
    }
    Start-Sleep -Seconds 2
    Write-Host "Detached!" -ForegroundColor Green
}



function Start-MsiSigning {
    if ($argSign -ne $true) {
        Write-Host "Skipping MSI signing..." -ForegroundColor Yellow
        return
    }

    Write-Host "MSI signing..." -ForegroundColor White
    & ./scripts/sign_code.cmd $arte/check_mk_agent.msi  $hash_file
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed sign MSI " $LASTEXITCODE -foreground Red
        return
    }
    Invoke-Detach
    & ./scripts/call_signing_tests.cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed test MSI " $LASTEXITCODE -foreground Red
        return
    }
    & py "-3" "./scripts/check_hashes.py" "$hash_file"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed hashing test " $LASTEXITCODE -foreground Red
        return
    }
    powershell Write-Host "MSI signing succeeded" -Foreground Green
}

function Clear-Artifacts() {
    if ($argCleanArtifacts -ne $true) {
        return
    }
    Write-Host "Cleaning artifacts..."
    $masks = "*.msi", "*.exe", "*.log", "*.yml"
    foreach ($mask in $masks) {
        Remove-Item -Path "$arte\$mask" -Force -ErrorAction SilentlyContinue
    }
}

function Clear-All() {
    if ($argClean -ne $true) {
        return
    }

    Write-Host "Cleaning packages..."
    Build-Package $true "cmk-agent-ctl" "Controller" "--clean"
    Build-Package $true "mk-sql" "MK-SQL" "--clean"

    Clear-Artifacts

    Write-Host "Cleaning $build_dir..."
    Remove-Item -Path "$build_dir" -Recurse -Force -ErrorAction SilentlyContinue
}


# Implement other flags and functionality as needed...

Invoke-CheckApp "choco" "choco -v"
Invoke-CheckApp "perl" "perl -v"
Invoke-CheckApp "make" "make -v"
Invoke-CheckApp "msvc" "& ""$msbuild_exe"" --version"
Invoke-CheckApp "is_crlf" "python .\scripts\check_crlf.py"

try {
    $mainStartTime = Get-Date
    Clear-Artifacts
    Clear-All
    Build-Agent
    Build-Package $argCtl "cmk-agent-ctl" "Controller"
    Build-Package $argSql "mk-sql" "MK-SQL"
    Build-Ohm
    Build-Ext
    Build-MSI
    Set-Msi-Version
    Start-Unit-Tests
    Start-BinarySigning
    Start-ArtifactUploading
    Start-MsiPatching
    Start-MsiSigning
    $endTime = Get-Date
    $elapsedTime = $endTime - $mainStartTime
    Write-Host "Elapsed time: $($elapsedTime.Hours):$($elapsedTime.Minutes):$($elapsedTime.Seconds)"
}
catch {
    Write-Host "Error: " $_ -ForegroundColor Red
    Write-Host "Trace stack: " -ForegroundColor Yellow
    Write-Host $_.ScriptStackTrace -ForegroundColor Yellow
}
finally {
    Invoke-Detach
}


