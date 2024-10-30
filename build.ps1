$exclude = @("venv", "bot_teste01.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "bot_teste01.zip" -Force