Param(
  [string]$Input = ".\data\raw\role_mentor.jsonl",
  [string]$Role = "Mentor",
  [string]$Output = ".\data\processed\mentor.jsonl",
  [double]$Val_Ratio = 0.02
)

python .\src\data\preprocess.py --input $Input --role $Role --output $Output --val_ratio $Val_Ratio
