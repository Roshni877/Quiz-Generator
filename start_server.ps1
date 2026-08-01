# PowerShell script to start the Flask server and open browser
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $projectDir
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "app.py" -WindowStyle Normal
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:5000"
