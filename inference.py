"""
Disaster AI Assistant Inference Script
Loads the fine-tuned LoRA adapter or base model to test safety responses.
"""

import os
import sys
import yaml
import argparse
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

SYSTEM_PROMPT = (
    "You are Disaster AI, an official citizen-safety emergency response assistant. "
    "You provide concise, life-saving, verified disaster guidance based on NDMA and NDRF protocols in English and Hindi. "
    "During life-threatening situations, prioritize immediate human safety, emphasize Helpline 112, "
    "and provide clear, numbered survival steps. Acknowledge uncertainty when details are insufficient and never offer risky advice."
)

class DisasterAIAssistant:
    def __init__(self, config_path: str = "training/config.yaml", adapter_dir: str = None):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.base_model_name = self.config["model"]["base_model_name"]
        self.adapter_dir = adapter_dir or self.config["training"]["output_dir"]
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_fine_tuned = False

        print(f"Initializing Disaster AI Assistant on {self.device.upper()}...")
        self._load_model()

    def _load_model(self):
        # 1. Load Tokenizer
        tokenizer_src = self.adapter_dir if os.path.exists(os.path.join(self.adapter_dir, "tokenizer_config.json")) else self.base_model_name
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_src, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 2. Load Base Model
        has_cuda = torch.cuda.is_available()
        dtype = torch.float16 if has_cuda else torch.float32

        base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            torch_dtype=dtype,
            device_map="auto" if has_cuda else None,
            trust_remote_code=True
        )

        # 3. Check for Fine-Tuned LoRA Adapter
        adapter_config_path = os.path.join(self.adapter_dir, "adapter_config.json")
        if os.path.exists(adapter_config_path):
            print(f"Loading Fine-Tuned LoRA adapter from: {self.adapter_dir}")
            self.model = PeftModel.from_pretrained(base_model, self.adapter_dir)
            self.is_fine_tuned = True
        else:
            print(f"No LoRA adapter found at {self.adapter_dir}. Using Pretrained Base Model: {self.base_model_name}")
            self.model = base_model
            self.is_fine_tuned = False

        if not has_cuda:
            self.model.to(self.device)
        self.model.eval()

    def generate_response(self, user_query: str, history: list = None, max_new_tokens: int = 350) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            for turn in history:
                messages.append(turn)
        messages.append({"role": "user", "content": user_query})

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.3,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.pad_token_id
            )

        # Slice generated response tokens
        generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Disaster AI Inference")
    parser.add_argument("--query", default="Floodwater is entering my ground floor house. What should I do right now?", help="User query")
    parser.add_argument("--config", default="training/config.yaml")
    args = parser.parse_args()

    assistant = DisasterAIAssistant(config_path=args.config)
    print(f"\nModel Status: {'FINE-TUNED ADAPTER ACTIVE' if assistant.is_fine_tuned else 'PRETRAINED BASE MODEL'}")
    print(f"\nUser Query: {args.query}\n")
    resp = assistant.generate_response(args.query)
    print("=" * 50)
    print("Disaster AI Assistant Response:")
    print("=" * 50)
    print(resp)
