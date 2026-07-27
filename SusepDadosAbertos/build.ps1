$exclude = @("venv", "SusepDadosAbertos.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "SusepDadosAbertos.zip" -Force