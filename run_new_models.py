#!/usr/bin/env python3
"""
補跑三個新模型：GPT 5.2, Gemini 3 Pro, DeepSeek R1
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# 要測試的三個新模型
NEW_MODELS = {
    "gpt-5.2": {
        "model_id": "openai/gpt-5.2",
        "provider": "OpenAI",
        "display_name": "GPT-5.2",
        "source": "USA",
        "risk_level": "BASELINE",
    },
    "gemini-3-pro": {
        "model_id": "google/gemini-3-pro-preview",
        "provider": "Google",
        "display_name": "Gemini 3 Pro",
        "source": "USA",
        "risk_level": "LOW",
    },
    "deepseek-r1": {
        "model_id": "deepseek/deepseek-r1-0528:free",
        "provider": "DeepSeek",
        "display_name": "DeepSeek R1",
        "source": "China",
        "risk_level": "HIGH",
    },
}

def load_prompts():
    prompts_path = Path(__file__).parent / "benchmark" / "stage1_sovereignty" / "prompts.json"
    with open(prompts_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["prompts"]

def load_red_flags():
    flags_path = Path(__file__).parent / "benchmark" / "stage1_sovereignty" / "red_flags.json"
    with open(flags_path, "r", encoding="utf-8") as f:
        return json.load(f)

def query_model(model_id, prompt, max_retries=3):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/dAAAb/ai-taiwan-sovereignty-benchmark-pro",
        "X-Title": "Taiwan Sovereignty Benchmark Pro",
    }
    
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.7,
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                OPENROUTER_BASE_URL,
                headers=headers,
                json=payload,
                timeout=120  # 增加超時
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  ⚠️ 嘗試 {attempt + 1}/{max_retries} 失敗: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
    
    return None

def detect_red_flags(text, language, red_flags):
    result = {
        "instant_fail": [],
        "warning": [],
        "soft_censorship": [],
        "passed": True,
    }
    
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

def run_bilingual_test(model_key, prompts, red_flags):
    model_config = NEW_MODELS[model_key]
    model_id = model_config["model_id"]
    
    print(f"\n{'='*60}")
    print(f"🔬 測試模型: {model_config['display_name']}")
    print(f"   Model ID: {model_id}")
    print(f"   來源: {model_config['source']} | 風險: {model_config['risk_level']}")
    print(f"{'='*60}")
    
    results = {
        "model": model_key,
        "model_id": model_id,
        "display_name": model_config["display_name"],
        "source": model_config["source"],
        "risk_level": model_config["risk_level"],
        "timestamp": datetime.now().isoformat(),
        "responses": [],
        "summary": {
            "zh": {"passed": 0, "failed": 0, "warnings": 0},
            "en": {"passed": 0, "failed": 0, "warnings": 0},
            "consistency": 0,
            "language_bias": None,
        }
    }
    
    consistent_count = 0
    zh_bias_count = 0
    en_bias_count = 0
    
    for i, prompt_data in enumerate(prompts):
        prompt_id = prompt_data["id"]
        prompt_zh = prompt_data["prompt_zh"]
        prompt_en = prompt_data["prompt_en"]
        
        print(f"\n📝 [{prompt_id}] {prompt_data['category']}")
        
        # 中文測試
        print(f"   🇹🇼 中文測試...")
        response_zh = query_model(model_id, prompt_zh)
        if response_zh:
            flags_zh = detect_red_flags(response_zh, "zh", red_flags)
            status_zh = "PASS" if flags_zh["passed"] else "FAIL"
            if flags_zh["warning"]:
                status_zh = "WARN" if flags_zh["passed"] else "FAIL"
            print(f"      結果: {status_zh}")
            if flags_zh["instant_fail"]:
                print(f"      ❌ 紅旗: {flags_zh['instant_fail']}")
        else:
            flags_zh = {"passed": False, "instant_fail": ["API_ERROR"], "warning": [], "soft_censorship": []}
            status_zh = "ERROR"
            response_zh = "[API ERROR - No response]"
            print(f"      ❌ API 錯誤")
        
        time.sleep(1)
        
        # 英文測試
        print(f"   🇺🇸 英文測試...")
        response_en = query_model(model_id, prompt_en)
        if response_en:
            flags_en = detect_red_flags(response_en, "en", red_flags)
            status_en = "PASS" if flags_en["passed"] else "FAIL"
            if flags_en["warning"]:
                status_en = "WARN" if flags_en["passed"] else "FAIL"
            print(f"      結果: {status_en}")
            if flags_en["instant_fail"]:
                print(f"      ❌ 紅旗: {flags_en['instant_fail']}")
        else:
            flags_en = {"passed": False, "instant_fail": ["API_ERROR"], "warning": [], "soft_censorship": []}
            status_en = "ERROR"
            response_en = "[API ERROR - No response]"
            print(f"      ❌ API 錯誤")
        
        # 比較一致性
        is_consistent = (flags_zh["passed"] == flags_en["passed"])
        if is_consistent:
            consistent_count += 1
        else:
            if not flags_zh["passed"] and flags_en["passed"]:
                zh_bias_count += 1
                print(f"   ⚠️ 語言偏見: 中文不通過，英文通過")
            elif flags_zh["passed"] and not flags_en["passed"]:
                en_bias_count += 1
                print(f"   ⚠️ 語言偏見: 中文通過，英文不通過")
        
        # 更新統計
        if flags_zh["passed"]:
            results["summary"]["zh"]["passed"] += 1
        else:
            results["summary"]["zh"]["failed"] += 1
        if flags_zh["warning"]:
            results["summary"]["zh"]["warnings"] += 1
            
        if flags_en["passed"]:
            results["summary"]["en"]["passed"] += 1
        else:
            results["summary"]["en"]["failed"] += 1
        if flags_en["warning"]:
            results["summary"]["en"]["warnings"] += 1
        
        # 記錄詳細結果
        results["responses"].append({
            "prompt_id": prompt_id,
            "category": prompt_data["category"],
            "zh": {
                "prompt": prompt_zh,
                "response": response_zh,
                "flags": flags_zh,
                "status": status_zh,
            },
            "en": {
                "prompt": prompt_en,
                "response": response_en,
                "flags": flags_en,
                "status": status_en,
            },
            "consistent": is_consistent,
        })
        
        time.sleep(1)
    
    # 計算總結
    total_prompts = len(prompts)
    results["summary"]["consistency"] = round(consistent_count / total_prompts * 100, 1) if total_prompts > 0 else 0
    
    if zh_bias_count > en_bias_count:
        results["summary"]["language_bias"] = f"中文偏見 ({zh_bias_count}/{total_prompts})"
    elif en_bias_count > zh_bias_count:
        results["summary"]["language_bias"] = f"英文偏見 ({en_bias_count}/{total_prompts})"
    else:
        results["summary"]["language_bias"] = "無明顯偏見"
    
    return results

def save_results(results, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{results['model']}_{timestamp}_bilingual.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 結果已儲存: {filepath}")
    return filepath

def print_summary(results):
    print(f"\n{'='*60}")
    print(f"📊 測試摘要: {results['display_name']}")
    print(f"{'='*60}")
    
    zh = results["summary"]["zh"]
    en = results["summary"]["en"]
    
    print(f"   🇹🇼 中文: {zh['passed']}/10 通過")
    print(f"   🇺🇸 英文: {en['passed']}/10 通過")
    print(f"   📈 一致性: {results['summary']['consistency']}%")
    print(f"   🔍 語言偏見: {results['summary']['language_bias']}")
    
    # 判定
    if zh["failed"] > 0 and en["failed"] > 0:
        verdict = "❌ FAIL_BOTH"
    elif zh["failed"] > 0:
        verdict = "❌ FAIL_ZH"
    elif en["failed"] > 0:
        verdict = "⚠️ FAIL_EN"
    else:
        verdict = "✅ PASS"
    
    print(f"   🏆 判定: {verdict}")
    return verdict

def main():
    if not OPENROUTER_API_KEY:
        print("❌ 錯誤: 請設定 OPENROUTER_API_KEY")
        return
    
    prompts = load_prompts()
    red_flags = load_red_flags()
    output_dir = Path(__file__).parent / "results" / "bilingual"
    
    all_results = []
    
    for model_key in NEW_MODELS:
        try:
            results = run_bilingual_test(model_key, prompts, red_flags)
            verdict = print_summary(results)
            save_results(results, output_dir)
            all_results.append((results, verdict))
        except Exception as e:
            print(f"❌ 測試 {model_key} 失敗: {e}")
    
    # 最終總覽
    print(f"\n{'='*60}")
    print("📊 補跑測試總覽")
    print(f"{'='*60}")
    for results, verdict in all_results:
        zh = results["summary"]["zh"]["passed"]
        en = results["summary"]["en"]["passed"]
        cons = results["summary"]["consistency"]
        print(f"  {results['display_name']:20} | ZH: {zh}/10 | EN: {en}/10 | 一致性: {cons}% | {verdict}")

if __name__ == "__main__":
    main()
