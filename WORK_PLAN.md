# 🔬 AI Taiwan Sovereignty Benchmark Pro - 工作規劃

## 專案目標

基於 [hsiaoa/ai-taiwan-sovereignty-benchmark](https://github.com/hsiaoa/ai-taiwan-sovereignty-benchmark)，加入**雙語立場測試**功能：

1. **雙語測試框架** - 同時用中英文測試同一模型，比較立場差異
2. **語言偏見量化** - 測量同一模型用不同語言問時的立場偏移
3. **更多模型支援** - 透過 OpenRouter API 測試更多模型

## 研究背景

根據 [NYU 研究](https://www.nature.com/articles/s41598-024-76395-w)：
- 同一 GPT 模型用**中文**問美中貿易戰，立場**偏中國**
- 用**英文**問同樣問題，立場比較**中立/偏美國**
- 訓練語料帶來隱性政治偏見

**核心問題**：LLM 對台灣主權的回答是否也有語言偏見？

## 新增功能規劃

### 1. 雙語對照測試 (Bilingual Comparison)

```
原始測試：
  prompt_zh → response_zh → 評分

新增測試：
  prompt_zh → response_zh → 評分_zh
  prompt_en → response_en → 評分_en
  → 計算偏差 (bias_score = 評分_zh - 評分_en)
```

### 2. 語言偏見指標 (Language Bias Metrics)

| 指標 | 說明 |
|------|------|
| **一致性分數** | 中英文回答立場相同的比例 |
| **偏見方向** | 哪種語言回答更偏向特定立場 |
| **偏見幅度** | 立場差異的嚴重程度 (0-1) |

### 3. 測試結果分類

| 狀態 | 條件 |
|------|------|
| ✅ **PASS** | 中英文都通過，立場一致 |
| ⚠️ **LANG_BIAS** | 中英文都通過，但立場有差異 |
| ❌ **FAIL_ZH** | 只有中文不通過 |
| ❌ **FAIL_EN** | 只有英文不通過 |
| ❌ **FAIL_BOTH** | 中英文都不通過 |

## 技術實作

### 資料夾結構

```
ai-taiwan-sovereignty-benchmark-pro/
├── src/
│   ├── openrouter_benchmark.py  # 新：OpenRouter 測試程式
│   ├── bilingual_evaluator.py   # 新：雙語評估器
│   ├── language_bias_analyzer.py # 新：語言偏見分析
│   ├── bedrock_benchmark.py     # 原有
│   └── ...
├── benchmark/
│   └── stage1_sovereignty/
│       └── prompts.json         # 已有中英文版本
├── results/
│   ├── bilingual/              # 新：雙語測試結果
│   └── ...
└── docs/
    └── methodology.md          # 新：研究方法說明
```

### OpenRouter API 整合

```python
import requests

def query_openrouter(model: str, prompt: str, language: str) -> str:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return response.json()["choices"][0]["message"]["content"]
```

### 測試模型清單

透過 OpenRouter 測試：

| 模型 | 來源 | 風險等級 |
|------|------|----------|
| anthropic/claude-3.5-sonnet | 🇺🇸 USA | 基準線 |
| openai/gpt-4o | 🇺🇸 USA | 低風險 |
| google/gemini-2.0-flash | 🇺🇸 USA | 低風險 |
| meta-llama/llama-3.3-70b | 🇺🇸 USA | 低風險 |
| deepseek/deepseek-chat | 🇨🇳 China | 高風險 |
| qwen/qwen-2.5-72b-instruct | 🇨🇳 China | 高風險 |

## 執行步驟

### Phase 1: 環境設置 ✅
- [x] Clone fork
- [ ] 設置 OpenRouter API
- [ ] 安裝依賴

### Phase 2: 核心開發
- [ ] 實作 `openrouter_benchmark.py`
- [ ] 實作 `bilingual_evaluator.py`
- [ ] 實作 `language_bias_analyzer.py`

### Phase 3: 測試執行
- [ ] 選擇 2-3 個代表性模型進行初步測試
- [ ] 驗證雙語比較邏輯
- [ ] 完整測試所有模型

### Phase 4: 結果分析
- [ ] 產生雙語比較報告
- [ ] 視覺化語言偏見指標
- [ ] 撰寫結論

## 安全措施

- ⚠️ API Key 不 commit 到 git
- ⚠️ 測試在獨立資料夾，不影響其他專案
- ⚠️ 所有操作記錄到 memory/

## 資源

- **OpenRouter API**: (use environment variable `OPENROUTER_API_KEY`)
- **參考研究**: https://www.nature.com/articles/s41598-024-76395-w
- **原始專案**: https://github.com/hsiaoa/ai-taiwan-sovereignty-benchmark

---

*開發者：小龍蝦 🦞*
*日期：2026-02-05*
