import json
from ai.gemini_client import chat
from tools import find_scheme_by_budget
from config.settings import FOREMAN_COMMISSION_RATE
from logic.chit_calculator import (
    calculate_prize_amount,
    calculate_dividend,
    generate_chit_breakdown,
)


def _extract_user_goals(user_msg: str, history: list[dict] = None) -> dict:
    history_text = ""
    if history:
        recent = history[-6:]
        history_text = "\n".join([f"{m['role']}: {m['text'][:150]}" for m in recent])

    prompt = f"""Extract user goals for chit fund investment from this message.

Return JSON only: {{
    "monthly_budget": number or null,
    "duration": number or null,
    "goal": "string",
    "need_early_prize": boolean
}}

goal options: "savings", "business", "investment", "education", "marriage", "house", "other"
need_early_prize: true if user wants to win auction early (first 50% of duration)

IMPORTANT: Look for any number followed by "per month", "monthly", "invest", "save", "budget" → that is monthly_budget.
Look for any number followed by "months", "weeks", "duration", "years" → that is duration.

Examples:
- "I can save 8000 per month" → {{"monthly_budget": 8000, "duration": null, "goal": "savings", "need_early_prize": false}}
- "I want to invest 10000 per month" → {{"monthly_budget": 10000, "duration": null, "goal": "savings", "need_early_prize": false}}
- "10000 per month for 20 months" → {{"monthly_budget": 10000, "duration": 20, "goal": "savings", "need_early_prize": false}}
- "I need 5 lakh for business in 2 years" → {{"monthly_budget": null, "duration": 24, "goal": "business", "need_early_prize": true}}
- "15000 monthly for my child's education" → {{"monthly_budget": 15000, "duration": null, "goal": "education", "need_early_prize": false}}

If not mentioned, use null for numbers, "savings" for goal, false for need_early_prize.
Message: {user_msg}"""
    response = chat(prompt)
    try:
        return json.loads(response)
    except Exception:
        return {"monthly_budget": None, "duration": None, "goal": "savings", "need_early_prize": False}


def _calculate_scheme_stats(scheme: dict) -> dict:
    value = scheme["value"]
    monthly = scheme["monthly"]
    members = scheme["members"]
    duration = scheme["duration"]

    result = calculate_prize_amount(value, 35)
    dividend = calculate_dividend(result["dividend_pool"], members)

    df, invest_summary = generate_chit_breakdown(
        value=value, monthly=monthly, duration=duration,
        members=members, commission_percent=FOREMAN_COMMISSION_RATE,
    )

    return {
        "chit_value": value,
        "monthly": monthly,
        "members": members,
        "duration": duration,
        "winner_amount": result["winner_amount"],
        "dividend_per_month": dividend,
        "total_invested": invest_summary["Total Amount Invested"],
        "profit": invest_summary["Profit"],
        "profit_percent": round(invest_summary["Profit"] / invest_summary["Total Amount Invested"] * 100, 1),
    }


def handle(user_msg: str, history: list[dict] = None) -> str:
    goals = _extract_user_goals(user_msg, history)
    budget = goals.get("monthly_budget")
    duration = goals.get("duration")
    goal = goals.get("goal", "savings")
    need_early = goals.get("need_early_prize", False)

    if budget is None and duration is None:
        return (
            "I'd be happy to recommend the right chit scheme for you!\n\n"
            "Please tell me:\n"
            "1. **Monthly budget** - How much can you invest per month?\n"
            "2. **Purpose** (optional) - Savings, business, education, marriage, house?\n"
            "3. **Duration** (optional) - Like 20, 30, 40, or 50 months"
        )

    results = find_scheme_by_budget(budget if budget else 999999999)
    if duration:
        results = [s for s in results if s["duration"] == duration]

    if not results:
        if budget:
            return f"No schemes match ₹{budget:,}/month for {duration} months. Try a different budget or duration."
        return f"No schemes found for {duration} months duration."

    stats = [_calculate_scheme_stats(s) for s in results[:5]]

    goal_reasons = {
        "savings": "helps you build wealth steadily with dividends",
        "business": "gives you a lump sum to invest in your business",
        "education": "helps you save for education expenses",
        "marriage": "helps you accumulate funds for marriage",
        "house": "helps you save for a down payment",
        "investment": "offers good returns through dividends",
    }

    lines = [f"**Recommended Schemes for Your {goal.title()} Goal:**\n"]

    for s in stats:
        lines.append(f"**₹{s['chit_value']:,} Chit**")
        lines.append(f"- Monthly: ₹{s['monthly']:,} | Duration: {s['duration']} months")
        lines.append(f"- You receive: ₹{s['winner_amount']:,} when you win auction")
        lines.append(f"- Monthly dividend: ₹{s['dividend_per_month']:,.2f}")
        lines.append(f"- Total invested: ₹{s['total_invested']:,.2f}")
        lines.append(f"- Your profit: ₹{s['profit']:,.2f} ({s['profit_percent']}%)")

        if need_early and s["duration"] <= 30:
            lines.append(f"- *Good for early win - shorter duration*")
        elif not need_early:
            lines.append(f"- *{goal_reasons.get(goal, goal_reasons['savings'])}*")
        lines.append("")

    lines.append("Would you like a detailed breakdown of any scheme?")
    return "\n".join(lines)


