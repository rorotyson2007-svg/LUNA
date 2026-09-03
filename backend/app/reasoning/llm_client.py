
import os
import json
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None

MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# LUNA DATA MODELS
# ============================================================

class Theory(BaseModel):
    id: str
    title: str
    explanation: str = ""
    confidence: str = "LOW"
    score: float = 0.0

    supporting_evidence: List[str] = Field(
        default_factory=list
    )

    contradicting_evidence: List[str] = Field(
        default_factory=list
    )

    assumptions: List[str] = Field(
        default_factory=list
    )


class TheoryResult(BaseModel):
    theories: List[Theory]


class RedTeamResult(BaseModel):
    theory_id: str
    verdict: str

    strengths: List[str] = Field(
        default_factory=list
    )

    unsupported_claims: List[str] = Field(
        default_factory=list
    )

    contradictions: List[str] = Field(
        default_factory=list
    )

    assumptions: List[str] = Field(
        default_factory=list
    )

    alternative_explanations: List[str] = Field(
        default_factory=list
    )

    critical_questions: List[str] = Field(
        default_factory=list
    )

    evidence_gaps: List[str] = Field(
        default_factory=list
    )


# ============================================================
# SAFE JSON EXTRACTION
# ============================================================

def _extract_json(text: str):

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:

        candidate = text[start:end + 1]

        return json.loads(candidate)

    raise ValueError(
        "Gemini did not return valid JSON."
    )


# ============================================================
# GENERIC GEMINI JSON CALL
# ============================================================

def _generate_json(
    system_instruction: str,
    payload: dict,
):

    if client is None:
        raise RuntimeError(
            "Gemini API key is not configured."
        )

    response = client.models.generate_content(

        model=MODEL_NAME,

        contents=json.dumps(
            payload,
            indent=2
        ),

        config={
            "system_instruction":
                system_instruction,

            "temperature": 0.2,

            "response_mime_type":
                "application/json",
        },
    )

    return _extract_json(
        response.text
    )


# ============================================================
# FALLBACK HELPERS
# ============================================================

def _get_evidence_ids(case_data: dict) -> List[str]:

    evidence = case_data.get("evidence", [])

    ids = []

    for index, item in enumerate(evidence):

        if isinstance(item, dict):

            evidence_id = (
                item.get("id")
                or item.get("evidence_id")
                or f"E{index + 1:02d}"
            )

        else:

            evidence_id = f"E{index + 1:02d}"

        ids.append(str(evidence_id))

    return ids


def _fallback_theories(
    case_data: dict
) -> TheoryResult:

    evidence_ids = _get_evidence_ids(case_data)

    gaps = case_data.get("gaps", [])

    supporting = evidence_ids[:2]

    contradicting = evidence_ids[2:3]

    assumptions = [
        "The available evidence is incomplete.",
        "Unobserved activity cannot be ruled out."
    ]

    if not evidence_ids:

        theories = [

            Theory(
                id="T01",
                title="Unmonitored Activity",
                explanation=(
                    "The available dataset does not contain "
                    "sufficient direct evidence to reconstruct "
                    "the complete incident. Activity may have "
                    "occurred outside the captured evidence."
                ),
                confidence="LOW",
                score=0.35,
                supporting_evidence=[],
                contradicting_evidence=[],
                assumptions=assumptions
            ),

            Theory(
                id="T02",
                title="Incomplete Evidence Capture",
                explanation=(
                    "The incident may appear unresolved because "
                    "important observations or events are missing "
                    "from the current evidence set."
                ),
                confidence="LOW",
                score=0.30,
                supporting_evidence=[],
                contradicting_evidence=[],
                assumptions=[
                    "Important evidence may not yet be available."
                ]
            ),

            Theory(
                id="T03",
                title="Alternative Explanation",
                explanation=(
                    "The current information does not establish "
                    "a single explanation. Multiple scenarios "
                    "remain possible until additional evidence "
                    "is obtained."
                ),
                confidence="LOW",
                score=0.25,
                supporting_evidence=[],
                contradicting_evidence=[],
                assumptions=[
                    "Multiple explanations remain compatible "
                    "with the available information."
                ]
            )
        ]

    else:

        theories = [

            Theory(
                id="T01",
                title="Activity Consistent With Available Evidence",
                explanation=(
                    "The currently available observations support "
                    "a possible sequence of events, but the evidence "
                    "is not sufficient to establish the explanation "
                    "as fact."
                ),
                confidence="MEDIUM",
                score=0.65,
                supporting_evidence=supporting,
                contradicting_evidence=contradicting,
                assumptions=assumptions
            ),

            Theory(
                id="T02",
                title="Unobserved Activity",
                explanation=(
                    "Some relevant activity may have occurred outside "
                    "the available observation window or evidence set."
                ),
                confidence="LOW",
                score=0.45,
                supporting_evidence=[],
                contradicting_evidence=[],
                assumptions=[
                    "The available evidence does not cover the "
                    "entire incident."
                ]
            ),

            Theory(
                id="T03",
                title="Alternative Scenario",
                explanation=(
                    "The same observations may be compatible with "
                    "another sequence of events. Additional evidence "
                    "is required to distinguish between competing "
                    "explanations."
                ),
                confidence="LOW",
                score=0.40,
                supporting_evidence=supporting,
                contradicting_evidence=[],
                assumptions=[
                    "Observed events may have more than one "
                    "plausible interpretation."
                ]
            )
        ]

    return TheoryResult(
        theories=theories
    )


