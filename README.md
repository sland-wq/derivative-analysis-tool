import streamlit as st

from src.derivative_analysis_tool import DerivativeInputs, analyze_derivative


st.set_page_config(page_title="Derivative Analysis Tool", layout="wide")
st.title("Derivative Analysis Web App")
st.caption("Analyze option-style derivatives with fair value, Greeks, risk, and AI-ready insights.")

with st.form("derivative_form"):
    col1, col2 = st.columns(2)

    with col1:
        underlying = st.text_input("Underlying", value="AAPL")
        derivative_type = st.selectbox("Derivative Type", ["option", "future", "swap", "structured product", "other"])
        option_style = st.selectbox("Option Style", ["European", "American", "Asian", "Barrier", "Binary", "Other"])
        option_type = st.selectbox("Option Type", ["call", "put"])
        spot = st.number_input("Spot", value=205.0, step=1.0)
        strike = st.number_input("Strike", value=210.0, step=1.0)

    with col2:
        expiry_days = st.number_input("Expiry Days", min_value=1, value=30)
        risk_free_rate = st.number_input("Risk-free Rate", value=0.05, step=0.005, format="%.4f")
        dividend_yield = st.number_input("Dividend Yield", value=0.01, step=0.001, format="%.4f")
        volatility = st.number_input("Volatility", value=0.22, step=0.01, format="%.4f")
        market_price = st.number_input("Market Price", value=3.25, step=0.05, format="%.4f")
        contract_size = st.number_input("Contract Size", value=100.0, step=1.0)
        market_context = st.text_area("Market Context", value="AI-driven earnings expectations and elevated volatility.")

    submitted = st.form_submit_button("Analyze Derivative")

if submitted:
    inputs = DerivativeInputs(
        underlying=underlying,
        derivative_type=derivative_type,
        option_style=option_style,
        option_type=option_type,
        spot=float(spot),
        strike=float(strike),
        expiry_days=float(expiry_days),
        risk_free_rate=float(risk_free_rate),
        dividend_yield=float(dividend_yield),
        volatility=float(volatility),
        market_price=float(market_price),
        contract_size=float(contract_size),
        market_context=market_context,
    )

    analysis = analyze_derivative(inputs)

    st.subheader("Summary")
    summary = analysis["summary"]
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Fair Value", f"{summary['fair_value']:.4f}")
    col_b.metric("Market Price", f"{summary['market_price']:.4f}")
    col_c.metric("Intrinsic", f"{summary['intrinsic_value']:.4f}")
    col_d.metric("Time Value", f"{summary['time_value']:.4f}")

    st.write(f"Moneyness: {summary['moneyness']}")
    st.write(f"Fair value gap: {summary['fair_value_gap']:.4f}")

    tab1, tab2, tab3, tab4 = st.tabs(["Greeks", "Scenarios", "Risk", "AI Prompt"])

    with tab1:
        greeks = analysis["greeks"]
        st.json(greeks)

    with tab2:
        scenarios = analysis["scenarios"]
        st.json(scenarios)

    with tab3:
        st.json(analysis["risk_summary"])

    with tab4:
        st.text_area("AI Analysis Prompt", analysis["analysis_prompt"], height=420)

    st.markdown("---")
    st.subheader("Interpretation")
    st.write(
        "This tool estimates the option's theoretical fair value, highlights the primary Greek exposures, and produces a structured prompt for deeper qualitative analysis. "
        "Use the scenario grid to understand how price moves and volatility shifts can affect the position."
    )
