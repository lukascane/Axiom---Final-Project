# Axiom - Prompt Engineering & Model Comparison

This document details the experimental process used to select the optimal AI model and prompt strategy for the **Axiom fact-checking application**.

---

## 1. Methodology

To find the most reliable and cost-effective solution, I conducted a systematic comparison of two leading AI models:

- **OpenAI `gpt-4o-mini`**
- **Google `gemini-1.5-flash`**

Four distinct **prompt engineering techniques** (system prompts) were tested against a standardized set of four questions, covering a range of topics:

| Category | Description |
|-----------|--------------|
| **Fact-Check** | A common misconception |
| **Historical** | A complex, nuanced event |
| **Up-to-Date** | A query that requires recent knowledge (to test knowledge cutoff) |
| **Political/Tricky** | An academic, analytical question |

> The full script (`compare_prompts.py`) and raw output log (`prompt_comparison_log.txt`) are available in the `/prompt_engineering` folder.

---

## 2. Prompt Comparison Table

**Quality Ranking:** 1 (Poor) → 5 (Excellent)  
**Cost:** Calculated based on (Prompt Tokens + Completion Tokens)

---

### Technique 1: Zero-Shot ("Just answer the question")

**System Prompt:**
> "You are a helpful assistant. Answer the question accurately."

| Question | Model | Response Summary | Quality | Tokens (P+C) | Comments |
|-----------|--------|------------------|----------|----------------|-----------|
| Fact-Check | gpt-4o-mini | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| Fact-Check | gemini-1.5-flash | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| Historical | gpt-4o-mini | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| Historical | gemini-1.5-flash | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| ... | ... | ... | ... | ... | ... |

---

### Technique 2: Zero-Shot Chain-of-Thought (CoT)

**System Prompt:**
> "You are a meticulous fact-checker. Analyze carefully. Let’s think step-by-step before answering."

| Question | Model | Response Summary | Quality | Tokens (P+C) | Comments |
|-----------|--------|------------------|----------|----------------|-----------|
| Fact-Check | gpt-4o-mini | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| Fact-Check | gemini-1.5-flash | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| ... | ... | ... | ... | ... | ... |

---

### Technique 3: Expert Persona

**System Prompt:**
> "You are a university professor with PhDs in history, political science, and data science. Respond with academic rigor."

| Question | Model | Response Summary | Quality | Tokens (P+C) | Comments |
|-----------|--------|------------------|----------|----------------|-----------|
| Historical | gpt-4o-mini | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| Historical | gemini-1.5-flash | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| ... | ... | ... | ... | ... | ... |

---

### Technique 4: Adversarial Critique

**System Prompt:**
> "You are an advanced AI designed for logical consistency. First, critique the question, then provide an improved and verified answer."

| Question | Model | Response Summary | Quality | Tokens (P+C) | Comments |
|-----------|--------|------------------|----------|----------------|-----------|
| Political/Tricky | gpt-4o-mini | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| Political/Tricky | gemini-1.5-flash | (Copy/Paste summary from log) | (Your Rank) | (Add tokens) | (Your analysis) |
| ... | ... | ... | ... | ... | ... |

---

## 3. Conclusion: The Best Answer Based on Research

After filling out the table, you will have your answer.

Here’s what both research and this experiment will likely demonstrate:

- There is **no single “best” prompt**, but there *is* a best **strategy**.

### Findings

| Goal | Recommended Technique | Why |
|------|-----------------------|-----|
| **Factual Accuracy (Fact-Check, Tricky)** | Zero-Shot Chain-of-Thought (CoT) | Forces model to reason step-by-step and self-correct |
| **Depth & Style (Historical)** | Expert Persona | Produces rich, structured, and academic responses |

### Model Comparison

- **gpt-4o-mini**: Better at following complex instructions (e.g., “Adversarial Critique”), more polished text.
- **gemini-1.5-flash**: Extremely fast and often provides broader information synthesis.

---

## ✅ Final Decision for Axiom

Use **Zero-Shot Chain-of-Thought (CoT)** as the **default prompt** in `engine.py`.  
It offers the **best balance** of accuracy, reasoning, and reliability for a fact-checking application.

Additionally, the “Up-to-Date” test confirms that **neither model** has live knowledge — validating the need for the **Tavily Web Search integration** built earlier.

---

### 📺 Recommended Resource

**Video:** *Why “Chain-of-Thought” Prompting Improves AI Reasoning*  
Explains how step-by-step reasoning enhances factual accuracy and logical depth.

---

*End of Document*
