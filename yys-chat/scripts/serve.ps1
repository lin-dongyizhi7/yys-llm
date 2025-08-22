Param(
  [int]$Port = 7860,
  [bool]$Share = $false
)

$shareFlag = if ($Share) { "--share true" } else { "--share false" }
python .\src\serve\app.py --port $Port $shareFlag
