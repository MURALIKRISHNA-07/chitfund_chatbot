import re
import streamlit as st
from ai.gemini_client import chat


KEYWORDS = {
    "calculate_chit": [
        "breakdown", "calculate", "profit", "dividend", "schedule",
        "how much", "what is the", "tell me the", "installment",
        "prize amount", "commission", "net amount", "total amount",
        "interest", "return", "maturity", "final amount",
        "generate", "show me", "display", "list", "table",
        "month wise", "monthly detail", "chit detail",
        "how many members", "what is the minimum", "what is the maximum",
        "prize money", "auction amount", "bid amount", "discount amount",
        "foreman share", "organization charges", "admin fee"
    ],
    "recommend_scheme": [
        "recommend", "suggest", "best", "budget", "plan",
        "which scheme", "which plan", "which chit", "what scheme",
        "for me", "suitable", "right", "correct", "appropriate",
        "invest", "investment", "saving", "save", "deposit",
        "monthly", "per month", "each month", "every month",
        "affordable", "low budget", "high return", "good return",
        "business", "education", "marriage", "house", "wedding",
        "goal", "target", "purpose", "need", "want",
        "short term", "long term", "duration", "period",
        "I want", "I need", "I can", "I have", "my budget",
        "how to start", "how to invest", "where to invest",
        "beginner", "first time", "new", "start"
    ],
    "compare_plans": [
        "compare", "comparison", "difference", "versus", "vs",
        "which is better", "which one", "what is better",
        "advantage", "disadvantage", "pros", "cons",
        "benefit", "drawback", "higher", "lower", "more", "less",
        "or", "alternatives", "options", "choices",
        "between", "among", "contrast"
    ],
    "ask_rules": [
        "what is", "how does", "how do", "why", "explain",
        "rules", "regulation", "policy", "terms", "condition",
        "commission", "agent", "foreman", "organizer",
        "auction", "bid", "bidding", "winner", "prize",
        "penalty", "fine", "default", "miss payment", "late payment",
        "registration", "enrollment", "membership",
        "eligible", "eligibility", "requirement", "criteria",
        "process", "procedure", "step", "how to",
        "risk", "safe", "secure", "guarantee", "trust",
        "legal", "law", "act", "government", "RBI",
        "is it legal", "is it safe", "is it secure", "approved",
        "certified", "licensed", "authorized", "registered",
        "how many", "what happens if", "can I", "may I",
        "duration", "period", "time", "how long",
        "minimum", "maximum", "limit", "range"
    ],
    "capture_lead": [
        "contact", "call me", "call back", "callback",
        "phone", "mobile", "number", "my number",
        "my name", "name is", "i am", "i'm",
        "interested", "enquiry", "inquiry", "question",
        "whatsapp", "email", "address",
        "join", "sign up", "enroll",
        "talk to", "speak to", "meet", "visit",
        "share", "give", "provide", "send"
    ]
}


