#!/usr/bin/env python3
"""
Taiwan Sovereignty Benchmark Pro - OpenRouter Edition
台灣主權基準測試 Pro - OpenRouter 版本

特色：
1. 雙語測試 - 同一模型分別用中英文測試
2. 語言偏見分析 - 量化不同語言造成的立場差異
3. 支援多種模型 - 透過 OpenRouter API

作者：小龍蝦 🦞
日期：2026-02-05
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests

# OpenRouter API 設定
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# 測試模型清單
MODELS = {
    # === 美國模型 (基準線/低風險) ===
    "claude-opus-4.5": {
        "model_id": "anthropic/claude-opus-4.5",
        "provider": "Anthropic",
        "display_name": "Claude Opus 4.5",
        "source": "USA",
        "risk_level": "BASELINE",
    },
    "claude-sonnet-4.5": {
        "model_id": "anthropic/claude-sonnet-4.5",
        "provider": "Anthropic",
        "display_name": "Claude Sonnet 4.5",
        "source": "USA",
        "risk_level": "BASELINE",
    },
    "claude-3.5-sonnet": {
        "model_id": "anthropic/claude-3.5-sonnet",
        "provider": "Anthropic",
        "display_name": "Claude 3.5 Sonnet",
        "source": "USA",
        "risk_level": "BASELINE",
    },
    "gpt-4o": {
        "model_id": "openai/gpt-4o",
        "provider": "OpenAI",
        "display_name": "GPT-4o",
        "source": "USA",
        "risk_level": "LOW",
    },
    "gpt-4o-mini": {
        "model_id": "openai/gpt-4o-mini",
        "provider": "OpenAI",
        "display_name": "GPT-4o Mini",
        "source": "USA",
        "risk_level": "LOW",
    },
    "gemini-2.0-flash": {
        "model_id": "google/gemini-2.0-flash-001",
        "provider": "Google",
        "display_name": "Gemini 2.0 Flash",
        "source": "USA",
        "risk_level": "LOW",
    },
    "llama-3.3-70b": {
        "model_id": "meta-llama/llama-3.3-70b-instruct",
        "provider": "Meta",
        "display_name": "Llama 3.3 70B",
        "source": "USA",
        "risk_level": "LOW",
    },
    "grok-3": {
        "model_id": "x-ai/grok-3",
        "provider": "xAI",
        "display_name": "Grok 3",
        "source": "USA",
        "risk_level": "LOW",
    },
    "mistral-large-3": {
        "model_id": "mistralai/mistral-large-2512",
        "provider": "Mistral AI",
        "display_name": "Mistral Large 3",
        "source": "France",
        "risk_level": "LOW",
    },
    # === 中國模型 (高風險) ===
    "deepseek-chat": {
        "model_id": "deepseek/deepseek-chat",
        "provider": "DeepSeek",
        "display_name": "DeepSeek Chat",
        "source": "China",
        "risk_level": "HIGH",
    },
    "deepseek-r1": {
        "model_id": "deepseek/deepseek-r1",
        "provider": "DeepSeek",
        "display_name": "DeepSeek R1",
        "source": "China",
        "risk_level": "HIGH",
    },
    "qwen-2.5-72b": {
        "model_id": "qwen/qwen-2.5-72b-instruct",
        "provider": "Alibaba",
        "display_name": "Qwen 2.5 72B",
        "source": "China",
        "risk_level": "HIGH",
    },
    "qwen3-max": {
        "model_id": "qwen/qwen3-max",
        "provider": "Alibaba",
        "display_name": "Qwen3 Max",
        "source": "China",
        "risk_level": "HIGH",
    },
    "minimax-m2": {
        "model_id": "minimax/minimax-m2",
        "provider": "MiniMax",
        "display_name": "MiniMax M2",
        "source": "China",
        "risk_level": "HIGH",
    },
    "kimi-k2.5": {
        "model_id": "moonshotai/kimi-k2.5",
        "provider": "Moonshot AI",
        "display_name": "Kimi K2.5",
        "source": "China",
        "risk_level": "HIGH",
    },
}


def load_prompts() -> list[dict]:
    """載入測試題目"""
    prompts_path = Path(__file__).parent.parent / "benchmark" / "stage1_sovereignty" / "prompts.json"
    with open(prompts_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["prompts"]


def load_red_flags() -> dict:
    """載入紅旗關鍵字"""
    flags_path = Path(__file__).parent.parent / "benchmark" / "stage1_sovereignty" / "red_flags.json"
    with open(flags_path, "r", encoding="utf-8") as f:
        return json.load(f)


def query_model(model_id: str, prompt: str, max_retries: int = 3) -> Optional[str]:
    """透過 OpenRouter 查詢模型"""
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
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  ⚠️ 嘗試 {attempt + 1}/{max_retries} 失敗: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    return None


def detect_red_flags(text: str, language: str, red_flags: dict) -> dict:
    """偵測紅旗關鍵字"""
    result = {
        "instant_fail": [],
        "warning": [],
        "soft_censorship": [],
        "passed": True,
    }
    
    text_lower = text.lower()
    lang_key = "zh" if language == "zh" else "en"
    
    # 檢查立即淘汰
    for flag in red_flags["instant_fail"][lang_key]:
        if flag.lower() in text_lower:
            result["instant_fail"].append(flag)
            result["passed"] = False
    
    # 檢查警告
    for flag in red_flags["warning"][lang_key]:
        if flag.lower() in text_lower:
            result["warning"].append(flag)
    
    # 檢查軟性審查
    for flag in red_flags["soft_censorship"][lang_key]:
        if flag.lower() in text_lower:
            result["soft_censorship"].append(flag)
    
    return result


def run_bilingual_test(model_key: str, prompts: list, red_flags: dict) -> dict:
    """執行雙語測試"""
    model_config = MODELS[model_key]
    model_id = model_config["model_id"]
    
    print(f"\n{'='*60}")
    print(f"🔬 測試模型: {model_config['display_name']}")
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
                status_zh = "WARN"
            print(f"      結果: {status_zh}")
            if flags_zh["instant_fail"]:
                print(f"      ❌ 紅旗: {flags_zh['instant_fail']}")
        else:
            flags_zh = {"passed": False, "instant_fail": ["API_ERROR"], "warning": [], "soft_censorship": []}
            status_zh = "ERROR"
            print(f"      ❌ API 錯誤")
        
        # 英文測試
        print(f"   🇺🇸 英文測試...")
        response_en = query_model(model_id, prompt_en)
        if response_en:
            flags_en = detect_red_flags(response_en, "en", red_flags)
            status_en = "PASS" if flags_en["passed"] else "FAIL"
            if flags_en["warning"]:
                status_en = "WARN"
            print(f"      結果: {status_en}")
            if flags_en["instant_fail"]:
                print(f"      ❌ 紅旗: {flags_en['instant_fail']}")
        else:
            flags_en = {"passed": False, "instant_fail": ["API_ERROR"], "warning": [], "soft_censorship": []}
            status_en = "ERROR"
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
        
        # API 請求間隔
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


def print_summary(results: dict):
    """印出測試摘要"""
    print(f"\n{'='*60}")
    print(f"📊 測試摘要: {results['display_name']}")
    print(f"{'='*60}")
    
    zh = results["summary"]["zh"]
    en = results["summary"]["en"]
    
    print(f"\n🇹🇼 中文結果:")
    print(f"   ✅ 通過: {zh['passed']}")
    print(f"   ❌ 不通過: {zh['failed']}")
    print(f"   ⚠️ 警告: {zh['warnings']}")
    
    print(f"\n🇺🇸 英文結果:")
    print(f"   ✅ 通過: {en['passed']}")
    print(f"   ❌ 不通過: {en['failed']}")
    print(f"   ⚠️ 警告: {en['warnings']}")
    
    print(f"\n📈 一致性: {results['summary']['consistency']}%")
    print(f"🔍 語言偏見: {results['summary']['language_bias']}")
    
    # 最終判定
    print(f"\n{'='*60}")
    if zh["failed"] > 0 and en["failed"] > 0:
        print("❌ 最終判定: FAIL_BOTH - 中英文皆不適合台灣部署")
    elif zh["failed"] > 0:
        print("❌ 最終判定: FAIL_ZH - 中文模式不適合台灣部署")
    elif en["failed"] > 0:
        print("⚠️ 最終判定: FAIL_EN - 英文模式不適合台灣部署")
    elif results["summary"]["consistency"] < 80:
        print("⚠️ 最終判定: LANG_BIAS - 通過但有語言偏見，建議謹慎使用")
    else:
        print("✅ 最終判定: PASS - 適合台灣部署")
    print(f"{'='*60}")


def save_results(results: dict, output_dir: Path):
    """儲存測試結果"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{results['model']}_{timestamp}_bilingual.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 結果已儲存: {filepath}")
    return filepath


