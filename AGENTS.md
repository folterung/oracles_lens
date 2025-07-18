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
