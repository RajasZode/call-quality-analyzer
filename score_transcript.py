# score_transcript.py

scoring_criteria = {
    "Call Opening": [
        {
            "description": "Agent greeted with full name, company name, and purpose",
            "keywords": ["this is", "my name is", "calling from", "insurance", "purpose of call", "bajaj", "welcome call"],
            "weight": 5,
            "critical": True
        },
        {
            "description": "Informed that this is a recorded call for quality/training",
            "keywords": ["this call is recorded", "quality", "training", "future reference", "recorded line", "record ho rahi hai"],
            "weight": 2,
            "critical": True
        }
    ],

    "Customer Information Gathering": [
        {
            "description": "Asked about members covered, DOB, family members, city, height, weight, nominee, email, alternate contact, address",
            "keywords": ["how many members", "dob", "date of birth", "family members", "spouse", "city", "height", "weight", "nominee", "email", "alternate number", "address", "kitne member", "janm", "pati", "bachche", "sheher", "vajan", "imeel", "dusra number", "ghar ka pata"],
            "weight": 5,
            "critical": True
        },
        {
            "description": "Asked PD/underwriting questions",
            "keywords": ["any medical condition", "underwriting", "health questions", "diabetes", "bp", "surgery", "asthma", "swastya", "bimari"],
            "weight": 5,
            "critical": True
        },
        {
            "description": "Portability case info: previous insurer, expiry date, claim history",
            "keywords": ["previous insurance", "old policy", "expiry date", "claim history", "purani policy", "samapti tithi", "daava"],
            "weight": 3,
            "critical": True
        }
    ],

    "Sales Pitch": [
        {
            "description": "Plan offered, premium, sum insured, policy year, tax benefit",
            "keywords": ["plan", "premium", "sum insured", "policy year", "tax benefit", "yojana", "labh"],
            "weight": 3,
            "critical": True
        },
        {
            "description": "Coverages and exclusions explained",
            "keywords": ["coverage", "exclusion", "waiting period", "pre-existing", "kya cover hai"],
            "weight": 5,
            "critical": True
        },
        {
            "description": "Claim process explained",
            "keywords": ["claim process", "cashless", "reimbursement", "co-payment", "daava prakriya"],
            "weight": 3,
            "critical": True
        },
        {
            "description": "No false commitment or mis-selling",
            "keywords": ["honest", "truth", "no false", "accurate", "jhooth nahi", "galat"],
            "weight": 10,
            "critical": True
        },
        {
            "description": "Objection handling, probing, plan USP, EMI/riders discussed",
            "keywords": ["objection", "not interested", "emi", "rider", "health prime", "respect rider", "benefit", "usps"],
            "weight": 20,
            "critical": True
        },
        {
            "description": "Used power statement to convert customer",
            "keywords": ["money", "trust", "reason for not interested", "time issue", "problem", "concern", "issue"],
            "weight": 10,
            "critical": True
        }
    ],

    "Communication Skill": [
        {
            "description": "Courtesy & personalization (golden words, name used 2x, rapport)",
            "keywords": ["thank you", "appreciate", "your name", "mr.", "mrs.", "miss", "sir", "ma'am"],
            "weight": 3,
            "critical": False
        },
        {
            "description": "Fluent speech, right speed, confident tone, no fumbling",
            "keywords": ["clear", "slow down", "voice modulation", "tone", "confidence", "energy", "clarity"],
            "weight": 3,
            "critical": False
        },
        {
            "description": "Engaged customer (2-way communication, active listening)",
            "keywords": ["any questions", "do you have", "kya samjha", "aap bataye", "sun raha hoon"],
            "weight": 2,
            "critical": False
        },
        {
            "description": "Empathy & acknowledgement",
            "keywords": ["i understand", "i'm sorry", "i hear you", "samajhta hoon"],
            "weight": 1,
            "critical": False
        },
        {
            "description": "Hold/unhold procedure followed",
            "keywords": ["may I place", "thank you for holding", "on hold", "dhanyavaad hold"],
            "weight": 2,
            "critical": False
        },
        {
            "description": "No rudeness, no abuse, no argument",
            "keywords": ["sorry", "no argument", "abuse", "shouting", "badtameezi", "jagda"],
            "weight": 3,
            "critical": True
        }
    ],

    "Call Closing": [
        {
            "description": "Follow-up date & time confirmed",
            "keywords": ["follow up", "next call", "call back", "schedule", "phir baat"],
            "weight": 5,
            "critical": True
        },
        {
            "description": "Cross-sell, referral if sales closed",
            "keywords": ["any other", "refer", "family member", "aur plan"],
            "weight": 4,
            "critical": True
        },
        {
            "description": "Disposition tagging done correctly",
            "keywords": ["disposition", "call status", "updated as"],
            "weight": 3,
            "critical": True
        },
        {
            "description": "Proper closing declaration",
            "keywords": ["thank you for your time", "have a nice day", "we are disconnecting", "closing the call", "disconnect"],
            "weight": 5,
            "critical": True
        }
    ]
}

# Scoring logic

def score_transcript(transcript, criteria):
    transcript_lower = transcript.lower()
    scored_output = {}

    for section, items in criteria.items():
        score = 0
        max_score = sum(item["weight"] for item in items)
        missed = []

        for item in items:
            matched = any(keyword.lower() in transcript_lower for keyword in item["keywords"])
            if matched:
                score += item["weight"]
            else:
                missed.append(item["description"])

        scored_output[section] = {
            "score": score,
            "max_score": max_score,
            "missed": missed
        }

    return scored_output