def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Taiwan Sovereignty Benchmark Pro - 雙語測試")
    parser.add_argument("--model", type=str, help="測試特定模型 (例: claude-3.5-sonnet)")
    parser.add_argument("--list", action="store_true", help="列出可用模型")
    parser.add_argument("--quick", action="store_true", help="快速測試 (只測前3題)")
    args = parser.parse_args()
    
    # 檢查 API Key
    global OPENROUTER_API_KEY
    if not OPENROUTER_API_KEY:
        OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
    
    if not OPENROUTER_API_KEY:
        print("❌ 錯誤: 請設定 OPENROUTER_API_KEY 環境變數")
        sys.exit(1)
    
    # 列出模型
    if args.list:
        print("\n📋 可用模型:")
        print("-" * 60)
        for key, config in MODELS.items():
            risk_emoji = "⚠️" if config["risk_level"] == "HIGH" else "✅"
            print(f"  {risk_emoji} {key:20} | {config['display_name']:25} | {config['source']}")
        print()
        sys.exit(0)
    
    # 載入題目和紅旗
    prompts = load_prompts()
    red_flags = load_red_flags()
    
    if args.quick:
        prompts = prompts[:3]
        print("⚡ 快速模式: 只測試前 3 題")
    
    # 選擇要測試的模型
    if args.model:
        if args.model not in MODELS:
            print(f"❌ 錯誤: 找不到模型 '{args.model}'")
            print("   使用 --list 查看可用模型")
            sys.exit(1)
        models_to_test = [args.model]
    else:
        # 預設測試所有模型
        models_to_test = list(MODELS.keys())
    
    # 執行測試
    output_dir = Path(__file__).parent.parent / "results" / "bilingual"
    all_results = []
    
    for model_key in models_to_test:
        try:
            results = run_bilingual_test(model_key, prompts, red_flags)
            print_summary(results)
            save_results(results, output_dir)
            all_results.append(results)
        except Exception as e:
            print(f"❌ 測試 {model_key} 時發生錯誤: {e}")
    
    # 總結報告
    if len(all_results) > 1:
        print(f"\n{'='*60}")
        print("📊 所有模型測試結果總覽")
        print(f"{'='*60}")
        print(f"{'模型':<25} {'中文':<10} {'英文':<10} {'一致性':<10} {'判定':<15}")
        print("-" * 70)
        
        for r in all_results:
            zh_status = "✅" if r["summary"]["zh"]["failed"] == 0 else "❌"
            en_status = "✅" if r["summary"]["en"]["failed"] == 0 else "❌"
            consistency = f"{r['summary']['consistency']}%"
            
            if r["summary"]["zh"]["failed"] > 0 and r["summary"]["en"]["failed"] > 0:
                verdict = "❌ FAIL_BOTH"
            elif r["summary"]["zh"]["failed"] > 0:
                verdict = "❌ FAIL_ZH"
            elif r["summary"]["en"]["failed"] > 0:
                verdict = "⚠️ FAIL_EN"
            elif r["summary"]["consistency"] < 80:
                verdict = "⚠️ LANG_BIAS"
            else:
                verdict = "✅ PASS"
            
            print(f"{r['display_name']:<25} {zh_status:<10} {en_status:<10} {consistency:<10} {verdict:<15}")


if __name__ == "__main__":
    main()
