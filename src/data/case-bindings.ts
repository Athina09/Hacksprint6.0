/** Links UI case IDs to encrypted backend records and demo copy. */

export interface CaseBinding {
  caseId: string;
  cpr: string;
  victimName: string;
  autopsyReportId: string;
  pathologist: string;
  reportDate: string;
  pmiDisplay: string;
  pmiNote: string;
  causeOfDeath: string;
  forensicFindings: string[];
  liveInsights: string[];
  hasTimeline: boolean;
  hasMovement: boolean;
  hasInvestigationGraph: boolean;
}

export const CASE_BINDINGS: Record<string, CaseBinding> = {
  "C-2041": {
    caseId: "C-2041",
    cpr: "CPR/2025/CHN/0891",
    victimName: "R. Suresh",
    autopsyReportId: "A-2041",
    pathologist: "Dr. K. Meenakshi, CFSL Chennai",
    reportDate: "26 Apr 2025 · 23:47",
    pmiDisplay: "8 – 10 Hours",
    pmiNote: "Vitreous potassium + algor mortis",
    causeOfDeath:
      "Blunt force trauma — occipital region with depressed skull fracture and subdural hemorrhage. Secondary: hepatic hemorrhage.",
    forensicFindings: [
      "3 patterned blunt impacts — iron rod (87 cm)",
      "Hemoperitoneum ~1,200 ml confirmed",
      "Post-mortem relocation via livor mortis",
      "Trace diazepam — pre-assault sedation",
      "DNA match S-118 at 99.2% on weapon",
      "Defensive wounds: victim conscious at onset",
    ],
    liveInsights: [
      "Brain hemorrhage detected — primary cause of death confirmed",
      "Liver trauma indicates blunt force abdominal impact",
      "Hemoperitoneum ~1,200 ml — internal bleeding active at time of recovery",
      "Defensive wounds on left arm confirm victim was conscious during assault",
      "Diazepam trace suggests pre-assault chemical sedation",
      "Post-mortem body relocation confirmed via livor mortis analysis",
      "Cell tower + physical evidence converge: TOD window 20:15–20:55",
      "Suspect S-118 DNA match at 99.2% on recovered weapon",
    ],
    hasTimeline: true,
    hasMovement: true,
    hasInvestigationGraph: true,
  },
  "C-2042": {
    caseId: "C-2042",
    cpr: "CPR/2025/CBE/0310",
    victimName: "—",
    autopsyReportId: "A-2042",
    pathologist: "Dr. P. Lakshmi, CFSL Coimbatore",
    reportDate: "29 Apr 2025 · 16:20",
    pmiDisplay: "—",
    pmiNote: "Robbery case — no victim autopsy",
    causeOfDeath: "N/A — bank heist investigation",
    forensicFindings: ["Bank CCTV: four suspects at Peelamedu branch 14:02"],
    liveInsights: ["Evidence index: CCTV-led robbery reconstruction"],
    hasTimeline: false,
    hasMovement: false,
    hasInvestigationGraph: false,
  },
  "C-2043": {
    caseId: "C-2043",
    cpr: "CPR/2025/MDU/0442",
    victimName: "Pending ID",
    autopsyReportId: "A-2043",
    pathologist: "Dr. K. Mohan, GH Madurai",
    reportDate: "01 May 2025 · 09:15",
    pmiDisplay: "12 – 18 Hours",
    pmiNote: "River recovery · moderate putrefaction",
    causeOfDeath: "Suspicious death — pending full histopathology",
    forensicFindings: [
      "Body recovered Vaigai river bank",
      "Sarcophagidae stage III — extended PMI",
      "Relocation hypothesis under review",
    ],
    liveInsights: ["Hypothesis: body relocation likely (livor vs recovery position)"],
    hasTimeline: false,
    hasMovement: false,
    hasInvestigationGraph: false,
  },
};

export function getCaseBinding(caseId: string): CaseBinding {
  return CASE_BINDINGS[caseId] ?? CASE_BINDINGS["C-2041"];
}

export function bmiLabel(heightCm: number, weightKg: number): string {
  const m = heightCm / 100;
  const bmi = weightKg / (m * m);
  const label =
    bmi < 18.5 ? "Underweight" : bmi < 25 ? "Normal" : bmi < 30 ? "Overweight" : "High";
  return `${bmi.toFixed(1)} — ${label}`;
}
