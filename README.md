# Stock Predictor

This project provides commands to gather news, predict stock movements, and evaluate predictions.

## Setup
1. Install dependencies: `pip install -r requirements.txt`.
2. Create a `.env` file with the following keys:
   - `NEWS_API_KEY`
   - `OPENAI_API_KEY`
   - `STOCK_API_KEY`
   - `GIT_USERNAME` *(optional)*
   - `GIT_EMAIL` *(optional)*

## Commands
Run using `python main.py [command]`.

### `gather`
Fetch recent news, analyze sentiment, generate a prediction report and commit it under `reports/`.

### `evaluate`
Find the latest report, fetch real market data, evaluate accuracy, and commit an evaluation file under `evaluations/`.

### `forecast`
Run both the gather and evaluate phases in one shot. This is useful for automation or daily cron jobs.

## Example
```
$ python main.py gather
Report generated at reports/prediction-2023-08-01.md
```
