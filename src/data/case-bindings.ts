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
  "MG-101": {
    caseId: "MG-101",
    cpr: "CPR/2026/MUM/1201",
    victimName: "A. Deshmukh",
    autopsyReportId: "A-101",
    pathologist: "Dr. S. Patil, CFSL Mumbai",
    reportDate: "10 May 2026 · 08:30",
    pmiDisplay: "6 – 8 Hours",
    pmiNote: "Vitreous potassium + dock recovery time",
    causeOfDeath: "Blunt force trauma — mooring hook strike, cranial impact",
    forensicFindings: [
      "Toolmark match on jacket",
      "Dock CCTV 02:14 assault at Gate 7",
      "Harbor witness timeline 02:05–02:20",
    ],
    liveInsights: [
      "CCTV confirms weapon class — mooring hook",
      "Constable statement aligns with assault window",
    ],
    hasTimeline: true,
    hasMovement: true,
    hasInvestigationGraph: true,
  },
  "MG-102": {
    caseId: "MG-102",
    cpr: "CPR/2026/PUN/0882",
    victimName: "N. Iyer",
    autopsyReportId: "A-102",
    pathologist: "Dr. A. Joshi, AFMC Pune",
    reportDate: "12 May 2026 · 14:00",
    pmiDisplay: "4 – 6 Hours",
    pmiNote: "Indoor lab scene · cyanide ingestion",
    causeOfDeath: "Acute cyanide poisoning",
    forensicFindings: [
      "Potassium cyanide 2.1 mg/L gastric aspirate",
      "Badge P-442 lab access 19:48",
    ],
    liveInsights: ["Digital log ties suspect badge to chemistry wing"],
    hasTimeline: false,
    hasMovement: false,
    hasInvestigationGraph: false,
  },
  "MG-103": {
    caseId: "MG-103",
    cpr: "CPR/2026/GOA/0033",
    victimName: "Unknown male",
    autopsyReportId: "A-103",
    pathologist: "Dr. P. Fernandes, GMC Goa",
    reportDate: "14 May 2026 · 11:20",
    pmiDisplay: "10 – 14 Hours",
    pmiNote: "Beach recovery · saltwater immersion",
    causeOfDeath: "Pending — trauma vs drowning",
    forensicFindings: [
      "Body Baga north tide line 06:30",
      "Fibreglass fragment — possible vessel strike",
    ],
    liveInsights: ["Coast guard notes inconsistent with simple drowning"],
    hasTimeline: false,
    hasMovement: false,
    hasInvestigationGraph: false,
  },
};

export function getCaseBinding(caseId: string): CaseBinding {
  return CASE_BINDINGS[caseId] ?? CASE_BINDINGS["MG-101"];
}

export function bmiLabel(heightCm: number, weightKg: number): string {
  const m = heightCm / 100;
  const bmi = weightKg / (m * m);
  const label =
    bmi < 18.5 ? "Underweight" : bmi < 25 ? "Normal" : bmi < 30 ? "Overweight" : "High";
  return `${bmi.toFixed(1)} (${label})`;
}
