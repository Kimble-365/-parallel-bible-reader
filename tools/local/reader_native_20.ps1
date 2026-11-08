# PowerShell 7: inspect tools, validate the reader, or build the current host app.
[CmdletBinding()]
param([ValidateSet('Tools','Check','Build')][string]$Task = 'Tools')
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'PowerShell 7 or later is required.' }
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Command failed with exit code $LASTEXITCODE" }
}
Push-Location $repo
try {
    if ($Task -eq 'Tools') {
        $PSVersionTable.PSVersion.ToString()
        Invoke-Checked -Command rustc -Arguments @('--version')
        Invoke-Checked -Command cargo -Arguments @('--version')
        Invoke-Checked -Command rustfmt -Arguments @('--version')
        Invoke-Checked -Command cargo -Arguments @('clippy','--version')
        Invoke-Checked -Command node -Arguments @('--version')
        Invoke-Checked -Command npm -Arguments @('--version')
        Invoke-Checked -Command python -Arguments @('--version')
        Invoke-Checked -Command python -Arguments @('-c','import sqlite3,unicodedata; print("SQLite",sqlite3.sqlite_version,"Unicode",unicodedata.unidata_version)')
    } elseif ($Task -eq 'Check') {
        Invoke-Checked -Command node -Arguments @('tests/native_20.cjs')
        Invoke-Checked -Command cargo -Arguments @('fmt','--manifest-path','apps/native-20/src-tauri/Cargo.toml','--','--check')
        Invoke-Checked -Command python -Arguments @('tests/toolchain_20.py')
    } else {
        Set-Location (Join-Path $repo 'apps/native-20')
        Invoke-Checked -Command npm -Arguments @('ci','--ignore-scripts')
        Invoke-Checked -Command npm -Arguments @('run','tauri','--','icon','../../releases/v2.0/icons/icon-512.png')
        # Builds only. No install, deployment, store upload or signing credentials.
        $bundle = if ($IsWindows) { 'nsis' } elseif ($IsMacOS) { 'app' } else { throw 'Use a Windows or Mac host for this desktop build.' }
        Invoke-Checked -Command npm -Arguments @('run','tauri','--','build','--ci','--debug','--bundles',$bundle,'--no-sign')
    }
} finally { Pop-Location }
