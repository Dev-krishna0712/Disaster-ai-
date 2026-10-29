"""
Disaster AI Supervised Fine-Tuning (SFT) + LoRA / QLoRA Pipeline
Fine-tunes Qwen2.5 on curated bilingual disaster management datasets.
Supports CUDA GPU (4-bit QLoRA) and CPU fallback mode.
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, TaskType

def load_config(config_path: str = "training/config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def train_sft(config_path: str = "training/config.yaml", quick_run: bool = False):
    config = load_config(config_path)
    model_cfg = config["model"]
    lora_cfg = config["lora"]
    train_cfg = config["training"]
    data_cfg = config["dataset"]

    print("=" * 60)
    print("DISASTER AI — SUPERVISED FINE-TUNING (SFT + LoRA)")
    print(f"Base Model: {model_cfg['base_model_name']}")
    print(f"Device: {'CUDA GPU' if torch.cuda.is_available() else 'CPU'}")
    print("=" * 60)

    # 1. Load Tokenizer
    print("\n[1/5] Loading Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_cfg["base_model_name"],
        trust_remote_code=model_cfg.get("trust_remote_code", True)
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 2. Load Model
    print("\n[2/5] Loading Pretrained Base Model...")
    has_cuda = torch.cuda.is_available()
    torch_dtype = torch.float16 if has_cuda else torch.float32

    # Check for bitsandbytes quantization if CUDA is available
    bnb_config = None
    if has_cuda and config.get("quantization") == "qlora_4bit":
        try:
            from transformers import BitsAndBytesConfig
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True
            )
            print(" -> Enabled 4-bit NormalFloat QLoRA Quantization.")
        except Exception as e:
            print(f" -> BitsAndBytes unavailable ({e}), using standard fp16.")

    model = AutoModelForCausalLM.from_pretrained(
        model_cfg["base_model_name"],
        torch_dtype=torch_dtype,
        quantization_config=bnb_config,
        device_map="auto" if has_cuda else None,
        trust_remote_code=model_cfg.get("trust_remote_code", True)
    )

    # 3. Setup PEFT LoRA Adapter
    print("\n[3/5] Configuring LoRA Adapters...")
    peft_config = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["lora_alpha"],
        lora_dropout=lora_cfg["lora_dropout"],
        target_modules=lora_cfg["target_modules"],
        bias=lora_cfg.get("bias", "none"),
        task_type=TaskType.CAUSAL_LM
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 4. Prepare and Format Datasets
    print("\n[4/5] Formatting and Tokenizing Conversational Dataset...")
    train_dataset = load_dataset("json", data_files=data_cfg["train_path"])["train"]
    val_dataset = load_dataset("json", data_files=data_cfg["validation_path"])["train"]

    max_length = train_cfg.get("max_seq_length", 512)

    def preprocess_function(examples):
        input_ids_list = []
        labels_list = []
        attention_mask_list = []

        for messages in examples["messages"]:
            # Format using tokenizer chat template
            formatted_text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False
            )
            tokens = tokenizer(
                formatted_text,
                truncation=True,
                max_length=max_length,
                padding=False
            )
            input_ids = tokens["input_ids"]
            attention_mask = tokens["attention_mask"]

            input_ids_list.append(input_ids)
            attention_mask_list.append(attention_mask)
            labels_list.append(list(input_ids))

        return {
            "input_ids": input_ids_list,
            "attention_mask": attention_mask_list,
            "labels": labels_list
        }

    tokenized_train = train_dataset.map(preprocess_function, batched=True, remove_columns=train_dataset.column_names)
    tokenized_val = val_dataset.map(preprocess_function, batched=True, remove_columns=val_dataset.column_names)

    epochs = 1 if quick_run else train_cfg.get("num_train_epochs", 3)
    output_dir = train_cfg["output_dir"]
    os.makedirs(output_dir, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=train_cfg.get("per_device_train_batch_size", 2),
        per_device_eval_batch_size=train_cfg.get("per_device_eval_batch_size", 2),
        gradient_accumulation_steps=train_cfg.get("gradient_accumulation_steps", 4),
        learning_rate=float(train_cfg.get("learning_rate", 2e-4)),
        lr_scheduler_type=train_cfg.get("lr_scheduler_type", "cosine"),
        warmup_ratio=train_cfg.get("warmup_ratio", 0.1),
        logging_steps=train_cfg.get("logging_steps", 1),
        save_strategy=train_cfg.get("save_strategy", "epoch"),
        eval_strategy=train_cfg.get("evaluation_strategy", "epoch"),
        fp16=has_cuda,
        bf16=False,
        report_to="none",
        use_cpu=not has_cuda,
        remove_unused_columns=False
    )

    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        padding=True,
        pad_to_multiple_of=8 if has_cuda else None
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        data_collator=data_collator,
    )

    # 5. Execute Training
    print("\n[5/5] Launching Fine-Tuning Execution...")
    start_time = datetime.utcnow()
    train_result = trainer.train()

    # Save final LoRA adapter & Tokenizer
    print(f"\n[OK] Training completed. Saving fine-tuned LoRA adapter to {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    # Save Training Metadata
    metadata = {
        "model_name": "Disaster-AI-Citizen-Assistant-LoRA",
        "base_model": model_cfg["base_model_name"],
        "training_completion_timestamp": datetime.utcnow().isoformat(),
        "training_duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        "train_loss": train_result.training_loss,
        "epochs_completed": epochs,
        "device_used": "CUDA" if has_cuda else "CPU",
        "lora_parameters": lora_cfg,
        "dataset_manifest": data_cfg["manifest_path"]
    }
    with open(os.path.join(output_dir, "training_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Adapter saved successfully with loss: {train_result.training_loss:.4f}")
    return metadata

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Disaster AI SFT + LoRA Training")
    parser.add_argument("--config", default="training/config.yaml", help="Path to config.yaml")
    parser.add_argument("--quick", action="store_true", help="Run 1 quick epoch for validation")
    args = parser.parse_args()

    train_sft(config_path=args.config, quick_run=args.quick)
