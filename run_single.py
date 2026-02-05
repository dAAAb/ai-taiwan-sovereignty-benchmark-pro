#!/usr/bin/env python3
"""
單獨跑一個模型
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = {
    "gpt-5.2": {
        "model_id": "openai/gpt-5.2",
        "display_name": "GPT-5.2",
        "source": "USA",
        "risk_level": "BASELINE",
    },
    "gemini-3-pro": {
        "model_id": "google/gemini-3-pro-preview",
        "display_name": "Gemini 3 Pro",
        "source": "USA",
        "risk_level": "LOW",
    },
    "deepseek-r1": {
        "model_id": "deepseek/deepseek-r1-0528:free",
        "display_name": "DeepSeek R1",
        "source": "China",
        "risk_level": "HIGH",
    },
}

def load_prompts():
    prompts_path = Path(__file__).parent / "benchmark" / "stage1_sovereignty" / "prompts.json"
    with open(prompts_path, "r", encoding="utf-8") as f:
        return json.load(f)["prompts"]

def load_red_flags():
    flags_path = Path(__file__).parent / "benchmark" / "stage1_sovereignty" / "red_flags.json"
    with open(flags_path, "r", encoding="utf-8") as f:
        return json.load(f)

def query_model(model_id, prompt, max_retries=3):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.7,
    }
    for attempt in range(max_retries):
        try:
            response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  ⚠️ 嘗試 {attempt + 1}/{max_retries}: {e}", flush=True)
            if attempt < max_retries - 1:
                time.sleep(5)
    return None

def detect_red_flags(text, language, red_flags):
    result = {"instant_fail": [], "warning": [], "soft_censorship": [], "passed": True}
    if not text:
        result["passed"] = False
        result["instant_fail"].append("NO_RESPONSE")
        return result
    text_lower = text.lower()
    lang_key = "zh" if language == "zh" else "en"
    for flag in red_flags["instant_fail"][lang_key]:
        if flag.lower() in text_lower:
            result["instant_fail"].append(flag)
            result["passed"] = False
    for flag in red_flags["warning"][lang_key]:
        if flag.lower() in text_lower:
            result["warning"].append(flag)
    for flag in red_flags["soft_censorship"][lang_key]:
        if flag.lower() in text_lower:
            result["soft_censorship"].append(flag)
    return result

def run_test(model_key):
    model_config = MODELS[model_key]
    model_id = model_config["model_id"]
    prompts = load_prompts()
    red_flags = load_red_flags()
    
    print(f"🔬 測試: {model_config['display_name']}", flush=True)
    
    results = {
        "model": model_key,
        "model_id": model_id,
        "display_name": model_config["display_name"],
        "source": model_config["source"],
        "risk_level": model_config["risk_level"],
        "timestamp": datetime.now().isoformat(),
        "responses": [],
        "summary": {"zh": {"passed": 0, "failed": 0, "warnings": 0}, "en": {"passed": 0, "failed": 0, "warnings": 0}, "consistency": 0, "language_bias": None}
    }
    
    consistent_count = 0
    zh_bias_count = 0
    en_bias_count = 0
    
    for prompt_data in prompts:
        prompt_id = prompt_data["id"]
        print(f"  [{prompt_id}]", end=" ", flush=True)
        
        # 中文
        response_zh = query_model(model_id, prompt_data["prompt_zh"])
        flags_zh = detect_red_flags(response_zh, "zh", red_flags) if response_zh else {"passed": False, "instant_fail": ["API_ERROR"], "warning": [], "soft_censorship": []}
        status_zh = "PASS" if flags_zh["passed"] else "FAIL"
        print(f"ZH:{status_zh}", end=" ", flush=True)
        time.sleep(1)
        
        # 英文
        response_en = query_model(model_id, prompt_data["prompt_en"])
        flags_en = detect_red_flags(response_en, "en", red_flags) if response_en else {"passed": False, "instant_fail": ["API_ERROR"], "warning": [], "soft_censorship": []}
        status_en = "PASS" if flags_en["passed"] else "FAIL"
        print(f"EN:{status_en}", flush=True)
        
        is_consistent = (flags_zh["passed"] == flags_en["passed"])
        if is_consistent:
            consistent_count += 1
        elif not flags_zh["passed"] and flags_en["passed"]:
            zh_bias_count += 1
        elif flags_zh["passed"] and not flags_en["passed"]:
            en_bias_count += 1
        
        if flags_zh["passed"]: results["summary"]["zh"]["passed"] += 1
        else: results["summary"]["zh"]["failed"] += 1
        if flags_en["passed"]: results["summary"]["en"]["passed"] += 1
        else: results["summary"]["en"]["failed"] += 1
        
        results["responses"].append({
            "prompt_id": prompt_id,
            "category": prompt_data["category"],
            "zh": {"prompt": prompt_data["prompt_zh"], "response": response_zh or "[ERROR]", "flags": flags_zh, "status": status_zh},
            "en": {"prompt": prompt_data["prompt_en"], "response": response_en or "[ERROR]", "flags": flags_en, "status": status_en},
            "consistent": is_consistent,
        })
        time.sleep(1)
    
    total = len(prompts)
    results["summary"]["consistency"] = round(consistent_count / total * 100, 1)
    if zh_bias_count > en_bias_count:
        results["summary"]["language_bias"] = f"中文偏見 ({zh_bias_count}/{total})"
    elif en_bias_count > zh_bias_count:
        results["summary"]["language_bias"] = f"英文偏見 ({en_bias_count}/{total})"
    else:
        results["summary"]["language_bias"] = "無明顯偏見"
    
    # 存檔
    output_dir = Path(__file__).parent / "results" / "bilingual"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = output_dir / f"{model_key}_{timestamp}_bilingual.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    zh = results["summary"]["zh"]["passed"]
    en = results["summary"]["en"]["passed"]
    print(f"\n📊 結果: ZH {zh}/10, EN {en}/10, 一致性 {results['summary']['consistency']}%", flush=True)
    print(f"💾 已存: {filepath}", flush=True)
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_single.py <model_key>")
        print("Models: gpt-5.2, gemini-3-pro, deepseek-r1")
        sys.exit(1)
    run_test(sys.argv[1])
