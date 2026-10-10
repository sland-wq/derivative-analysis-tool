from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def _normal_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


@dataclass
class DerivativeInputs:
    underlying: str = "AAPL"
    derivative_type: str = "option"
    option_style: str = "European"
    option_type: str = "call"
    spot: float = 100.0
    strike: float = 100.0
    expiry_days: float = 30.0
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0
    volatility: float = 0.2
    market_price: float = 0.0
    contract_size: float = 100.0
    market_context: str = ""


def parse_expiry_days(value: Optional[str]) -> float:
    if value is None:
        return 30.0
    try:
        return float(value)
    except ValueError:
        target = datetime.strptime(value, "%Y-%m-%d").date()
        today = datetime.today().date()
        delta = (target - today).days
        return max(delta, 1.0)


def classify_moneyness(spot: float, strike: float, option_type: str) -> str:
    if option_type.lower() == "call":
        if spot > strike:
            return "ITM"
        if abs(spot - strike) < 1e-9:
            return "ATM"
        return "OTM"
    if spot < strike:
        return "ITM"
    if abs(spot - strike) < 1e-9:
        return "ATM"
    return "OTM"


def black_scholes_price(
    spot: float,
    strike: float,
    t: float,
    rate: float,
    dividend: float,
    sigma: float,
    option_type: str,
) -> Dict[str, float]:
    if t <= 0:
        intrinsic = max(spot - strike, 0.0) if option_type.lower() == "call" else max(strike - spot, 0.0)
        return {
            "price": intrinsic,
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "vega": 0.0,
            "rho": 0.0,
            "d1": 0.0,
            "d2": 0.0,
        }

    sqrt_t = math.sqrt(t)
    discount_factor = math.exp(-rate * t)
    dividend_factor = math.exp(-dividend * t)

    d1 = (
        math.log(spot / strike)
        + (rate - dividend + 0.5 * sigma * sigma) * t
    ) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t

    nd1 = _normal_cdf(d1)
    nd2 = _normal_cdf(d2)
    n_minus_d1 = _normal_cdf(-d1)
    n_minus_d2 = _normal_cdf(-d2)

    call_price = spot * dividend_factor * nd1 - strike * discount_factor * nd2
    put_price = strike * discount_factor * n_minus_d2 - spot * dividend_factor * n_minus_d1

    if option_type.lower() == "call":
        price = call_price
    else:
        price = put_price

    pdf_d1 = _normal_pdf(d1)
    delta_call = dividend_factor * nd1
    delta_put = -dividend_factor * n_minus_d1
    gamma = dividend_factor * pdf_d1 / (spot * sigma * sqrt_t)

    theta_call = (
        -spot * dividend_factor * pdf_d1 * sigma / (2.0 * sqrt_t)
        - rate * strike * discount_factor * nd2
        + dividend * spot * dividend_factor * nd1
    )
    theta_put = (
        -spot * dividend_factor * pdf_d1 * sigma / (2.0 * sqrt_t)
        + rate * strike * discount_factor * n_minus_d2
        - dividend * spot * dividend_factor * n_minus_d1
    )

    vega = spot * dividend_factor * pdf_d1 * sqrt_t
    rho_call = strike * t * discount_factor * nd2
    rho_put = -strike * t * discount_factor * n_minus_d2

    if option_type.lower() == "call":
        delta = delta_call
        theta = theta_call
        rho = rho_call
    else:
        delta = delta_put
        theta = theta_put
        rho = rho_put

    return {
        "price": price,
        "delta": delta,
        "gamma": gamma,
        "theta": theta,
        "vega": vega,
        "rho": rho,
        "d1": d1,
        "d2": d2,
    }


def calc_intrinsic_value(spot: float, strike: float, option_type: str) -> float:
    if option_type.lower() == "call":
        return max(spot - strike, 0.0)
    return max(strike - spot, 0.0)