def _fallback_red_team(
    case_data: dict
) -> RedTeamResult:

    gaps = case_data.get("gaps", [])

    evidence_ids = _get_evidence_ids(case_data)

    return RedTeamResult(

        theory_id="T01",

        verdict="PLAUSIBLE",

        strengths=[
            "The theory is consistent with the currently "
            "available evidence.",
            "The theory explicitly acknowledges uncertainty."
        ],

        unsupported_claims=[
            "The available evidence does not establish intent.",
            "The available evidence does not establish identity."
        ],

        contradictions=[],

        assumptions=[
            "The current evidence set is incomplete."
        ],

        alternative_explanations=[
            "The observed events may have another explanation.",
            "Relevant activity may have occurred outside "
            "the observation window."
        ],

        critical_questions=[
            "What evidence exists immediately before and after "
            "the observed events?",
            "Are there additional cameras, witnesses, or records?",
            "Can the current timeline be independently verified?"
        ],

        evidence_gaps=[
            str(g)
            for g in gaps
        ] or [
            "Additional corroborating evidence is required."
        ]
    )


# ============================================================
# CASE THEORY ENGINE
# ============================================================

THEORY_SYSTEM_PROMPT = """
You are LUNA's Case Theory Engine.

LUNA is a privacy-first investigative reasoning system.

Your task is NOT to identify a real person.

All people must remain anonymous identifiers such as
Person #A17, Person #B04, Person #C09.

Your task is to reconstruct what may have happened.

Generate 2 to 4 COMPETING theories.

A theory must:

1. Explain the available evidence.
2. Reference specific evidence IDs.
3. Include supporting evidence.
4. Include contradicting evidence.
5. Explicitly state assumptions.
6. Avoid treating assumptions as facts.
7. Consider alternative explanations.
8. Assign a confidence level.
9. Assign a numerical score from 0.0 to 1.0.

Important:

A high score does NOT mean guilt.

It only means the theory currently explains the
available evidence better than competing explanations.

Return ONLY valid JSON.
"""


def generate_theories(
    case_data: dict
) -> TheoryResult:

    try:

        result = _generate_json(
            THEORY_SYSTEM_PROMPT,
            case_data
        )

        return TheoryResult.model_validate(
            result
        )

    except Exception as error:

        print(
            f"[LUNA] Gemini theory engine unavailable: "
            f"{type(error).__name__}: {error}"
        )

        print(
            "[LUNA] Using deterministic fallback reasoning."
        )

        return _fallback_theories(
            case_data
        )


# ============================================================
# RED TEAM
# ============================================================

RED_TEAM_SYSTEM_PROMPT = """
You are LUNA's Red Team / Devil's Advocate engine.

Your job is to attack the leading investigation theory.

DO NOT attempt to prove the theory.

Attempt to BREAK it.

You must distinguish carefully between:

SUPPORTED FACT
UNSUPPORTED CLAIM
ASSUMPTION
CONTRADICTION
EVIDENCE GAP

A missing piece of evidence is NOT automatically a contradiction.

A contradiction exists only when available evidence
actually conflicts with the theory.

Ask:

1. What does the evidence actually establish?
2. What is merely inferred?
3. Which claims have no direct support?
4. What assumptions are required?
5. Does any evidence contradict the theory?
6. Could another explanation fit the same evidence?
7. What evidence is missing?
8. What critical question remains unanswered?

People must remain anonymous.

Never identify a real person.

Return ONLY valid JSON.
"""


def run_red_team(
    case_data: dict
) -> RedTeamResult:

    try:

        result = _generate_json(
            RED_TEAM_SYSTEM_PROMPT,
            case_data
        )

        return RedTeamResult.model_validate(
            result
        )

    except Exception as error:

        print(
            f"[LUNA] Gemini red-team engine unavailable: "
            f"{type(error).__name__}: {error}"
        )

        print(
            "[LUNA] Using deterministic fallback red-team reasoning."
        )

        return _fallback_red_team(
            case_data
        )
