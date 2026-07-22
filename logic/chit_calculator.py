import json
import requests
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from config.settings import SCHEMES_API_URL, SCHEMES_JSON_PATH, FOREMAN_COMMISSION_RATE


def load_schemes() -> list[dict]:
    if SCHEMES_API_URL:
        try:
            resp = requests.get(SCHEMES_API_URL, timeout=5)
            resp.raise_for_status()
            return resp.json().get("groups", [])
        except Exception:
            pass

    with open(SCHEMES_JSON_PATH, "r") as f:
        return json.load(f).get("groups", [])


def find_scheme(chit_value: int, monthly: int = None) -> dict | None:
    for group in load_schemes():
        for s in group["schemes"]:
            if s["value"] == chit_value:
                if monthly is None or s["monthly"] == monthly:
                    return {
                        "value": s["value"],
                        "monthly": s["monthly"],
                        "members": group["members"],
                        "duration": group["duration"],
                    }
    return None


def calculate_prize_amount(chit_value: int, discount_pct: float) -> dict:
    discount = chit_value * discount_pct / 100
    winner_amount = chit_value - discount
    commission = chit_value * FOREMAN_COMMISSION_RATE / 100
    dividend_pool = discount - commission

    return {
        "chit_value": chit_value,
        "discount_pct": discount_pct,
        "discount": discount,
        "winner_amount": winner_amount,
        "foreman_commission": commission,
        "dividend_pool": dividend_pool,
    }


def calculate_dividend(dividend_pool: int, members: int) -> float:
    return dividend_pool / members if members > 0 else 0


def calculate_next_installment(monthly: int, dividend: float) -> float:
    return monthly - dividend


def calculate_maturity_return(monthly: int, duration: int) -> int:
    return monthly * duration


def compare_schemes(chit_values: list[int]) -> list[dict]:
    results = []
    for val in chit_values:
        scheme = find_scheme(val)
        if scheme:
            results.append({
                "chit_value": val,
                "monthly": scheme["monthly"],
                "members": scheme["members"],
                "duration": scheme["duration"],
                "total_invested": scheme["monthly"] * scheme["duration"],
            })
    return results


def recommend_scheme(monthly_budget: int, duration_pref: int = None) -> list[dict]:
    matches = []
    for group in load_schemes():
        for s in group["schemes"]:
            if s["monthly"] <= monthly_budget:
                if duration_pref is None or group["duration"] == duration_pref:
                    matches.append({
                        "value": s["value"],
                        "monthly": s["monthly"],
                        "members": group["members"],
                        "duration": group["duration"],
                    })
    return sorted(matches, key=lambda x: x["value"], reverse=True)


def generate_chit_breakdown(
    value: int,
    monthly: int,
    duration: int,
    members: int,
    commission_percent: float = 5,
    bid_percentages: list[float] = None,
    start_date: str = None,
) -> pd.DataFrame:
    if bid_percentages is None:
        bid_percentages = [35] * duration

    if len(bid_percentages) < duration:
        raise ValueError("Bid percentage list should have one value per month.")

    if start_date is None:
        today = date.today()
        start_date = today.replace(day=1) + relativedelta(months=1)
    else:
        start_date = pd.to_datetime(start_date)

    commission = value * commission_percent / 100

    current_installment = monthly
    last_month_dividend = 0

    data = []

    for i in range(duration):
        month = start_date + relativedelta(months=i)
        bid_percent = bid_percentages[i]
        total_collected = current_installment * members
        auction_amount = value
        bid_offer = auction_amount * bid_percent / 100
        net_amount = auction_amount - bid_offer
        distribution = bid_offer - commission
        per_head_dividend = distribution / members
        next_installment = monthly - per_head_dividend

        data.append({
            "Month": month.strftime("%b-%y"),
            "Instal No": i + 1,
            "Instal Amt Paid by Customer": round(current_installment, 2),
            "No Members": members,
            "Total Amt Collected from Customers": round(total_collected, 2),
            "Last Month Dividend": round(last_month_dividend, 2),
            "Total Amt Available for Auction": round(auction_amount, 2),
            "Bid %": bid_percent,
            "Bid Offer": round(bid_offer, 2),
            "Foreman Commission": round(commission, 2),
            "Net Amount Payable to PS": round(net_amount, 2),
            "Amt Available for Distribution (Dividend)": round(distribution, 2),
            "Per Head Dividend": round(per_head_dividend, 2),
            "Next Month Instalment": round(next_installment, 2),
        })

        current_installment = next_installment
        last_month_dividend = distribution

    df = pd.DataFrame(data)

    total_invested = df["Instal Amt Paid by Customer"].sum()
    total_received = value
    profit = total_received - total_invested

    summary = {
        "Total Amount Invested": round(total_invested, 2),
        "Total Amount Received": round(total_received, 2),
        "Profit": round(profit, 2),
    }

    return df, summary