def handle_compare(user_msg: str) -> str:
    import re
    from tools import find_scheme_by_value, calculate_profit
    
    msg = user_msg.lower()
    
    values = []
    
    patterns = [
        r'(\d+)\s*(lakh|lac)',
        r'(\d+)\s*00000',
        r'(\d+)\s*crore',
        r'(\d+)\s*0000000',
        r'₹?\s*(\d[\d,]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, msg)
        for match in matches:
            if isinstance(match, tuple):
                num = match[0].replace(',', '')
                unit = match[1] if len(match) > 1 else ''
            else:
                num = match.replace(',', '')
                unit = ''
            
            if 'lakh' in unit or 'lac' in unit:
                values.append(int(num) * 100000)
            elif 'crore' in unit:
                values.append(int(num) * 10000000)
            elif len(num) >= 5:
                values.append(int(num))
    
    if len(values) < 2:
        all_schemes = []
        from logic.chit_calculator import load_schemes
        for group in load_schemes():
            for s in group["schemes"]:
                all_schemes.append(s["value"])
        all_schemes = sorted(set(all_schemes))[:4]
        values = all_schemes
    
    results = []
    for val in values[:4]:
        scheme = find_scheme_by_value(val)
        if scheme:
            profit_data = calculate_profit(
                val, scheme["monthly"], scheme["duration"], scheme["members"]
            )
            results.append({
                "chit_value": val,
                "monthly": scheme["monthly"],
                "members": scheme["members"],
                "duration": scheme["duration"],
                "total_invested": profit_data["Total Amount Invested"],
                "profit": profit_data["Profit"],
            })
    
    if not results:
        return "No schemes found to compare. Available values: ₹1,00,000 | ₹2,00,000 | ₹3,00,000 | ₹5,00,000"
    
    lines = ["**Comparison of Chit Schemes:**\n"]
    lines.append("| Chit Value | Monthly | Members | Duration | Total Invested | Profit |")
    lines.append("|------------|---------|---------|----------|----------------|--------|")
    
    for s in results:
        lines.append(
            f"| ₹{s['chit_value']:,} | ₹{s['monthly']:,} | {s['members']} | {s['duration']} months | ₹{s['total_invested']:,.2f} | ₹{s['profit']:,.2f} |"
        )
    
    lines.append("")
    lines.append("**Key Differences:**")
    
    if len(results) >= 2:
        r1, r2 = results[0], results[1]
        lines.append(f"- **₹{r1['chit_value']:,}**: Monthly ₹{r1['monthly']:,} | You invest ₹{r1['total_invested']:,.2f} | Profit ₹{r1['profit']:,.2f}")
        lines.append(f"- **₹{r2['chit_value']:,}**: Monthly ₹{r2['monthly']:,} | You invest ₹{r2['total_invested']:,.2f} | Profit ₹{r2['profit']:,.2f}")
    
    lines.append("")
    lines.append("Would you like a detailed breakdown of any scheme?")
    return "\n".join(lines)