def build_analysis_prompt(inputs: DerivativeInputs, values: Dict[str, Any]) -> str:
    market_price = inputs.market_price or values["price"]
    intrinsic = calc_intrinsic_value(inputs.spot, inputs.strike, inputs.option_type)
    time_value = market_price - intrinsic

    return f"""
You are an expert derivatives analyst and quantitative research assistant. Analyze the following derivative instrument in a structured, professional, and investor-friendly manner.

Inputs:
- Underlying asset: {inputs.underlying}
- Derivative type: {inputs.derivative_type}
- Option style: {inputs.option_style}
- Option type: {inputs.option_type}
- Spot price: {inputs.spot}
- Strike price: {inputs.strike}
- Expiry: {inputs.expiry_days} days
- Risk-free rate: {inputs.risk_free_rate}
- Dividend yield: {inputs.dividend_yield}
- Volatility: {inputs.volatility}
- Market price: {market_price}
- Contract size: {inputs.contract_size}
- Market context: {inputs.market_context or 'Not provided'}

Provide a detailed analysis with the following sections:
1. Executive Summary
2. Structure and Payoff Analysis
3. Fair Value and Pricing
4. Greeks and Sensitivities
5. Risk Breakdown
6. Scenario Analysis
7. Market View and Sentiment
8. Trading and Hedging Interpretation
9. Final Conclusion

Key metrics to present:
- Fair value: {values['price']:.4f}
- Intrinsic value: {intrinsic:.4f}
- Time value: {time_value:.4f}
- Delta: {values['delta']:.4f}
- Gamma: {values['gamma']:.4f}
- Theta: {values['theta']:.4f}
- Vega: {values['vega']:.4f}
- Rho: {values['rho']:.4f}
- Moneyness: {classify_moneyness(inputs.spot, inputs.strike, inputs.option_type)}

Explain whether the derivative looks rich or cheap relative to fair value, how the Greeks drive the trade, and what the main risk is in the current environment.
""".strip()


def analyze_derivative(inputs: DerivativeInputs) -> Dict[str, Any]:
    t = max(inputs.expiry_days / 365.0, 1.0 / 365.0)
    values = black_scholes_price(
        inputs.spot,
        inputs.strike,
        t,
        inputs.risk_free_rate,
        inputs.dividend_yield,
        inputs.volatility,
        inputs.option_type,
    )

    market_price = inputs.market_price or values["price"]
    intrinsic = calc_intrinsic_value(inputs.spot, inputs.strike, inputs.option_type)
    time_value = market_price - intrinsic
    estimate_gap = market_price - values["price"]

    output = {
        "underlying": inputs.underlying,
        "derivative_type": inputs.derivative_type,
        "option_style": inputs.option_style,
        "option_type": inputs.option_type,
        "inputs": asdict(inputs),
        "summary": {
            "fair_value": round(values["price"], 6),
            "market_price": round(market_price, 6),
            "fair_value_gap": round(estimate_gap, 6),
            "intrinsic_value": round(intrinsic, 6),
            "time_value": round(time_value, 6),
            "moneyness": classify_moneyness(inputs.spot, inputs.strike, inputs.option_type),
            "estimated_volatility": inputs.volatility,
        },
        "greeks": {
            "delta": round(values["delta"], 6),
            "gamma": round(values["gamma"], 6),
            "theta": round(values["theta"], 6),
            "vega": round(values["vega"], 6),
            "rho": round(values["rho"], 6),
        },
        "scenario": {
            "bullish_case": "Value benefits from upside move and positive delta exposure.",
            "bearish_case": "Value weakens as underlying falls and time decay continues.",
            "volatility_case": "Higher implied volatility generally supports option value, especially for long options.",
        },
        "prompt": build_analysis_prompt(inputs, values),
    }
    return output


def load_input_file(path: str) -> DerivativeInputs:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return DerivativeInputs(**payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derivative options analysis tool.")
    parser.add_argument("--input-file", type=str, help="Path to a JSON file containing analysis inputs.")
    parser.add_argument("--underlying", type=str, default="AAPL")
    parser.add_argument("--derivative-type", type=str, default="option")
    parser.add_argument("--option-style", type=str, default="European")
    parser.add_argument("--option-type", type=str, default="call")
    parser.add_argument("--spot", type=float, default=100.0)
    parser.add_argument("--strike", type=float, default=100.0)
    parser.add_argument("--expiry-days", type=str, default="30")
    parser.add_argument("--risk-free-rate", type=float, default=0.05)
    parser.add_argument("--dividend-yield", type=float, default=0.0)
    parser.add_argument("--volatility", type=float, default=0.2)
    parser.add_argument("--market-price", type=float, default=None)
    parser.add_argument("--contract-size", type=float, default=100.0)
    parser.add_argument("--market-context", type=str, default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.input_file:
        inputs = load_input_file(args.input_file)
    else:
        inputs = DerivativeInputs(
            underlying=args.underlying,
            derivative_type=args.derivative_type,
            option_style=args.option_style,
            option_type=args.option_type,
            spot=args.spot,
            strike=args.strike,
            expiry_days=parse_expiry_days(args.expiry_days),
            risk_free_rate=args.risk_free_rate,
            dividend_yield=args.dividend_yield,
            volatility=args.volatility,
            market_price=args.market_price,
            contract_size=args.contract_size,
            market_context=args.market_context,
        )

    analysis = analyze_derivative(inputs)
    print(json.dumps({
        "summary": analysis["summary"],
        "greeks": analysis["greeks"],
        "scenario": analysis["scenario"],
    }, indent=2))
    print("\n--- ANALYSIS PROMPT ---\n")
    print(analysis["prompt"])


if __name__ == "__main__":
    main()
