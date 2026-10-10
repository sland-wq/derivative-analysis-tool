# derivative-analysis-tool

A full Python-based derivative analysis tool focused on option-style instruments. It calculates fair value, Greeks, scenario sensitivity, and generates a ready-to-use analyst prompt for a deeper market review.

## Features

- Black-Scholes pricing for option analysis
- Delta, Gamma, Theta, Vega, and Rho calculations
- Intrinsic value and time value analysis
- Moneyness classification
- Scenario grid analysis for spot changes
- AI-friendly analysis prompt generation
- JSON input/output support

## Project structure

- `src/derivative_analysis_tool.py` — main script with pricing and analysis logic
- `src/__init__.py` — package exports
- `prompts/derivative_analysis_prompt.txt` — reusable prompt template
- `data/sample_inputs.json` — sample market input values

## Quick start

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

Or use a JSON file:

```bash
python src/derivative_analysis_tool.py --input-file data/sample_inputs.json
```

## Example outcome

The script prints:

- fair value
- market gap
- intrinsic value and time value
- Greeks
- scenario matrix
- risk summary
- analyst prompt for deeper analysis

## Notes

This version is a stronger working prototype for derivative analysis and is designed to be extended with live option chain ingestion, strategy models, chart rendering, or a web interface.
