scoring_criteria = {
    "Call Opening": [
        {
            "description": "Greeting must start with Good Morning / Afternoon / Evening (not Hi/Hello)",
            "keywords": ["Good morning", "good afternoon", "good evening"],
            "weight": 1,
            "critical": True,
            "must_start": True,
            "negative_keywords": ["hi", "hello"]
        },
        {
            "description": "Agent to mention his/her name and company name",
            "keywords": ["my name is", "this is", "calling from", "bajaj", "insurance"],
            "weight": 1,
            "critical": True
        },
        {
            "description": "Agent to ask for customer's name",
            "keywords": ["your name", "may I know your name", "confirm your name", "Am I talking to", "Am I speaking with"],
            "weight": 1,
            "critical": False
        },
        {
            "description": "Agent to explain the purpose of the call",
            "keywords": ["purpose of call", "regarding", "calling you for", "welcome call", "insurance", "health", "policy"],
            "weight": 1,
            "critical": True
        },
        {
            "description": "Inform about call recording & took language confirmation at beginning",
            "keywords": ["this call is recorded", "for quality", "for training", "recorded line", "record ho rahi hai", "language", "english", "hindi"],
            "weight": 1,
            "critical": True,
            "must_be_in_opening": True
        }
    ],

    "Information Gathering": [
        {
            "description": "Ask about members covered, DOB, family members, city, height, weight, nominee, email, alternate contact, address",
            "keywords": ["how many members", "dob", "date of birth", "family members", "spouse", "city", "height", "weight", "nominee", "email", "alternate number", "address", "kitne member", "janm", "pati", "bachche", "sheher", "vajan", "imeel", "dusra number", "ghar ka pata"],
            "weight": 5,
            "critical": True
        },
        {
            "description": "Agent to ask PED/Underwriting questions",
            "keywords": [
                "pre existing disease", "diabetes", "high blood pressure", "bp",
                "thyroid", "medical condition", "consume cigarette", "alcohol",
                "smoke", "drink", "critical illness", "hospitalized",
                "hospitalization", "accident", "surgery", "asthma"
            ],
            "weight": 5,
            "critical": True,
            "scoring_type": "per_keyword",
            "max_score": 5,
            "min_required": 3
        },
        {
            "description": "Portability case info: previous insurer, expiry date, claim history",
            "keywords": ["previous insurance", "old policy", "expiry date", "claim history", "purani policy", "samapti tithi", "daava"],
            "weight": 3,
            "critical": True,
            "condition_keywords": ["i want to port", "port my policy", "switch policy", "transfer policy", "portability"]
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

def score_transcript(transcript_input, criteria=scoring_criteria):
    if isinstance(transcript_input, str):
        transcript_text = transcript_input.lower()
    else:
        transcript_text = " ".join([
            segment['text'].lower()
            for segment in transcript_input
            if segment.get('speaker', '').upper() in ["SPEAKER_01", "UNKNOWN"]
        ])

    results = {}

    for section, criteria_list in criteria.items():
        section_score = 0
        section_total = 0
        missed = []
        achieved = []
        evaluated_count = 0

        for c in criteria_list:
            score = 0
            if "condition_keywords" in c and not any(k in transcript_text for k in c["condition_keywords"]):
                continue

            section_total += c['weight']
            evaluated_count += 1

            if c.get("scoring_type") == "per_keyword":
                matched_keywords = set()
                for kw in c["keywords"]:
                    if kw in transcript_text:
                        matched_keywords.add(kw)
                score = min(len(matched_keywords), c.get("max_score", c["weight"]))
                if len(matched_keywords) < c.get("min_required", 1):
                    score = 0
                if score == 0:
                    missed.append(f"{c['description']} (0/{c['weight']})")
                else:
                    achieved.append(f"{c['description']} ({score}/{c['weight']})")

            elif c.get("must_start"):
                first_sentence = ""
                if isinstance(transcript_input, list):
                    for line in transcript_input:
                        if line.get("speaker", "").upper() in ["SPEAKER_01", "UNKNOWN"]:
                            first_sentence = line.get("text", "").lower()
                            break
                first_20_words = " ".join(first_sentence.split()[:20])
                if any(kw.lower() in first_20_words for kw in c["keywords"]) and not any(bad.lower() in first_20_words for bad in c.get("negative_keywords", [])):
                    score = c["weight"]
                    achieved.append(f"{c['description']} ({score}/{c['weight']})")
                else:
                    missed.append(f"{c['description']} (0/{c['weight']})")

            elif c.get("must_be_in_opening"):
                first_50_words = " ".join(transcript_text.split()[:50])
                if any(kw in first_50_words for kw in c["keywords"]):
                    score = c["weight"]
                    achieved.append(f"{c['description']} ({score}/{c['weight']})")
                else:
                    missed.append(f"{c['description']} (0/{c['weight']})")

            else:
                if any(kw in transcript_text for kw in c["keywords"]):
                    score = c["weight"]
                    achieved.append(f"{c['description']} ({score}/{c['weight']})")
                else:
                    missed.append(f"{c['description']} (0/{c['weight']})")

            section_score += score

        percent = round((section_score / section_total) * 100, 1) if section_total > 0 else 0
        results[section] = {
            "score": section_score,
            "total": section_total,
            "percent": percent,
            "missed": missed,
            "missed_count": len(missed),
            "achieved_count": evaluated_count - len(missed),
            "achieved": achieved
        }

    return results
