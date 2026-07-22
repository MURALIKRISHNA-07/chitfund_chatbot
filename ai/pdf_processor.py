import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uuid
from datetime import datetime, timezone

from ai.embeddings import get_embedding, get_sparse_embedding
from ai.vector_store import upsert_vectors
from qdrant_client.models import PointStruct


KNOWLEDGE_BASE = [
    # ── Definitions ──────────────────────────────────────────────
    {
        "title": "What is a Chit Fund?",
        "category": "definition",
        "intent": "knowledge",
        "tags": ["chit fund", "definition", "what is", "meaning", "introduction"],
        "text": """A chit fund is a financial savings and borrowing instrument popular in India. It is a scheme where a group of individuals come together and contribute a fixed sum of money every month. The total collected amount is then given to one member each month through a reverse auction process. Members can bid for the prize money by offering the highest discount. The chit fund runs for a duration equal to the number of members, ensuring everyone gets a turn to receive the prize money. It combines the benefits of savings and credit in a single financial product."""
    },
    {
        "title": "What is Dividend?",
        "category": "definition",
        "intent": "knowledge",
        "tags": ["dividend", "distribution", "share", "discount", "profit"],
        "text": """Dividend is the portion of the successful bid discount that is distributed equally among all subscribers after deducting the foreman's commission. When a member wins the auction with a discount offer, that discount amount minus the foreman's commission is divided equally among all members. The dividend reduces the next month's installment for each member. For example, if the discount is Rs.1,75,000 and foreman commission is Rs.25,000, the total dividend is Rs.1,50,000. Divided among 50 members, each gets Rs.3,000 as dividend."""
    },
    {
        "title": "What is Prize Money?",
        "category": "definition",
        "intent": "knowledge",
        "tags": ["prize money", "winner amount", "net amount", "bid amount"],
        "text": """Prize Money (also called Net Amount or Winner Amount) is the amount received by the winning bidder in a chit fund auction. It is calculated as: Prize Money = Gross Chit Amount minus Bid Offer Amount. For example, in a Rs.5,00,000 chit with a 35% bid discount, the Prize Money is Rs.3,25,000 (Rs.5,00,000 - Rs.1,75,000). The winner receives this amount and pays reduced installments in subsequent months."""
    },
    {
        "title": "What is Foreman Commission?",
        "category": "definition",
        "intent": "knowledge",
        "tags": ["foreman", "commission", "agent", "organizer", "charges", "fee"],
        "text": """Foreman Commission (also called Agent Commission or Organization Charges) is the fee charged by the chit fund organizer (foreman) for managing the chit fund. It is typically 5% of the gross chit amount. This commission is deducted from the bid discount amount before calculating the dividend. For example, in a Rs.5,00,000 chit, the foreman commission is Rs.25,000 (5% of Rs.5,00,000). The foreman manages all administrative tasks including conducting auctions, maintaining records, and distributing payments."""
    },
    {
        "title": "What is Bid Offer Amount?",
        "category": "definition",
        "intent": "knowledge",
        "tags": ["bid", "offer", "discount", "auction bid", "percentage"],
        "text": """Bid Offer Amount is the amount a subscriber is willing to forego (discount) to win the prize money in an auction. It is expressed as a percentage of the gross chit amount. The minimum bid is 5% (foreman commission) and the maximum is 40% as per law. For example, in a Rs.5,00,000 chit, a 35% bid means the subscriber foregoes Rs.1,75,000. The bid offer amount determines the dividend distributed to all members."""
    },
    {
        "title": "What is Gross Chit Amount?",
        "category": "definition",
        "intent": "knowledge",
        "tags": ["gross amount", "chit amount", "total", "pool", "pot"],
        "text": """Gross Chit Amount (also called Total Pot Value or Pool Amount) is the total money collected from all members in a given month. It is calculated as: Monthly Installment multiplied by Number of Members. For example, in a chit with 50 members paying Rs.10,000 each, the Gross Chit Amount is Rs.5,00,000. This amount is used in the auction process each month."""
    },
    {
        "title": "What is Monthly Installment?",
        "category": "definition",
        "intent": "knowledge",
        "tags": ["installment", "monthly", "subscription", "contribution", "payment"],
        "text": """Monthly Installment (also called Subscription or Contribution) is the fixed amount each member pays every month to the chit fund. This amount remains constant throughout the chit duration. For example, in a Rs.5,00,000 chit with 50 members, each member pays Rs.10,000 per month. The installment may be reduced in subsequent months if dividend is received."""
    },
    {
        "title": "What is Reverse Auction?",
        "category": "definition",
        "intent": "knowledge",
        "tags": ["reverse auction", "auction", "bidding", "process"],
        "text": """A reverse auction in a chit fund is where members compete to offer the highest discount to win the prize money. Unlike regular auctions where buyers compete to pay the highest price, in a chit fund auction, members compete to accept the lowest amount. The member who offers the highest discount (lowest net amount) wins the auction and receives the prize money. This process ensures fair distribution and market-driven pricing."""
    },
    {
        "title": "What is Next Month Installment?",
        "category": "definition",
        "intent": "knowledge",
        "tags": ["next installment", "reduced amount", "net payment"],
        "text": """Next Month Installment is the reduced amount a member pays in the month following the auction. It is calculated as: Monthly Installment minus Dividend Received. For example, if monthly installment is Rs.10,000 and dividend received is Rs.3,000, the next month installment is Rs.7,000. This reduced installment continues for all members after each auction."""
    },

    # ── Process ──────────────────────────────────────────────────
    {
        "title": "How Does a Chit Fund Work?",
        "category": "process",
        "intent": "knowledge",
        "tags": ["how", "works", "process", "mechanism", "steps"],
        "text": """How Does A Chit Fund Work?
Simply put, the chit fund begins on a specified date and continues for the number of months equal to the number of subscribers. Members contribute their monthly installments to the pot, and a reverse auction is conducted each month allowing members to bid for the Prize Money.
The subscriber willing to take the lowest sum with the lowest bid is declared the winner and receives the Prize Money for that month. The balance amount is distributed as a dividend among all members after deducting the Foreman's Commission (5%). The process is repeated each month, thus allowing each member to win the Prize Money. A Chit fund offers you the unique advantage of allowing you to borrow from your future savings."""
    },
    {
        "title": "Monthly Auction Process",
        "category": "process",
        "intent": "knowledge",
        "tags": ["auction", "monthly", "bidding", "winner", "process"],
        "text": """Auction Process:
- The Highest Bidder/Prized Subscriber wins the Prize Money for that month.
- Example: Auction confirmed at 35% discount (Rs.1,75,000)
- Out of Rs.5,00,000 pooled:
  * Rs.3,25,000 goes to highest bidder
  * Rs.25,000 (5%) goes to Foreman (Muthoot Chits)
  * Rs.1,50,000 distributed equally to all 50 members
- Each member gets Rs.3,000 (1,50,000/50) as Dividend
- Next month, subscriber pays only Rs.7,000 (10,000 - 3,000)"""
    },
    {
        "title": "Registration Process",
        "category": "process",
        "intent": "knowledge",
        "tags": ["registration", "enrollment", "join", "how to", "start"],
        "text": """Activities after Receiving Prior Sanction from The Registrar of Chits:
1. Following receipt of the Prior Sanction, the Foreman can announce the launch of the Chit Fund and begin selling tickets.
2. After selling all of the tickets, the Foreman will register the agreement with the Registrar and obtain the Commencement Certificate to hold the first auction.
3. The contribution will be made in the form of a fixed monthly installment (Rs.10,000 per month).
4. From the second month onwards, the members will be able to bid for the Prize Money from the collected funds through a reverse auction.
5. 40% is the maximum discount anyone can quote (as per Law)."""
    },
    {
        "title": "Auction Participation Options",
        "category": "process",
        "intent": "knowledge",
        "tags": ["participation", "how to bid", "bid", "auction", "proxy"],
        "text": """Participating in The Auction:
A member can participate in the auction for the Prize Money from the second month onwards. The first month's Gross Chit Amount goes to the company. To be eligible to make a bid, the subscriber should have paid all the installments and not have any pending ones.

Options to Participate:
1. Direct Participation: The member can either participate online or personally attend the auction in the Chit office on the date and time specified in the Chit Fund agreement.
2. Bid Offer Letter: The subscriber needs to fill in all the details in the letter before signing and sending it to the Chit's office.
3. Bid Authorization Letter: The customer can send a proxy to participate in the auction on their behalf. The proxy must carry the authorization letter and valid ID proof to participate."""
    },

    # ── Examples ─────────────────────────────────────────────────
    {
        "title": "Rs.5 Lakh Chit Fund Example",
        "category": "example",
        "intent": "knowledge",
        "tags": ["example", "5 lakh", "calculation", "illustration", "sample"],
        "text": """Example: Assume a chit fund scheme with 50 members that will run for 50 months, with each paying a monthly installment of Rs.10,000 to create a Rs.5,00,000 pot. When the auction is announced, the member who bids the highest discount wins the Bid. (40% is the maximum discount anyone can bid as per Law).

Complete Breakdown:
- Number of members: 50
- Duration: 50 months
- Monthly installment: Rs.10,000
- Total pot value: Rs.5,00,000 (50 x 10,000)
- Winning Bid discount: 35%
- Discount amount: Rs.1,75,000 (35% of 5,00,000)
- Amount received by winner: Rs.3,25,000 (5,00,000 less 1,75,000)
- Foreman's commission: 5% = Rs.25,000
- Total Dividend: Rs.1,50,000 (1,75,000 less 25,000)
- Dividend per member: Rs.3,000 (1,50,000/50)
- Next month installment: Rs.7,000 (10,000 - 3,000)

Keep this entire example together. Do not split it."""
    },
    {
        "title": "Investment Return Example",
        "category": "example",
        "intent": "knowledge",
        "tags": ["return", "profit", "investment", "example", "maturity"],
        "text": """Investment Return Example:
If someone waits to win the Prize Money at the end of the period:
- Total Amount Invested = Rs.4,19,500
- Total Amount Received = Rs.5 lakhs
- Profit = Rs.52,500

Note: The above calculation is only an illustration; the actual return is determined by the auction discount decided by the Chit Fund subscribers."""
    },

    # ── Benefits ─────────────────────────────────────────────────
    {
        "title": "Benefits of Chit Funds",
        "category": "benefits",
        "intent": "knowledge",
        "tags": ["benefits", "advantages", "why", "good", "reasons"],
        "text": """Key Benefits of Chit Funds:
1. Immediate Financial Assistance: Access to lump-sum amount whenever needed without restrictions.
2. Easy Accessibility: Simple and convenient compared to traditional financial institutions with minimal documentation.
3. Disciplined Savings Habit: Encourages regular monthly savings without market fluctuations.
4. Dual Benefit of Savings and Credit: Systematic savings plus easy access to credit.
5. Flexible Usage of Funds: Can be used for emergencies, weddings, education, medical expenses, home improvements.
6. Business Finance Support: Source of finance for entrepreneurs to start business, manage working capital, purchase equipment.
7. Financial Inclusion: Support for those who may not qualify for traditional bank loans.
8. Regular Returns Through Dividends: Monthly dividends reduce contribution burden.
9. Emergency Financial Reserve: Quick access to funds for urgent needs.
10. Higher Return Potential: Better returns compared to traditional savings options.
11. Social Bonding and Community Support: Brings together people from same locality or workplace.
12. Freedom and Convenience: Freedom to use winnings according to priorities.
13. Suitable for Different Financial Needs: Beneficial for housewives, salaried employees, small business owners, and families."""
    },
    {
        "title": "Chit Funds for Savings",
        "category": "benefits",
        "intent": "knowledge",
        "tags": ["savings", "save", "money", "habit", "discipline"],
        "text": """Chit Funds for Savings:
Chit funds encourage a disciplined savings habit by requiring regular monthly contributions. Unlike traditional savings accounts, chit funds offer the dual benefit of savings and credit. Members receive dividends that reduce their monthly installment burden. The systematic approach helps build wealth over time. At maturity, members receive the full prize amount, which is higher than their total investment due to dividends earned throughout the period."""
    },
    {
        "title": "Chit Funds for Business",
        "category": "benefits",
        "intent": "knowledge",
        "tags": ["business", "entrepreneur", "startup", "capital", "working capital"],
        "text": """Chit Funds for Business:
Chit funds are an excellent source of finance for entrepreneurs and small business owners. They provide lump-sum amounts that can be used for starting a business, managing working capital, purchasing equipment, or expanding operations. Unlike bank loans, chit funds do not require collateral or extensive documentation. The flexible usage of funds allows entrepreneurs to invest in their business according to their specific needs."""
    },
    {
        "title": "Chit Funds for Emergency",
        "category": "benefits",
        "intent": "knowledge",
        "tags": ["emergency", "urgent", "medical", "crisis", "quick"],
        "text": """Chit Funds for Emergency:
Chit funds serve as an excellent emergency financial reserve. Members can access quick funds through the auction process for urgent needs like medical emergencies, unexpected expenses, or financial crises. The prize money can be received within a month of winning the auction, providing immediate financial relief. This makes chit funds a reliable alternative to emergency loans or credit card debt."""
    },

    # ── FAQ ──────────────────────────────────────────────────────
    {
        "title": "Can I Bid in Every Auction?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["bid", "auction", "participate", "every", "frequency"],
        "text": """Question: Can I bid in every auction?
Answer: Yes, you can participate in the auction from the second month onwards. To be eligible to make a bid, you should have paid all your installments and not have any pending ones. You can participate in every subsequent auction until you win the prize money. Once you win, you cannot bid again until all other members have also won."""
    },
    {
        "title": "What Happens if I Miss a Payment?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["miss", "payment", "default", "penalty", "late"],
        "text": """Question: What happens if I miss a payment?
Answer: If a member misses a payment, they may face penalties as per the chit fund agreement. Missing payments can result in:
1. Late payment charges or penalties
2. Disqualification from participating in auctions until payments are regularized
3. Potential legal action in case of prolonged default
4. Loss of accrued dividends
It is important to maintain regular payments to continue enjoying the benefits of the chit fund."""
    },
    {
        "title": "Who Gets the Dividend?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["dividend", "who gets", "distribution", "receive"],
        "text": """Question: Who gets the dividend?
Answer: The dividend is distributed equally among ALL members of the chit fund, including the winner of the auction. After deducting the foreman's commission from the bid discount amount, the remaining dividend is divided equally among all subscribers. This means even the auction winner receives a share of the dividend, reducing their effective cost."""
    },
    {
        "title": "What is the Maximum Discount I Can Bid?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["maximum", "discount", "bid", "limit", "40%"],
        "text": """Question: What is the maximum discount I can bid?
Answer: As per Indian law, the maximum discount anyone can bid is 40% of the gross chit amount. The minimum bid is 5% (which is the foreman commission). For example, in a Rs.5,00,000 chit, the maximum discount is Rs.2,00,000 (40%) and the minimum is Rs.25,000 (5%). The actual discount depends on market conditions and competition among members."""
    },
    {
        "title": "Can I Use Chit Fund for Education?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["education", "school", "college", "fees", "child"],
        "text": """Question: Can I use chit fund for education?
Answer: Yes, chit funds are suitable for education expenses. Many members join chit funds specifically to save for their children's education. The prize money received can be used for school fees, college tuition, educational materials, or study abroad expenses. The disciplined monthly savings helps accumulate a significant amount over time."""
    },
    {
        "title": "Is Chit Fund Safe?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["safe", "secure", "risk", "trust", "legal"],
        "text": """Question: Is chit fund safe?
Answer: Registered chit funds regulated by the Registrar of Chits are safe. They operate under the Chit Funds Act, 1982, which provides legal protection to subscribers. Key safety features include:
1. Government regulation and oversight
2. Foreman must provide security/bond
3. Regular auditing of accounts
4. Legal recourse in case of disputes
However, always ensure you join a registered and reputable chit fund company."""
    },
    {
        "title": "What is the Minimum Duration?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["minimum", "duration", "time", "period", "shortest"],
        "text": """Question: What is the minimum duration?
Answer: The minimum duration of a chit fund depends on the number of members. Typically, chit funds run for 20, 25, 30, 40, or 50 months. Shorter duration chit funds (20-30 months) are available but may have different terms. The duration is always equal to the number of members in the chit fund."""
    },
    {
        "title": "How Many Members Can Join?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["members", "how many", "group", "size", "participants"],
        "text": """Question: How many members can join?
Answer: The number of members in a chit fund determines its duration. Common configurations are:
- 20 members: 20 months duration
- 25 members: 25 months duration
- 30 members: 30 months duration
- 40 members: 40 months duration
- 50 members: 50 months duration
The number of members can range from 20 to 50, with 50 being the most common size."""
    },
    {
        "title": "Can I Join Multiple Chit Funds?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["multiple", "join", "more than one", "several"],
        "text": """Question: Can I join multiple chit funds?
Answer: Yes, you can join multiple chit funds if you can afford the monthly installments. Many people join 2-3 chit funds with different durations to maximize their returns. However, ensure you can comfortably pay all installments without financial strain. Joining multiple chit funds can provide multiple opportunities to win prize money and earn dividends."""
    },
    {
        "title": "What Happens at the End of Chit Fund?",
        "category": "faq",
        "intent": "knowledge",
        "tags": ["end", "maturity", "completion", "final", "last month"],
        "text": """Question: What happens at the end of the chit fund?
Answer: At the end of the chit fund duration (when all members have won), the last member receives the prize money without any auction. The final month's collection is distributed to the last member. All members would have received their prize money once during the entire duration. The chit fund then concludes, and members can choose to join a new chit fund if they wish."""
    },

    # ── Policies ─────────────────────────────────────────────────
    {
        "title": "Eligibility Criteria",
        "category": "policies",
        "intent": "knowledge",
        "tags": ["eligibility", "criteria", "who can join", "requirements", "qualify"],
        "text": """Eligibility Criteria:
To join a chit fund, you must:
1. Be at least 18 years old
2. Have a valid identity proof (Aadhaar, PAN, Passport)
3. Have a valid address proof
4. Have a bank account
5. Be able to pay the monthly installments regularly
6. Sign the chit fund agreement
Most chit funds accept salaried employees, self-employed individuals, business owners, and housewives. The requirements are minimal compared to traditional financial institutions."""
    },
    {
        "title": "Commission Structure",
        "category": "policies",
        "intent": "knowledge",
        "tags": ["commission", "structure", "foreman", "charges", "fee", "rate"],
        "text": """Commission Structure:
The foreman commission is typically 5% of the gross chit amount. This commission is:
1. Deducted from the bid discount amount before calculating dividend
2. Used by the foreman to manage administrative costs
3. Part of the regulated fee structure under the Chit Funds Act
For example, in a Rs.5,00,000 chit, the foreman commission is Rs.25,000 (5% of Rs.5,00,000). This amount is deducted from the discount before distributing dividend to members."""
    },
    {
        "title": "Chit Terminology",
        "category": "definitions",
        "intent": "knowledge",
        "tags": ["terminology", "terms", "glossary", "definitions"],
        "text": """Chit Terminology:
- Instalment (Monthly Subscription) = Rs.10,000
- Period = Number of months = 50
- Gross Chit Amount = Total of Instalments by all members = Rs.5 lakh (10,000x50)
- Bid Offer Amount = Amount willing to be foregone by subscriber to win Prize Money = Rs.1,75,000 (if Bid = 35%)
- Min Bid Amount = 5% (Foreman Commission)
- Max Bid Amount = 30% (for 30 & 40 months) and 35% (for 50 months)
- Net Amount (Prize Money) = Chit Amount minus Bid-Offer Amount (5,00,000 - 1,75,000 = 3,25,000)
- Foreman Commission (FC) = 5% of Gross Chit Amount (25,000)
- Total Dividend = Bid offer Amount minus Foreman Commission (1,75,000 - 25,000 = 1,50,000)
- Dividend per Customer = Total Dividend/No of Subscribers (1,50,000/50 = 3,000)
- Next Month Instalment = Gross Instalment minus Dividend (10,000 - 3,000 = 7,000)"""
    },
]


def build_vectorstore(pdf_path: str = None, user_id: str = "system", organization_id: str = "default"):
    points = []
    now = datetime.now(timezone.utc).isoformat()

    for i, chunk in enumerate(KNOWLEDGE_BASE):
        dense_embedding = get_embedding(chunk["text"])
        sparse_embedding = get_sparse_embedding(chunk["text"])

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector={
                "text-dense-vector": dense_embedding,
                "text-sparse-vector": sparse_embedding,
            },
            payload={
                "user_id": user_id,
                "organization_id": organization_id,
                "document_id": "chitfunds.pdf",
                "document_name": "chitfunds.pdf",
                "document_type": "text",
                "chunk_number": i,
                "section_title": chunk["title"],
                "category": chunk["category"],
                "intent": chunk["intent"],
                "tags": chunk["tags"],
                "text": chunk["text"],
                "source": "chitfunds.pdf",
                "created_at": now,
            },
        )
        points.append(point)

    upsert_vectors(points)
    return len(points)


if __name__ == "__main__":
    count = build_vectorstore()
    print(f"Indexed {count} intent-based chunks into Qdrant.")