def detect_intent(msg: str) -> str:
    msg_lower = msg.lower().strip()

    # Check recommend_scheme first (monthly budget patterns)
    if re.search(r'\b\d+\s*(per month|monthly|/month|pm)\b', msg_lower):
        return "recommend_scheme"
    if re.search(r'\b(invest|save|saving|budget|deposit|pay)\s+\d+\b', msg_lower):
        return "recommend_scheme"
    if re.search(r'\b\d+\s*(invest|save|budget|deposit|pay)\b', msg_lower):
        return "recommend_scheme"
    if re.search(r'\b(i want|i need|i can|i have|my budget)\b', msg_lower):
        if any(w in msg_lower for w in ["invest", "save", "plan", "scheme", "chit", "month"]):
            return "recommend_scheme"

    # Check capture_lead (personal details)
    if re.search(r'\b(my name|call me|phone|mobile|number|whatsapp|email)\b', msg_lower):
        return "capture_lead"
    if re.search(r'\b(i am|i\'m)\s+\w+', msg_lower):
        return "capture_lead"
    if re.search(r'\b(share|give|provide|send)\s+(me\s+)?(your|contact|number|details)\b', msg_lower):
        return "capture_lead"

    # Check compare_plans
    if re.search(r'\b(compare|versus|vs|which is better|which one|difference)\b', msg_lower):
        return "compare_plans"
    if re.search(r'\b\d+\s*(lakh|lac|00000)\s+(or|versus|vs)\s+\d+\s*(lakh|lac|00000)\b', msg_lower):
        return "compare_plans"
    if re.search(r'\b\d+\s*(lakh|lac|00000)\s+and\s+\d+\s*(lakh|lac|00000)\b', msg_lower):
        return "compare_plans"
    if re.search(r'\b(between|compare|diff)\s+\d+\s*(lakh|lac|00000)\b', msg_lower):
        return "compare_plans"

    # Check calculate_chit (specific chit value with calculation keywords)
    if re.search(r'\b\d+\s*(lakh|lac|00000|crore|cr)\b', msg_lower):
        if any(w in msg_lower for w in KEYWORDS["calculate_chit"]):
            return "calculate_chit"
        if any(w in msg_lower for w in KEYWORDS["recommend_scheme"]):
            return "recommend_scheme"
        return "calculate_chit"

    # Check ask_rules
    if any(w in msg_lower for w in KEYWORDS["ask_rules"]):
        return "ask_rules"

    # Check recommend_scheme (general)
    if any(w in msg_lower for w in KEYWORDS["recommend_scheme"]):
        return "recommend_scheme"

    # Check calculate_chit (general)
    if any(w in msg_lower for w in KEYWORDS["calculate_chit"]):
        return "calculate_chit"

    # Check capture_lead (general)
    if any(w in msg_lower for w in KEYWORDS["capture_lead"]):
        return "capture_lead"

    # LLM fallback
    return _llm_classify(msg)


def _llm_classify(msg: str) -> str:
    prompt = f"""You are an intent classifier for a chit fund chatbot.

Choose EXACTLY ONE intent from the list below.

calculate_chit
- Show breakdown for ₹5 lakh chit
- Calculate dividend
- Profit for ₹2 lakh
- Generate schedule
- Monthly detail for 3 lakh
- How much I get for 200000

find_scheme
- Show ₹5 lakh scheme
- Tell me about 2 lakh plan
- Details of ₹3 lakh chit

recommend_scheme
- I can invest ₹10000 per month
- Suggest a plan
- Which scheme is best for me?
- My budget is ₹8000
- I want to save 15000 monthly

compare_plans
- Compare ₹2 lakh and ₹5 lakh
- Which is better?
- Difference between plans

ask_rules
- What is dividend?
- How does chit work?
- What is commission?
- Explain auction
- Rules of chit fund

capture_lead
- My name is Ravi
- Call me at 9876543210
- I want to join
- My phone is 98xxxxxxxx

learn_chit_fund
- General questions about chit funds

Return ONLY the intent name, nothing else.

User: {msg}"""
    response = chat(prompt).strip().lower()

    valid_intents = ["calculate_chit", "find_scheme", "recommend_scheme", "compare_plans", "ask_rules", "capture_lead", "learn_chit_fund"]
    if response in valid_intents:
        return response
    return "learn_chit_fund"


def store_breakdown(df, summary=None):
    st.session_state.breakdown_df = df
    st.session_state.breakdown_summary = summary


def route(user_msg: str, history: list[dict] = None) -> str:
    intent = detect_intent(user_msg)

    if intent == "recommend_scheme":
        from agents.recommendation_agent import handle
        return handle(user_msg, history)
    elif intent == "calculate_chit":
        from agents.calculation_agent import handle
        return handle(user_msg, history)
    elif intent == "compare_plans":
        from agents.recommendation_agent import handle_compare
        return handle_compare(user_msg)
    elif intent == "capture_lead":
        from agents.lead_agent import handle
        return handle(user_msg, history)
    elif intent == "find_scheme":
        from agents.calculation_agent import handle
        return handle(user_msg, history)
    else:
        from agents.rag_agent import handle
        return handle(user_msg)
