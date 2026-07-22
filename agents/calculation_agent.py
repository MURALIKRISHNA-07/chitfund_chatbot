import json
from ai.gemini_client import chat
from config.settings import FOREMAN_COMMISSION_RATE
from tools import (
    find_scheme_by_value,
    find_scheme_by_budget,
    generate_chit_breakdown,
)
from logic.chit_calculator import (
    calculate_prize_amount,
    calculate_dividend,
    calculate_next_installment,
)


def _extract_values(user_msg: str, history: list[dict] = None) -> dict:
    history_text = ""
    if history:
        recent = history[-4:]
        history_text = "\n".join([f"{m['role']}: {m['text'][:100]}" for m in recent])

    prompt = f"""Extract chit fund calculation values from this message.
Consider the conversation history for context.

Return JSON only: {{"chit_value": number, "discount_pct": number, "question_type": "string"}}

chit_value: the chit value in rupees (e.g., 500000 for 5 lakh)
discount_pct: discount percentage if mentioned (e.g., 35 for 35%)
question_type: one of "breakdown", "dividend", "profit", "summary", "general"

Examples:
- "5 lakh chit" → {{"chit_value": 500000, "discount_pct": null, "question_type": "summary"}}
- "5 lakh breakdown" → {{"chit_value": 500000, "discount_pct": null, "question_type": "breakdown"}}
- "what is dividend for 5 lakh" → {{"chit_value": 500000, "discount_pct": null, "question_type": "dividend"}}
- "profit in 5 lakh chit" → {{"chit_value": 500000, "discount_pct": null, "question_type": "profit"}}

If no chit value mentioned, use null.
Message: {user_msg}"""
    response = chat(prompt)
    try:
        data = json.loads(response)
        return {
            "chit_value": data.get("chit_value"),
            "discount_pct": data.get("discount_pct"),
            "question_type": data.get("question_type", "general"),
        }
    except Exception:
        return {"chit_value": None, "discount_pct": None, "question_type": "general"}


def handle(user_msg: str, history: list[dict] = None) -> str:
    params = _extract_values(user_msg, history)
    chit_value = params.get("chit_value")
    question_type = params.get("question_type", "general")

    if chit_value is None:
        return (
            "Please tell me the chit value you'd like to know about.\n\n"
            "For example:\n"
            "- \"5 lakh chit\"\n"
            "- \"2,00,000 chit breakdown\"\n"
            "- \"what is dividend for 10 lakh\"\n"
            "- \"profit in 3 lakh chit\""
        )

    scheme = find_scheme_by_value(chit_value)
    if scheme is None:
        available = find_scheme_by_budget(999999999)
        values = sorted(set(s["value"] for s in available))
        values_str = " | ".join([f"₹{v:,}" for v in values])
        return f"No scheme found for ₹{chit_value:,}. Available: {values_str}"

    monthly = scheme["monthly"]
    members = scheme["members"]
    duration = scheme["duration"]
    discount_pct = params.get("discount_pct") or 35

    result = calculate_prize_amount(chit_value, discount_pct)
    dividend = calculate_dividend(result["dividend_pool"], members)
    next_inst = calculate_next_installment(monthly, dividend)

    if question_type == "dividend":
        return (
            f"**For ₹{chit_value:,} chit ({members} members):**\n\n"
            f"Dividend Pool: ₹{result['dividend_pool']:,}\n"
            f"**Your Dividend: ₹{dividend:,.2f}**\n\n"
            f"This dividend is distributed among all {members} members equally."
        )

    if question_type == "profit":
        df, invest_summary = generate_chit_breakdown(
            value=chit_value, monthly=monthly, duration=duration,
            members=members, commission_percent=FOREMAN_COMMISSION_RATE,
        )
        from agents.conversation_agent import store_breakdown
        store_breakdown(df, invest_summary)
        return (
            f"**For ₹{chit_value:,} chit:**\n\n"
            f"Total Invested: ₹{invest_summary['Total Amount Invested']:,.2f}\n"
            f"Total Received: ₹{invest_summary['Total Amount Received']:,}\n"
            f"**Your Profit: ₹{invest_summary['Profit']:,.2f}**\n\n"
            f"*Full month-by-month breakdown shown below.*"
        )

    df, invest_summary = generate_chit_breakdown(
        value=chit_value, monthly=monthly, duration=duration,
        members=members, commission_percent=FOREMAN_COMMISSION_RATE,
    )
    from agents.conversation_agent import store_breakdown
    store_breakdown(df, invest_summary)

    return (
        f"**₹{chit_value:,} Chit Summary:**\n\n"
        f"Monthly: ₹{monthly:,} | Members: {members} | Duration: {duration} months\n"
        f"Discount: {discount_pct}% = ₹{result['discount']:,}\n"
        f"Winner Gets: ₹{result['winner_amount']:,}\n"
        f"Foreman Commission: ₹{result['foreman_commission']:,}\n"
        f"Dividend per Member: ₹{dividend:,.2f}\n"
        f"Next Installment: ₹{next_inst:,.2f}\n\n"
        f"Total Invested: ₹{invest_summary['Total Amount Invested']:,.2f}\n"
        f"Profit: ₹{invest_summary['Profit']:,.2f}\n\n"
        f"*Full month-by-month breakdown shown below.*"
    )
