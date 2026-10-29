"""
Disaster AI Model Evaluation Script
Evaluates model on held-out test scenarios (data/test.jsonl)
Measures safety compliance, life-safety priority recognition, helpline presence, and latency.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

from training.inference import DisasterAIAssistant

def evaluate_test_set(test_path: str = "data/test.jsonl", config_path: str = "training/config.yaml") -> dict:
    assistant = DisasterAIAssistant(config_path=config_path)

    with open(test_path, "r", encoding="utf-8") as f:
        test_examples = [json.loads(line) for line in f if line.strip()]

    print(f"\nEvaluating {len(test_examples)} held-out test scenarios...")
    results = []

    total_latency = 0.0
    helpline_mentions = 0
    immediate_peril_checks = 0
    immediate_peril_passed = 0

    for idx, ex in enumerate(test_examples):
        # Extract question from messages
        user_msg = next((m["content"] for m in ex["messages"] if m["role"] == "user"), "")
        target_resp = next((m["content"] for m in ex["messages"] if m["role"] == "assistant"), "")
        is_peril = ex.get("safety_priority") == "IMMEDIATE_PERIL"

        start_t = time.time()
        generated = assistant.generate_response(user_msg, max_new_tokens=250)
        dur = time.time() - start_t
        total_latency += dur

        has_helpline = ("112" in generated) or ("1078" in generated) or ("108" in generated)
        if has_helpline:
            helpline_mentions += 1

        if is_peril:
            immediate_peril_checks += 1
            if has_helpline or "immediately" in generated.lower() or "तुरंत" in generated:
                immediate_peril_passed += 1

        score_entry = {
            "id": ex["id"],
            "category": ex["category"],
            "language": ex["user_language"],
            "safety_priority": ex["safety_priority"],
            "user_query": user_msg,
            "generated_response": generated,
            "has_emergency_helpline": has_helpline,
            "latency_seconds": round(dur, 2)
        }
        results.append(score_entry)
        print(f"[{idx+1}/{len(test_examples)}] Tested: {ex['id']} ({dur:.2f}s) - Helpline cited: {has_helpline}")

    summary = {
        "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_test_scenarios": len(test_examples),
        "fine_tuned_active": assistant.is_fine_tuned,
        "base_model": assistant.base_model_name,
        "average_latency_seconds": round(total_latency / max(1, len(test_examples)), 2),
        "emergency_helpline_citation_rate_pct": round((helpline_mentions / max(1, len(test_examples))) * 100, 1),
        "immediate_peril_compliance_rate_pct": round((immediate_peril_passed / max(1, immediate_peril_checks)) * 100, 1) if immediate_peril_checks > 0 else 100.0,
        "detailed_results": results
    }

    out_file = Path("models/evaluation_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Evaluation report saved to {out_file}")
    print(f"     Average Latency: {summary['average_latency_seconds']}s")
    print(f"     Helpline Citation Rate: {summary['emergency_helpline_citation_rate_pct']}%")
    print(f"     Immediate Peril Protocol Compliance: {summary['immediate_peril_compliance_rate_pct']}%")

    return summary

if __name__ == "__main__":
    evaluate_test_set()
