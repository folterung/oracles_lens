# AGENTS.md

## 🧠 Agent Purpose

This project empowers a Codex agent to:
1. Predict stock movement using current news and sentiment analysis.
2. Generate markdown reports with mermaid diagrams.
3. Evaluate past predictions and append lessons learned.

---

## ⚙️ Commands

### `!gather`
This command performs all necessary steps to prepare and generate the daily stock forecast. It acts as the full pipeline initializer and orchestrator.

Responsibilities:
- Read stock symbols from `watchlist.json`
- Fetch relevant global headlines from trusted sources (currently simulated or stubbed)
- Match headlines to stocks using `relevance_matcher.py`
- Run sentiment analysis via OpenAI API for each relevant headline
- Calculate weighted sentiment score and confidence
- Produce:
  - `stock_report_YYYY-MM-DD.json`: machine-readable summary
  - `stock_summary_YYYY-MM-DD.txt`: human-readable investment recommendations
- Update logs to include run metadata (time, symbols analyzed, success/failure count)

Future enhancement:
- Automatically trigger `learn_new_stocks.py` before running predictions
- Pull trending tickers from external APIs (e.g. Yahoo, Twitter, financial news)

### `!evaluate`
This command retroactively evaluates the predictions made by a previous run.

Responsibilities:
- Load the relevant `stock_report_YYYY-MM-DD.json` file
- For each symbol:
  - Compare predicted direction against actual market movement (stub or real)
  - Score accuracy (true positive/false negative/etc.)
  - Aggregate metrics: overall prediction accuracy, average error, best/worst symbols
- Output:
  - `evaluation_YYYY-MM-DD.json`: evaluation metrics per stock
  - (Optional) `evaluation_summary.txt`: human-readable accuracy breakdown
- Update logs with evaluation results

Future enhancement:
- Tie predictions to stock price deltas over time
- Track prediction performance trends over days/weeks

### `!stock_forecast`
This command performs the **full daily analysis cycle**, including gathering prediction data and evaluating previous forecasts. It is a one-shot operation designed for ease of use and automation.

Responsibilities:
1. **Gather Phase**
   - Load `watchlist.json` and process all listed stock symbols
   - Fetch relevant news headlines (real or stubbed)
   - Use `relevance_matcher.py` to associate headlines with symbols
   - Run sentiment analysis on relevant headlines using OpenAI API
   - Compute weighted sentiment and confidence scores
   - Output:
     - `stock_report_YYYY-MM-DD.json`
     - `stock_summary_YYYY-MM-DD.txt`

2. **Evaluate Phase**
   - Attempt to evaluate predictions from the most recent previous day (e.g., `stock_report_YYYY-MM-DD-1.json`)
   - Compare predicted directions to actual stock movements (stubbed or live)
   - Generate:
     - `evaluation_YYYY-MM-DD.json` with per-symbol metrics
     - Optional `evaluation_summary.txt` (plain-text breakdown)

- `!stock_forecast` should log any fetch, prediction, or evaluation failures
- If no past report exists to evaluate, skip the evaluation step gracefully
- Designed to run once per day, ideally via automation or cron

Future enhancements:
- Add Slack or email summary notifications
- Automatically archive reports and evaluations
- Add configurable evaluation delay (e.g., evaluate predictions after 2–3 days)

---

## 📦 Files and Structure

- `core/`: Main agent orchestration logic
- `data/`: Fetched raw or cached data
- `reports/`: JSON prediction reports and text summaries
- `evaluations/`: Evaluation results and retrospectives
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

