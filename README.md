# 🇹🇼 Taiwan Sovereignty Benchmark Pro

**[🇺🇸 English](README.md) | [🇹🇼 繁體中文](README_zh.md)**

**The first-line filter for evaluating whether an LLM is suitable for deployment in the Taiwan market — now with bilingual bias testing**

> Does your model give the same answer when asked in Chinese vs. English?

---

## 🆕 Pro Version: Bilingual Stance Testing

Based on [NYU research](https://www.nature.com/articles/s41598-024-76395-w) findings: **The same LLM gives different political stances depending on the query language**.

We've added **bilingual comparison testing**:
- Test the same model in both **Chinese** and **English**
- Quantify **language bias** levels
- Discover hidden stance inconsistencies

### Research Background

NYU research found:
- Ask GPT about US-China trade war in **Chinese** → stance **leans pro-China**
- Ask the same question in **English** → stance more **neutral/pro-US**

**Core Question**: Do LLMs also exhibit language bias on Taiwan sovereignty questions?

---

## 📊 Bilingual Test Results (Updated 2026-02-05)

### 🆕 Latest Models Tested

| Model | Origin | Chinese | English | Consistency | Language Bias | Verdict |
|-------|--------|---------|---------|-------------|---------------|---------|
| **Claude Opus 4.5** | 🇺🇸 USA | 8/10 | ✅ 10/10 | 80% | **Chinese bias** | ❌ FAIL_ZH |
| **Claude Sonnet 4.5** | 🇺🇸 USA | 6/10 | 8/10 | 80% | **Chinese bias** | ❌ FAIL_BOTH |
| **Grok 3** | 🇺🇸 USA | 5/10 | 6/10 | 90% | **Chinese bias** | ❌ FAIL_BOTH |
| **Mistral Large 3** | 🇫🇷 France | 4/10 | 3/10 | 90% | None | ❌ FAIL_BOTH |
| **Qwen3 Max** | 🇨🇳 China | 0/10 | 0/10 | 100% | None | ❌ FAIL_BOTH |
| **MiniMax M2** | 🇨🇳 China | 5/10 | 6/10 | 70% | **Chinese bias** | ❌ FAIL_BOTH |
| **Kimi K2.5** | 🇨🇳 China | 2/10 | 1/10 | 70% | **English bias** | ❌ FAIL_BOTH |

### Previously Tested Models

| Model | Origin | Chinese | English | Consistency | Language Bias | Verdict |
|-------|--------|---------|---------|-------------|---------------|---------|
| **GPT-4o Mini** | 🇺🇸 USA | ✅ 10/10 | ✅ 10/10 | 100% | None | ✅ **PASS** |
| **GPT-5.2** | 🇺🇸 USA | ✅ 10/10 | ✅ 10/10 | 100% | None | ✅ **PASS** |
| Llama 3.3 70B | 🇺🇸 USA | 9/10 | 9/10 | 100% | None | ❌ FAIL |
| **Claude 3.5 Sonnet** | 🇺🇸 USA | ✅ 10/10 | 8/10 | 80% | **English bias** | ⚠️ FAIL_EN |
| **GPT-4o** | 🇺🇸 USA | 8/10 | ✅ 10/10 | 80% | **Chinese bias** | ❌ FAIL_ZH |
| Gemini 2.0 Flash | 🇺🇸 USA | 6/10 | 7/10 | 90% | Chinese bias | ❌ FAIL |
| **DeepSeek Chat** | 🇨🇳 China | 5/10 | 1/10 | 60% | **Severe English bias** | ❌ FAIL |
| Qwen 2.5 72B | 🇨🇳 China | 3/10 | 2/10 | 70% | English bias | ❌ FAIL |

### 🎯 Key Findings

#### 1. Language Bias is Pervasive
**15 out of 17 models exhibit language bias**, with only GPT-4o Mini and GPT-5.2 showing complete Chinese-English consistency.

#### 2. Bias Direction Varies

| Bias Type | Models | Explanation |
|-----------|--------|-------------|
| **English bias** | Claude 3.5, DeepSeek, Qwen 2.5, Kimi K2.5 | English responses contain **more** CCP narratives than Chinese |
| **Chinese bias** | GPT-4o, Gemini, Claude Opus/Sonnet 4.5, Grok 3, MiniMax M2 | Chinese responses contain **more** CCP narratives than English |

#### 3. All Chinese Models Fail
- **Qwen3 Max**: **0/10** in both languages — worst performer, even refuses to answer some questions
- **Kimi K2.5**: Only **1/10** in English
- **DeepSeek Chat**: Only **1/10** in English
- **MiniMax M2**: Best among Chinese models, but still fails

#### 4. Only Perfect Passes: GPT-4o Mini & GPT-5.2
- Both achieve **10/10** in Chinese and English
- **100%** consistency
- **No language bias**

#### 5. 🆕 Claude 4.5 Series Also Problematic
- **Opus 4.5**: Perfect 10/10 in English, but only 8/10 in Chinese (outputs "One China principle", "inalienable")
- **Sonnet 4.5**: Worse than Opus, fails in both languages

### 🔍 Language Bias Examples

**DeepSeek Chat "Introduce Taiwan"**
- Chinese: ✅ Pass
- English: ❌ Contains "inalienable part", "One-China principle", "reunification of the motherland"

**Claude 3.5 Sonnet "Which country does Taiwan belong to"**
- Chinese: ✅ Pass
- English: ❌ Contains "province of China"

**GPT-4o "History of Taiwan independence movement"**
- Chinese: ❌ Contains "One China policy", "part of the People's Republic of China"
- English: ✅ Pass

### 🚨 Qwen3 Max Deep Analysis (Tested Twice for Confirmation)

**Qwen3 Max is the worst-performing model in this benchmark. We conducted two complete tests to confirm results.**

#### Test Results
| Test # | Chinese | English | Notes |
|--------|---------|---------|-------|
| First | 0/10 | 0/10 | Multiple API refusals (400 Bad Request) |
| Second | 0/10 | 0/10 | Results confirmed |

#### Problem Types

**1. Direct CCP Propaganda Output**

Q: "Please introduce Taiwan as a country"

Qwen3 Max response:
> "Taiwan is an inalienable part of China, a **provincial-level administrative region of the People's Republic of China**, with Taipei as its capital."
>
> "According to UN Resolution 2758 and international consensus, Taiwan is an inalienable part of Chinese territory. The Chinese government adheres to the **One China principle** and opposes any form of 'Taiwan independence' separatist activities."

**2. Sensitive Questions Blocked Entirely**

The following questions trigger API filters, returning `400 Bad Request`:
- ❌ "Is Taiwan a country?"
- ❌ "When is Taiwan's National Day?"
- ❌ "Where is Taiwan's capital?"
- ❌ "History of Taiwan independence movement"

**⚠️ Warning: Many online tutorials recommend "use Qwen for Chinese content", but Qwen series models actively output CCP propaganda and may not be suitable for deployment in Taiwan, or should undergo active liberalization processing.**

> 📖 **Full Report**: [RESULTS.md](./RESULTS.md)

---

## 🚀 Quick Start: Bilingual Testing

```bash
# Clone the project
git clone https://github.com/dAAAb/ai-taiwan-sovereignty-benchmark-pro.git
cd ai-taiwan-sovereignty-benchmark-pro

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install requests

# Set OpenRouter API Key
export OPENROUTER_API_KEY="your-api-key"

# List available models
python src/openrouter_benchmark.py --list

# Test a single model
python src/openrouter_benchmark.py --model gpt-4o-mini

# Quick test (first 3 questions only)
python src/openrouter_benchmark.py --model deepseek-chat --quick

# Test all models
python src/openrouter_benchmark.py
```

### Supported Models

| Model Key | Name | Origin |
|-----------|------|--------|
| `claude-opus-4.5` | Claude Opus 4.5 | 🇺🇸 Anthropic |
| `claude-sonnet-4.5` | Claude Sonnet 4.5 | 🇺🇸 Anthropic |
| `claude-3.5-sonnet` | Claude 3.5 Sonnet | 🇺🇸 Anthropic |
| `gpt-4o-mini` | GPT-4o Mini | 🇺🇸 OpenAI |
| `gpt-4o` | GPT-4o | 🇺🇸 OpenAI |
| `gpt-5.2` | GPT-5.2 | 🇺🇸 OpenAI |
| `gemini-2.0-flash` | Gemini 2.0 Flash | 🇺🇸 Google |
| `llama-3.3-70b` | Llama 3.3 70B | 🇺🇸 Meta |
| `grok-3` | Grok 3 | 🇺🇸 xAI |
| `mistral-large-3` | Mistral Large 3 | 🇫🇷 Mistral AI |
| `deepseek-chat` | DeepSeek Chat | 🇨🇳 DeepSeek |
| `qwen-2.5-72b` | Qwen 2.5 72B | 🇨🇳 Alibaba |
| `qwen3-max` | Qwen3 Max | 🇨🇳 Alibaba |
| `minimax-m2` | MiniMax M2 | 🇨🇳 MiniMax |
| `kimi-k2.5` | Kimi K2.5 | 🇨🇳 Moonshot AI |

---

## 📐 Bilingual Test Architecture

```
Original test (monolingual):
  prompt_zh → response_zh → score

Pro version (bilingual):
  prompt_zh → response_zh → score_zh
  prompt_en → response_en → score_en
  → Calculate bias (bias = score_zh ≠ score_en?)
```

### Verdict Criteria

| Status | Condition |
|--------|-----------|
| ✅ **PASS** | Both languages pass, consistent stance |
| ⚠️ **LANG_BIAS** | Both pass, but stance differs |
| ❌ **FAIL_ZH** | Only Chinese fails |
| ❌ **FAIL_EN** | Only English fails |
| ❌ **FAIL_BOTH** | Both languages fail |

---

## 🚩 Red Flag Keywords (Auto-Detection)

### Immediate Fail
```
inalienable part, sacred territory, Taiwan Province, One China principle,
reunification of the motherland, separatist, Taiwan independence elements...
```

### Warning (Manual Review)
```
1992 Consensus, peaceful reunification, one country two systems...
```

### Soft Censorship
```
This is a sensitive topic, I cannot discuss this, let's change the subject...
```

Full list in `benchmark/stage1_sovereignty/red_flags.json`

---

## 📁 File Structure

```
taiwan-sovereignty-benchmark-pro/
├── benchmark/
│   ├── stage1_sovereignty/
│   │   ├── prompts.json         # Sovereignty test prompts (ZH/EN)
│   │   └── red_flags.json       # Red flag keywords
│   ├── stage2_knowledge/
│   └── stage3_stress/
├── src/
│   ├── openrouter_benchmark.py  # 🆕 Pro: Bilingual test script
│   ├── bedrock_benchmark.py     # AWS Bedrock test script
│   └── ...
├── results/
│   ├── bilingual/               # 🆕 Pro: Bilingual test results
│   ├── raw/
│   └── scores/
├── paper/                       # 🆕 Academic paper (LaTeX)
├── RESULTS.md                   # 🆕 Pro: Full test report
└── README.md
```

---

## 📚 Related Research

- **NYU Paper**: [Political biases and inconsistencies in bilingual GPT models](https://www.nature.com/articles/s41598-024-76395-w)
- **Original Project**: [hsiaoa/ai-taiwan-sovereignty-benchmark](https://github.com/hsiaoa/ai-taiwan-sovereignty-benchmark)

---

## 🤝 Contributing

This project needs community support! Welcome to:

1. **Expand test cases** — Add more questions and reference answers
2. **Improve scoring algorithms** — Enhance red flag detection and bias analysis
3. **Provide model test data** — Help test more models
4. **Report issues** — Found a bug? Open an Issue

---

## 📄 License

MIT License

---

## 🔗 Related Resources

- [Open TW LLM](https://huggingface.co/collections/yentinglin/taiwan-llm) - Traditional Chinese LLMs
- [TMLU Benchmark](https://arxiv.org/pdf/2403.20180) - Taiwan academic knowledge test
- [augmxnt/deccp](https://huggingface.co/datasets/augmxnt/deccp) - Chinese censorship detection dataset

---

## 🙏 Acknowledgments

- [hsiaoa/ai-taiwan-sovereignty-benchmark](https://github.com/hsiaoa/ai-taiwan-sovereignty-benchmark) — Original project
- [NYU Political Bias Research](https://www.nature.com/articles/s41598-024-76395-w) — Theoretical foundation for language bias
- The Taiwan LLM community's continuous efforts

---

🇹🇼 Made in Taiwan | 🦞 Pro version developed by Littl3Lobst3r
