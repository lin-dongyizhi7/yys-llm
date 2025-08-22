Param(
  [string]$BaseModel = "Qwen/Qwen2-1.5B-Instruct",
  [string]$Dataset = ".\data\processed\mentor.jsonl",
  [string]$Role = "Mentor",
  [string]$OutputDir = ".\models\mentor",
  [int]$Epochs = 3,
  [int]$BatchSize = 2,
  [double]$LR = 2e-4,
  [int]$CutoffLen = 2048,
  [string]$Quant = "4bit"
)

python .\src\train\train_lora.py --base_model $BaseModel --dataset $Dataset --role $Role --output_dir $OutputDir --epochs $Epochs --batch_size $BatchSize --lr $LR --cutoff_len $CutoffLen --quant $Quant
