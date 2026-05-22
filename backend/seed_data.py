"""Initial records written into encrypted stores on first boot."""

AUTOPSIES = [
    {
        "CPR Number": "CPR/2025/CHN/0891",
        "Age": 34,
        "Sex": "M",
        "Height": 172,
        "Weight": 68,
        "Putrefaction": 2,
        "Putre_level": "Early",
        "Algor Mortis": 1,
        "Rigor Mortis": "Partial",
        "Livor Mortis": "Fixed posterior",
        "Stomach Contents": "Rice, vegetables — ~2h pre-mortem",
        "Vitreous Potassium": 8.2,
        "Entomology": "Calliphoridae stage II — 18–24h PMI",
    },
    {
        "CPR Number": "CPR/2025/MDU/0442",
        "Age": 28,
        "Sex": "F",
        "Height": 161,
        "Weight": 55,
        "Putrefaction": 1,
        "Putre_level": "Minimal",
        "Algor Mortis": 0,
        "Rigor Mortis": "Full",
        "Livor Mortis": "Blanching",
        "Stomach Contents": "Empty",
        "Vitreous Potassium": 6.1,
        "Entomology": "No colonization",
    },
    {
        "CPR Number": "CPR/2025/CBE/0310",
        "Age": 45,
        "Sex": "M",
        "Height": 178,
        "Weight": 82,
        "Putrefaction": 3,
        "Putre_level": "Moderate",
        "Algor Mortis": 2,
        "Rigor Mortis": "Passed",
        "Livor Mortis": "Fixed",
        "Stomach Contents": "Alcohol residue",
        "Vitreous Potassium": 11.4,
        "Entomology": "Sarcophagidae stage III",
    },
]

EVIDENCE_INDEX = [
    {
        "document": "CCTV timestamp 20:41 — suspect exits Central Station Gate 4 wearing dark hoodie.",
        "metadata": {"type": "cctv", "confidence": 91, "case_id": "C-2041"},
    },
    {
        "document": "Witness statement: victim seen arguing near platform 3 at approximately 20:15.",
        "metadata": {"type": "witness", "confidence": 72, "case_id": "C-2041"},
    },
    {
        "document": "DNA partial match 99.2% — suspect S-118 on recovered wrench.",
        "metadata": {"type": "forensic", "confidence": 99, "case_id": "C-2041"},
    },
    {
        "document": "Cell tower ping — victim device last active 20:52 near Egmore signal.",
        "metadata": {"type": "digital", "confidence": 85, "case_id": "C-2041"},
    },
    {
        "document": "Autopsy: subarachnoid hemorrhage consistent with blunt occipital impact.",
        "metadata": {"type": "forensic", "confidence": 94, "case_id": "C-2041"},
    },
    {
        "document": "Bank CCTV — four suspects enter Peelamedu branch 14:02.",
        "metadata": {"type": "cctv", "confidence": 88, "case_id": "C-2042"},
    },
]

CASE_TIMELINES = {
    "C-2041": [
        {
            "id": 1,
            "time": "20:15",
            "title": "Witness altercation",
            "eventType": "witness",
            "description": "Argument reported at Platform 3",
            "confidence": 72,
            "severity": "medium",
            "aiInsight": "Corroborates victim presence 35 min before TOD window",
        },
        {
            "id": 2,
            "time": "20:41",
            "title": "Suspect exit CCTV",
            "eventType": "cctv",
            "description": "Gate 4 egress — dark hoodie",
            "confidence": 91,
            "severity": "high",
            "aiInsight": "Matches S-118 clothing description from prior FIR",
        },
        {
            "id": 3,
            "time": "20:52",
            "title": "Last cell ping",
            "eventType": "digital",
            "description": "Victim device near Egmore",
            "confidence": 85,
            "severity": "critical",
            "aiInsight": "Constrains TOD upper bound",
        },
    ],
}

CASE_MOVEMENT = {
    "C-2041": [
        {"lat": 13.0827, "lng": 80.2707, "label": "Central Station", "time": "20:15", "type": "victim"},
        {"lat": 13.0732, "lng": 80.2609, "label": "Platform 3", "time": "20:28", "type": "victim"},
        {"lat": 13.0681, "lng": 80.2551, "label": "Gate 4", "time": "20:41", "type": "suspect"},
        {"lat": 13.0772, "lng": 80.2644, "label": "Egmore signal", "time": "20:52", "type": "victim"},
    ],
}
