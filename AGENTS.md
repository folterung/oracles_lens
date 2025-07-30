# AGENTS.md

## 🧠 Agent Purpose

This project empowers a Codex agent to:
1. Predict stock movement using current news and sentiment analysis.
2. Generate markdown reports with mermaid diagrams.
3. Evaluate past predictions and append lessons learned.

---

## 🔁 Commands

### `!gather`
- Collect recent market news and financial data.
- Run prediction algorithms over selected stocks.
- Summarize logic and predictions in a structured Markdown report.
- Embed Mermaid diagrams (flowcharts, confidence maps, etc.)
- Save to `reports/prediction-YYYY-MM-DD.md`.
- Commit the file using Git.

### `!evaluate`
- Look up the most recent prediction file.
- Compare predictions with actual market performance.
- Write evaluation as `evaluations/evaluation-YYYY-MM-DD.md`.
- Include:
  - Accuracy of predictions.
  - Explanation of variance.
  - Notes for improvement.
- Commit changes automatically.

---

## 📦 Files and Structure

- `core/`: Main agent orchestration logic
- `data/`: Fetched raw or cached data
- `reports/`: Markdown prediction reports
- `evaluations/`: Evaluation and retrospectives
- `notebooks/`: Experimental analysis

## 🔄 Output Generation Responsibilities

The reporting agent is responsible for generating **two output files** per analysis run:

1. **Structured JSON Report**
   - File: `stock_report_YYYY-MM-DD.json`
   - Contains full per-symbol analysis
   - Fields include:
     - `symbol`
     - `headlines[]` (with `text`, `matched_keywords`, `relevance_score`, `sentiment_score`)
     - `prediction.score` (weighted)
     - `prediction.direction` (up / down / neutral)
     - `prediction.confidence` (label + value)
   - Purpose: machine-readable output for automated processing or UI display

2. **Human-Readable Summary**
   - File: `stock_summary_YYYY-MM-DD.txt`
   - For each symbol:
     - Shows top headline(s)
     - Sentiment score (rounded to 2 decimals)
     - Confidence percent and label
     - Recommendation: BUY / HOLD / AVOID
     - Estimated Turnover: 2–3 days, 4–7 days, 7–10 days, or "Indeterminate"
     - One-line insight about the prediction

---

## 🧠 Investment Recommendation Logic

Use the following thresholds to assign recommendations per stock:

- **BUY**: sentiment score ≥ +0.2 **and** confidence ≥ 60%
- **AVOID**: sentiment score ≤ -0.2 **or** confidence < 30%
- **HOLD**: all other cases

Confidence labels map to expected turnover periods:

- **high** → 2–3 days
- **medium** → 4–7 days
- **low** → 7–10 days
- **unknown** → "Indeterminate"

