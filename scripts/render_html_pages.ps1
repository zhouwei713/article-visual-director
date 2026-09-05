[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$InputDir,
  [Parameter(Mandatory = $true)]
  [string]$OutputDir,
  [int]$Width = 1080,
  [int]$Height = 1440,
  [Alias('Pages')]
  [string[]]$IncludePage = @()
)

$inputRoot = (Resolve-Path -LiteralPath $InputDir -ErrorAction Stop).Path
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$outputRoot = (Resolve-Path -LiteralPath $OutputDir -ErrorAction Stop).Path
$npxCommand = (Get-Command npx -ErrorAction Stop).Source
$playwrightCliPackage = '@playwright/cli@0.1.19'
$renderHelper = Join-Path $PSScriptRoot 'render_html_pages.js'
$session = "article-visual-director-$([Guid]::NewGuid().ToString('N'))"
$pages = @(Get-ChildItem -LiteralPath $inputRoot -Filter '*.html' -File | Sort-Object Name)
$requestedPages = @($IncludePage | ForEach-Object { [System.IO.Path]::GetFileNameWithoutExtension($_) })
if ($requestedPages.Count -gt 0) {
  $pages = @($pages | Where-Object { $requestedPages -contains $_.BaseName })
}
$serverRoot = Split-Path -Parent $inputRoot
$pythonCommand = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonCommand) {
  $pythonCommand = (Get-Command py -ErrorAction Stop).Source
}
$serverProcess = $null

if ($pages.Count -eq 0) {
  throw "No matching HTML pages found in $inputRoot"
}

function Invoke-PlaywrightCli {
  param([string[]]$Arguments)
  & $npxCommand --yes --package $playwrightCliPackage playwright-cli --session $session @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Playwright CLI failed with exit code $LASTEXITCODE"
  }
}

try {
  $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
  $listener.Start()
  $port = ([System.Net.IPEndPoint]$listener.LocalEndpoint).Port
  $listener.Stop()

  $serverProcess = Start-Process -FilePath $pythonCommand -ArgumentList @('-m', 'http.server', $port.ToString(), '--bind', '127.0.0.1') -WorkingDirectory $serverRoot -WindowStyle Hidden -PassThru
  $serverReady = $false
  for ($attempt = 0; $attempt -lt 40; $attempt++) {
    try {
      $client = [System.Net.Sockets.TcpClient]::new()
      $client.Connect('127.0.0.1', $port)
      $client.Dispose()
      $serverReady = $true
      break
    }
    catch {
      Start-Sleep -Milliseconds 150
    }
  }
  if (-not $serverReady) {
    throw "Local HTML server did not start"
  }

  $jobs = @($pages | ForEach-Object {
    $page = $_
    $relativePage = $page.FullName.Substring($serverRoot.Length).TrimStart('\', '/').Replace('\', '/')
    $urlParts = $relativePage.Split('/') | ForEach-Object { [System.Uri]::EscapeDataString($_) }
    [ordered]@{
      name = $page.Name
      url = "http://127.0.0.1:$port/" + ($urlParts -join '/')
      output = Join-Path $outputRoot ($page.BaseName + '.png')
    }
  })
  $jobsJson = ConvertTo-Json $jobs -Compress
  $encodedJobs = [System.Uri]::EscapeDataString($jobsJson)
  Invoke-PlaywrightCli @('open', "about:blank#$encodedJobs")
  Invoke-PlaywrightCli @('resize', $Width.ToString(), $Height.ToString())
  Invoke-PlaywrightCli @('run-code', '--filename', $renderHelper)
  foreach ($page in $pages) {
    Write-Output ("RENDER_PASS {0}" -f $page.Name)
  }
}
finally {
  & $npxCommand --yes --package $playwrightCliPackage playwright-cli --session $session close 2>$null | Out-Null
  if ($serverProcess -and -not $serverProcess.HasExited) {
    Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    $serverProcess.WaitForExit()
  }
}
