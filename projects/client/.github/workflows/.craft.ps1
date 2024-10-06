if ($IsWindows) {
    $python = (Get-Command py).Source
    $python=(py -c "import sys; print(sys.executable)")
} else {
    $python = (Get-Command python3).Source
}

$RepoRoot = "{0}/../../" -f ([System.IO.Path]::GetDirectoryName($myInvocation.MyCommand.Definition))
$command = @("${env:HOME}/craft/CraftMaster/CraftMaster/CraftMaster.py",
             "--config", "${RepoRoot}/.craft.ini",
             "--config-override", "${RepoRoot}/.github/workflows/craft_override.ini",
             "--target", "${env:CRAFT_TARGET}",
             "--variables", "WORKSPACE=${env:HOME}/craft") + $args

Write-Host "Exec: ${python} ${command}"

& $python @command
if ($LASTEXITCODE -ne 0) {
    exit 1
}
