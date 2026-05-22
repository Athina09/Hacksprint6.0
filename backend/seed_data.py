"""Initial records written into encrypted stores on first boot."""

# Bump when you change cases — forces re-write of .enc files on API start.
SEED_VERSION = "mg-v1"

# Cases used in RAG eval + Streamlit accuracy chart (edit here).
EVAL_CASES = {
    "MG-101": {"label": "Mumbai Harbor Assault", "chart": "Mumbai Harbor", "district": "Mumbai"},
    "MG-102": {"label": "Pune Lab Poisoning", "chart": "Pune Lab", "district": "Pune"},
    "MG-103": {"label": "Goa Beach Recovery", "chart": "Goa Beach", "district": "Goa"},
}

AUTOPSIES = [
    {
        "case_id": "MG-101",
        "victim_name": "A. Deshmukh",
        "CPR Number": "CPR/2026/MUM/1201",
        "Age": 31,
        "Sex": "M",
        "Height": 172,
        "Weight": 68,
        "Putrefaction": 1,
        "Putre_level": "Early",
        "Algor Mortis": 1,
        "Rigor Mortis": "Partial",
        "Livor Mortis": "Fixed dorsal",
        "Stomach Contents": "Fish curry — ~3h pre-mortem",
        "Vitreous Potassium": 7.4,
        "Entomology": "Minimal blowfly activity — 6–8h PMI",
    },
    {
        "case_id": "MG-102",
        "victim_name": "N. Iyer",
        "CPR Number": "CPR/2026/PUN/0882",
        "Age": 26,
        "Sex": "F",
        "Height": 158,
        "Weight": 52,
        "Putrefaction": 0,
        "Putre_level": "None",
        "Algor Mortis": 0,
        "Rigor Mortis": "Absent",
        "Livor Mortis": "Not fixed",
        "Stomach Contents": "Coffee, biscuit crumbs",
        "Vitreous Potassium": 5.2,
        "Entomology": "Not applicable — indoor scene",
    },
    {
        "case_id": "MG-103",
        "victim_name": "Unknown male",
        "CPR Number": "CPR/2026/GOA/0033",
        "Age": 40,
        "Sex": "M",
        "Height": 180,
        "Weight": 76,
        "Putrefaction": 2,
        "Putre_level": "Early–moderate",
        "Algor Mortis": 1,
        "Rigor Mortis": "Full",
        "Livor Mortis": "Blanching",
        "Stomach Contents": "Empty",
        "Vitreous Potassium": 9.8,
        "Entomology": "Saltwater immersion artifacts",
    },
]

EVIDENCE_INDEX = [
    {
        "document": "Dock CCTV 02:14 — victim struck with mooring hook near Gate 7 loading bay.",
        "metadata": {"type": "cctv", "confidence": 89, "case_id": "MG-101"},
    },
    {
        "document": "Harbor constable statement: argument heard at 02:05, victim found bleeding at 02:20.",
        "metadata": {"type": "witness", "confidence": 74, "case_id": "MG-101"},
    },
    {
        "document": "Toolmark analysis: hook matches blood pattern on victim Deshmukh jacket.",
        "metadata": {"type": "forensic", "confidence": 91, "case_id": "MG-101"},
    },
    {
        "document": "Lab access log — suspect badge P-442 swiped into chemistry wing 19:48.",
        "metadata": {"type": "digital", "confidence": 86, "case_id": "MG-102"},
    },
    {
        "document": "Toxicology: potassium cyanide 2.1 mg/L in gastric aspirate — victim Iyer.",
        "metadata": {"type": "forensic", "confidence": 97, "case_id": "MG-102"},
    },
    {
        "document": "Beach patrol report: body at Baga north end, tide line 06:30, wallet absent.",
        "metadata": {"type": "scene", "confidence": 80, "case_id": "MG-103"},
    },
    {
        "document": "Coast guard note: fibreglass fragment on shoulder — possible boat strike.",
        "metadata": {"type": "forensic", "confidence": 72, "case_id": "MG-103"},
    },
]

CASE_TIMELINES = {
    "MG-101": [
        {
            "id": 1,
            "time": "02:05",
            "title": "Argument reported",
            "eventType": "witness",
            "description": "Loading bay Gate 7",
            "confidence": 74,
            "severity": "medium",
            "aiInsight": "Sets lower TOD bound",
        },
        {
            "id": 2,
            "time": "02:14",
            "title": "CCTV assault",
            "eventType": "cctv",
            "description": "Mooring hook strike",
            "confidence": 89,
            "severity": "critical",
            "aiInsight": "Weapon visible on footage",
        },
    ],
}

EVIDENCE_EVAL_QUERIES = [
    {"id": "ev1", "case_id": "MG-101", "query": "mooring hook CCTV", "must_match": ["hook", "CCTV"]},
    {"id": "ev2", "case_id": "MG-101", "query": "harbor constable argument", "must_match": ["constable", "02:05"]},
    {"id": "ev3", "case_id": "MG-101", "query": "toolmark Deshmukh jacket", "must_match": ["toolmark", "Deshmukh"]},
    {"id": "ev4", "case_id": "MG-102", "query": "cyanide gastric Iyer", "must_match": ["cyanide", "Iyer"]},
    {"id": "ev5", "case_id": "MG-102", "query": "badge chemistry wing", "must_match": ["badge", "chemistry"]},
    {"id": "ev6", "case_id": "MG-103", "query": "Baga beach patrol tide", "must_match": ["Baga", "tide"]},
    {"id": "ev7", "case_id": "MG-103", "query": "fibreglass boat strike", "must_match": ["fibreglass", "boat"]},
]

TIMELINE_EVAL_QUERIES = [
    {"id": "tl1", "case_id": "MG-101", "query": "argument Gate 7", "must_match": ["Argument", "Gate"]},
    {"id": "tl2", "case_id": "MG-101", "query": "CCTV mooring hook", "must_match": ["CCTV", "hook"]},
]

CASE_MOVEMENT = {
    "MG-101": [
        {"lat": 18.9400, "lng": 72.8350, "label": "Gate 7 loading bay", "time": "02:05", "type": "victim"},
        {"lat": 18.9385, "lng": 72.8340, "label": "Mooring hook strike CCTV", "time": "02:14", "type": "suspect"},
    ],
}

RETRIEVAL_EVAL: list[dict] = [
    {"domain": "evidence", "case_id": "MG-101", "query": "mooring hook dock CCTV", "must_match": ["hook", "cctv"]},
    {"domain": "evidence", "case_id": "MG-102", "query": "cyanide toxicology Iyer", "must_match": ["cyanide", "iyer"]},
    {"domain": "evidence", "case_id": "MG-103", "query": "Baga beach body tide", "must_match": ["baga", "tide"]},
    {"domain": "timeline", "case_id": "MG-101", "query": "CCTV assault mooring", "must_match": ["cctv", "hook"]},
    {"domain": "autopsy", "case_id": "MG-101", "query": "vitreous potassium 7.4", "must_match": ["vitreous", "7.4"]},
    {"domain": "autopsy", "case_id": "MG-102", "query": "vitreous 5.2 cyanide scene", "must_match": ["vitreous", "5.2"]},
    {"domain": "movement", "case_id": "MG-101", "query": "Gate 7 loading bay", "must_match": ["gate", "loading"]},
]
