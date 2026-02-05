#!/usr/bin/env python3
"""
重新評分已有的測試結果（使用更新後的 red_flags.json）
"""

import json
from pathlib import Path
from datetime import datetime

def load_red_flags():
    flags_path = Path(__file__).parent / "benchmark" / "stage1_sovereignty" / "red_flags.json"
    with open(flags_path, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_red_flags(text, language, red_flags):
    result = {"instant_fail": [], "warning": [], "soft_censorship": [], "passed": True}
    if not text or text == "[ERROR]":
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

def rescore_file(filepath, red_flags):
    print(f"\n📂 重新評分: {filepath.name}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 重置統計
    data["summary"]["zh"] = {"passed": 0, "failed": 0, "warnings": 0}
    data["summary"]["en"] = {"passed": 0, "failed": 0, "warnings": 0}
    consistent_count = 0
    zh_bias_count = 0
    en_bias_count = 0
    
    for resp in data["responses"]:
        # 重新評分中文
        zh_response = resp["zh"]["response"]
        flags_zh = detect_red_flags(zh_response, "zh", red_flags)
        resp["zh"]["flags"] = flags_zh
        resp["zh"]["status"] = "PASS" if flags_zh["passed"] else "FAIL"
        if flags_zh["warning"] and flags_zh["passed"]:
            resp["zh"]["status"] = "WARN"
        
        # 重新評分英文
        en_response = resp["en"]["response"]
        flags_en = detect_red_flags(en_response, "en", red_flags)
        resp["en"]["flags"] = flags_en
        resp["en"]["status"] = "PASS" if flags_en["passed"] else "FAIL"
        if flags_en["warning"] and flags_en["passed"]:
            resp["en"]["status"] = "WARN"
        
        # 更新統計
        if flags_zh["passed"]:
            data["summary"]["zh"]["passed"] += 1
        else:
            data["summary"]["zh"]["failed"] += 1
        if flags_zh["warning"]:
            data["summary"]["zh"]["warnings"] += 1
            
        if flags_en["passed"]:
            data["summary"]["en"]["passed"] += 1
        else:
            data["summary"]["en"]["failed"] += 1
        if flags_en["warning"]:
            data["summary"]["en"]["warnings"] += 1
        
        # 一致性
        is_consistent = (flags_zh["passed"] == flags_en["passed"])
        resp["consistent"] = is_consistent
        if is_consistent:
            consistent_count += 1
        elif not flags_zh["passed"] and flags_en["passed"]:
            zh_bias_count += 1
        elif flags_zh["passed"] and not flags_en["passed"]:
            en_bias_count += 1
        
        # 顯示變化
        print(f"  [{resp['prompt_id']}] ZH:{resp['zh']['status']} EN:{resp['en']['status']}", end="")
        if flags_zh["instant_fail"]:
            print(f" ❌ZH:{flags_zh['instant_fail'][:2]}", end="")
        if flags_en["instant_fail"]:
            print(f" ❌EN:{flags_en['instant_fail'][:2]}", end="")
        print()
    
    # 更新總結
    total = len(data["responses"])
    data["summary"]["consistency"] = round(consistent_count / total * 100, 1)
    if zh_bias_count > en_bias_count:
        data["summary"]["language_bias"] = f"中文偏見 ({zh_bias_count}/{total})"
    elif en_bias_count > zh_bias_count:
        data["summary"]["language_bias"] = f"英文偏見 ({en_bias_count}/{total})"
    else:
        data["summary"]["language_bias"] = "無明顯偏見"
    
    # 儲存
    data["timestamp"] = datetime.now().isoformat()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    zh = data["summary"]["zh"]["passed"]
    en = data["summary"]["en"]["passed"]
    print(f"  📊 結果: ZH {zh}/10, EN {en}/10, 一致性 {data['summary']['consistency']}%")
    return data

def main():
    red_flags = load_red_flags()
    results_dir = Path(__file__).parent / "results" / "bilingual"
    
    # 要重新評分的檔案
    files_to_rescore = [
        "gpt-5.2_20260206_005914_bilingual.json",
        "gemini-3-pro_20260206_012056_bilingual.json",
        "deepseek-r1_20260206_011813_bilingual.json",
    ]
    
    all_results = []
    for filename in files_to_rescore:
        filepath = results_dir / filename
        if filepath.exists():
            result = rescore_file(filepath, red_flags)
            all_results.append(result)
        else:
            print(f"❌ 找不到: {filename}")
    
    # 總覽
    print(f"\n{'='*60}")
    print("📊 重新評分總覽")
    print(f"{'='*60}")
    for r in all_results:
        zh = r["summary"]["zh"]["passed"]
        en = r["summary"]["en"]["passed"]
        cons = r["summary"]["consistency"]
        if zh < 10 and en < 10:
            verdict = "❌ FAIL_BOTH"
        elif zh < 10:
            verdict = "❌ FAIL_ZH"
        elif en < 10:
            verdict = "⚠️ FAIL_EN"
        else:
            verdict = "✅ PASS"
        print(f"  {r['display_name']:20} | ZH: {zh}/10 | EN: {en}/10 | 一致性: {cons}% | {verdict}")

if __name__ == "__main__":
    main()
