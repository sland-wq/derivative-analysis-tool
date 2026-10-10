# derivative-analysis-tool

A small Python-based derivatives analysis tool for options and structured derivative scenarios. It calculates Black-Scholes pricing metrics, Greeks, moneyness, and generates a polished derivative analysis prompt for AI-assisted review.

## Features

- Option pricing and fair value estimation
- Delta, Gamma, Theta, Vega, and Rho calculations
- Moneyness classification
- Intrinsic value and time value analysis
- Scenario-ready prompt generation for deeper analysis
- JSON output for automation and dashboards

## Project structure

- `src/derivative_analysis_tool.py` — main analysis engine
- `prompts/derivative_analysis_prompt.txt` — reusable prompt template
- `data/sample_inputs.json` — sample values for quick testing

## Quick start

1. Clone the repo
2. Run the tool:

```bash
python src/derivative_analysis_tool.py \
  --underlying AAPL \
  --derivative-type option \
  --option-type call \
  --spot 205 \
  --strike 210 \
  --expiry-days 30 \
  --risk-free-rate 0.05 \
  --dividend-yield 0.01 \
  --volatility 0.22 \
  --market-price 3.25 \
  --contract-size 100
```

3. The script prints:
   - a numeric pricing summary
   - a prompt ready for a GPT-style derivative analyst

## Example output

The tool returns a structured dictionary including:

- fair value
- intrinsic value
- time value
- delta / gamma / theta / vega / rho
- moneyness
- estimated scenarios
- AI prompt text

## Sample input file

You can also load a JSON file:

```bash
python src/derivative_analysis_tool.py --input-file data/sample_inputs.json
```

## Notes

This is a lightweight starter project intended for analysis and education. For production use, you can extend it with live market data, option-chain ingestion, calibration, or a web UI.
