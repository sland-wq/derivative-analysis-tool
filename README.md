# derivative-analysis-tool

A lightweight Python derivatives analysis tool for option-like instruments. It calculates fair value with Black-Scholes, derives key Greeks, classifies moneyness, and generates an AI-ready analysis prompt for deeper investment or risk review.

## Features

- Option pricing using Black-Scholes
- Delta, Gamma, Theta, Vega, and Rho
- Intrinsic and time value analysis
- Moneyness classification (ITM / ATM / OTM)
- AI prompt generation for analyst workflows
- JSON sample inputs for quick testing

## Project structure

- `src/derivative_analysis_tool.py` — analysis engine
- `prompts/derivative_analysis_prompt.txt` — reusable prompt template
- `data/sample_inputs.json` — example input values

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

You can also load a JSON file:

```bash
python src/derivative_analysis_tool.py --input-file data/sample_inputs.json
```

## Example output

The tool prints a JSON summary including:

- fair value
- market gap
- intrinsic value
- time value
- Greeks
- moneyness
- an AI analysis prompt

## Notes

This is a clean starter implementation and is suitable for educational and prototype work. It is designed to be extended with live market data, option chains, or a user interface.
