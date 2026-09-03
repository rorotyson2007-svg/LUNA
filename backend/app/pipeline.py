import json
import re
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv

from app.models.evidence import *
from app.models.theory import *


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(maximum, safe_float(value, minimum)))


def as_list(value):
    return value if isinstance(value, list) else []


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):

    if not text:
        return None

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        candidate = text[start:end + 1]

        try:
            return json.loads(candidate)
        except Exception:
            pass

    return None


# ============================================================
# TIMELINE FALLBACK
# ============================================================

def build_timeline_from_text(text):

    if not text:
        return []

    events = []

    time_pattern = re.compile(
        r"\b(?:[01]?\d|2[0-3])[:.][0-5]\d"
        r"(?:\s?(?:AM|PM))?\b",
        re.IGNORECASE,
    )

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        match = time_pattern.search(sentence)

        timestamp = (
            match.group(0)
            if match
            else "UNKNOWN"
        )

        events.append({
            "id": f"EVENT-{len(events) + 1:03d}",
            "timestamp": timestamp,
            "event": sentence,
            "source": "CASE-TEXT",
            "confidence": (
                0.75
                if timestamp != "UNKNOWN"
                else 0.5
            ),
        })

    return events


# ============================================================
# TIMELINE FROM EVIDENCE
# ============================================================

def build_timeline_from_evidence(evidence):

    timeline = []

    for item in evidence or []:

        if not isinstance(item, dict):
            continue

        text = (
            item.get("event")
            or item.get("description")
            or item.get("text")
            or item.get("content")
            or item.get("summary")
        )

        if not text:
            continue

        timestamp = (
            item.get("timestamp")
            or item.get("time")
            or "UNKNOWN"
        )

        timeline.append({
            "id": f"EVENT-{len(timeline) + 1:03d}",
            "timestamp": timestamp,
            "event": str(text),
            "source": (
                item.get("id")
                or item.get("source")
                or "UNKNOWN"
            ),
            "confidence": clamp(
                item.get("confidence", 0.5),
                0,
                1,
            ),
        })

    return timeline


# ============================================================
# TIMELINE NORMALIZATION
# ============================================================

def normalize_timeline(timeline):

    if not isinstance(timeline, list):
        return []

    normalized = []

    for index, item in enumerate(
        timeline,
        start=1,
    ):

        if isinstance(item, str):

            normalized.append({
                "id": f"EVENT-{index:03d}",
                "timestamp": "UNKNOWN",
                "event": item,
                "source": "LUNA",
                "confidence": 0.5,
            })

            continue

        if not isinstance(item, dict):
            continue

        normalized.append({
            "id": (
                item.get("id")
                or f"EVENT-{index:03d}"
            ),

            "timestamp": (
                item.get("timestamp")
                or item.get("time")
                or item.get("date")
                or "UNKNOWN"
            ),

            "event": (
                item.get("event")
                or item.get("description")
                or item.get("text")
                or item.get("summary")
                or "Unspecified event"
            ),

            "source": (
                item.get("source")
                or item.get("evidence_id")
                or "UNKNOWN"
            ),

            "confidence": clamp(
                item.get("confidence", 0.5),
                0,
                1,
            ),
        })

    return normalized


# ============================================================
# EVIDENCE NORMALIZATION
# ============================================================

def normalize_evidence(evidence):

    normalized = []

    for index, item in enumerate(
        evidence or [],
        start=1,
    ):

        if isinstance(item, str):

            normalized.append({
                "id": f"EV-{index:03d}",
                "type": "CASE MATERIAL",
                "source": "CASE-TEXT",
                "description": item,
                "quality": 0.5,
                "reliability": 0.5,
                "directness": 0.5,
            })

            continue

        if not isinstance(item, dict):
            continue

        normalized.append({

            "id": (
                item.get("id")
                or f"EV-{index:03d}"
            ),

            "type": (
                item.get("type")
                or "UNKNOWN"
            ),

            "source": (
                item.get("source")
                or "CASE-TEXT"
            ),

            "description": (
                item.get("description")
                or item.get("text")
                or item.get("content")
                or item.get("summary")
                or ""
            ),

            "quality": clamp(
                item.get("quality", 0.5)
            ),

            "reliability": clamp(
                item.get("reliability", 0.5)
            ),

            "directness": clamp(
                item.get("directness", 0.5)
            ),
        })

    return normalized


# ============================================================
# THEORY NORMALIZATION
# ============================================================

def normalize_theories(theories):

    normalized = []

    for index, theory in enumerate(
        theories or [],
        start=1,
    ):

        if not isinstance(theory, dict):
            continue

        normalized.append({

            "id": (
                theory.get("id")
                or f"T-{index:03d}"
            ),

            "title": (
                theory.get("title")
                or f"Investigation Theory {index}"
            ),

            "explanation": (
                theory.get("explanation")
                or ""
            ),

            "supporting_evidence": as_list(
                theory.get("supporting_evidence")
            ),

            "contradicting_evidence": as_list(
                theory.get("contradicting_evidence")
            ),

            "assumptions": as_list(
                theory.get("assumptions")
            ),

            "score": clamp(
                theory.get("score", 0.0)
            ),

            "confidence": (
                theory.get("confidence")
                or "low"
            ),
        })

    return normalized


# ============================================================
# RED TEAM NORMALIZATION
# ============================================================

def normalize_red_team(red_team):

    if isinstance(red_team, list):
        return red_team

    if isinstance(red_team, dict):
        return [red_team]

    return []


# ============================================================
# EVIDENCE DNA
# ============================================================

def build_evidence_dna(evidence):

    dna = []

    for item in evidence:

        if not isinstance(item, dict):
            continue

        quality = clamp(
            item.get("quality", 0.5)
        )

        reliability = clamp(
            item.get("reliability", 0.5)
        )

        directness = clamp(
            item.get("directness", 0.5)
        )

        strength = (
            quality
            + reliability
            + directness
        ) / 3

        dna.append({

            "evidence_id":
                item.get("id", "UNKNOWN"),

            "type":
                item.get("type", "UNKNOWN"),

            "source":
                item.get("source", "UNKNOWN"),

            "quality":
                quality,

            "reliability":
                reliability,

            "directness":
                directness,

            "strength":
                round(strength, 3),

            "classification":
                (
                    "HIGH"
                    if strength >= 0.75
                    else
                    "MEDIUM"
                    if strength >= 0.5
                    else
                    "LOW"
                ),
        })

    return dna


# ============================================================
# EVIDENCE DEPENDENCIES
# ============================================================

def build_evidence_dependencies(
    evidence,
    theories,
):

    dependencies = []

    for theory in theories:

        if not isinstance(theory, dict):
            continue

        theory_id = theory.get(
            "id",
            "UNKNOWN",
        )

        supporting = theory.get(
            "supporting_evidence",
            [],
        )

        for evidence_id in supporting:

            dependencies.append({

                "theory_id":
                    theory_id,

                "evidence_id":
                    evidence_id,

                "relationship":
                    "SUPPORTS",

                "dependency_strength":
                    0.7,
            })

    return dependencies


# ============================================================
# THEORY COLLISION
# ============================================================

def build_theory_collisions(theories):

    collisions = []

    for i in range(len(theories)):

        for j in range(i + 1, len(theories)):

            a = theories[i]
            b = theories[j]

            if not isinstance(a, dict):
                continue

            if not isinstance(b, dict):
                continue

            collisions.append({

                "theory_a":
                    a.get("id"),

                "theory_b":
                    b.get("id"),

                "conflict":
                    (
                        f"{a.get('title', 'Theory A')} "
                        f"and "
                        f"{b.get('title', 'Theory B')} "
                        "represent competing explanations."
                    ),

                "winner":
                    (
                        a.get("id")
                        if safe_float(
                            a.get("score")
                        )
                        >
                        safe_float(
                            b.get("score")
                        )
                        else b.get("id")
                    ),
            })

    return collisions


# ============================================================
# COUNTERFACTUAL ENGINE
# ============================================================

def build_counterfactuals(theories):

    counterfactuals = []

    for theory in theories:

        if not isinstance(theory, dict):
            continue

        theory_id = theory.get(
            "id",
            "UNKNOWN",
        )

        title = theory.get(
            "title",
            "Unknown theory",
        )

        supporting = theory.get(
            "supporting_evidence",
            [],
        )

        counterfactuals.append({

            "theory_id":
                theory_id,

            "question":
                f"If {title} were false, what evidence should we expect to see?",

            "expected_observation":
                "At least one independent evidence source should contradict the theory.",

            "current_signal":
                (
                    f"{len(supporting)} supporting evidence "
                    "references identified."
                ),

            "status":
                "TEST_REQUIRED",
        })

    return counterfactuals


# ============================================================
# UNKNOWN EVENT DETECTION
# ============================================================

def build_unknown_events(
    timeline,
    contradictions,
):

    unknown_events = []

    for event in timeline:

        if not isinstance(event, dict):
            continue

        if (
            event.get("timestamp") == "UNKNOWN"
            or safe_float(
                event.get("confidence", 0)
            ) < 0.5
        ):

            unknown_events.append({

                "event_id":
                    event.get("id"),

                "reason":
                    "Event has temporal or confidence uncertainty.",

                "severity":
                    "MEDIUM",
            })

    for contradiction in contradictions:

        if isinstance(contradiction, str):

            unknown_events.append({

                "event_id":
                    "UNKNOWN",

                "reason":
                    contradiction,

                "severity":
                    "HIGH",
            })

    return unknown_events


# ============================================================
# BLIND-SPOT MAPPER
# ============================================================

def build_blind_spots(
    case_text,
    evidence,
):

    text = (case_text or "").lower()

    blind_spots = []

    keywords = [
        "blind spot",
        "blindspot",
        "not visible",
        "out of view",
        "outside camera",
        "camera coverage",
        "obstructed",
        "obstruction",
        "blocked view",
        "unknown location",
    ]

    for keyword in keywords:

        if keyword in text:

            blind_spots.append({

                "type":
                    "VISIBILITY_GAP",

                "description":
                    (
                        f"Case material references "
                        f"'{keyword}'."
                    ),

                "severity":
                    "HIGH",

                "recommended_action":
                    "Review adjacent camera coverage or independent evidence.",
            })

    if not blind_spots:

        blind_spots.append({

            "type":
                "UNASSESSED",

            "description":
                "No explicit camera blind spot was established from the supplied material.",

            "severity":
                "LOW",

            "recommended_action":
                "Verify camera coverage around critical events.",
        })

    return blind_spots


# ============================================================
# INCIDENT REPLAY
# ============================================================

def build_incident_replay(timeline):

    frames = []

    for index, event in enumerate(
        timeline,
        start=1,
    ):

        if not isinstance(event, dict):
            continue

        frames.append({

            "frame":
                index,

            "event_id":
                event.get("id"),

            "timestamp":
                event.get("timestamp"),

            "description":
                event.get("event"),

            "confidence":
                event.get("confidence", 0.5),
        })

    return {

        "type":
            "TIMELINE_REPLAY",

        "frame_count":
            len(frames),

        "frames":
            frames,
    }


# ============================================================
# CONFIDENCE ENGINE
# ============================================================

def build_confidence(
    evidence,
    theories,
    timeline,
):

    evidence_scores = []

    for item in evidence:

        if not isinstance(item, dict):
            continue

        score = (
            clamp(item.get("quality", 0.5))
            +
            clamp(item.get("reliability", 0.5))
            +
            clamp(item.get("directness", 0.5))
        ) / 3

        evidence_scores.append(score)

    theory_scores = []

    for theory in theories:

        if not isinstance(theory, dict):
            continue

        theory_scores.append(
            clamp(
                theory.get("score", 0.0)
            )
        )

    timeline_scores = []

    for event in timeline:

        if not isinstance(event, dict):
            continue

        timeline_scores.append(
            clamp(
                event.get("confidence", 0.5)
            )
        )

    evidence_quality = (
        sum(evidence_scores)
        / len(evidence_scores)
        if evidence_scores
        else 0.5
    )

    theory_confidence = (
        max(theory_scores)
        if theory_scores
        else 0.0
    )

    timeline_certainty = (
        sum(timeline_scores)
        / len(timeline_scores)
        if timeline_scores
        else 0.5
    )

    overall = (
        evidence_quality * 0.4
        +
        theory_confidence * 0.4
        +
        timeline_certainty * 0.2
    )

    return {

        "overall":
            round(overall, 3),

        "theory":
            round(theory_confidence, 3),

        "evidence_quality":
            round(evidence_quality, 3),

        "timeline_certainty":
            round(timeline_certainty, 3),
    }


# ============================================================
# INFORMATION GAIN
# ============================================================

def build_information_gain(
    evidence_gaps,
    next_best_evidence,
):

    output = []

    for index, item in enumerate(
        next_best_evidence or [],
        start=1,
    ):

        if isinstance(item, dict):

            action = (
                item.get("action")
                or item.get("description")
                or "Obtain additional evidence."
            )

            reason = (
                item.get("reason")
                or "Could reduce uncertainty."
            )

            priority = item.get(
                "priority",
                index,
            )

        else:

            action = str(item)
            reason = "Could reduce uncertainty."
            priority = index

        output.append({

            "priority":
                priority,

            "action":
                action,

            "reason":
                reason,

            "estimated_information_gain":
                round(
                    max(
                        0.1,
                        1.0 - (
                            index * 0.12
                        ),
                    ),
                    3,
                ),
        })

    if not output:

        for index, gap in enumerate(
            evidence_gaps or [],
            start=1,
        ):

            output.append({

                "priority":
                    index,

                "action":
                    str(gap),

                "reason":
                    "Resolving this evidence gap may reduce case uncertainty.",

                "estimated_information_gain":
                    0.6,
            })

    return output


# ============================================================
# IDENTITY LOCK
# ============================================================

def build_identity_lock():

    return {

        "status":
            "LOCKED",

        "identity_reveal_required":
            False,

        "reason":
            (
                "LUNA can evaluate the incident "
                "without exposing personal identity."
            ),

        "authorization_required":
            True,
    }


# ============================================================
# INVESTIGATION GRAPH
# ============================================================

def build_investigation_graph(
    evidence,
    timeline,
    theories,
):

    nodes = []
    edges = []

    for item in evidence:

        if not isinstance(item, dict):
            continue

        evidence_id = item.get(
            "id",
            "UNKNOWN",
        )

        nodes.append({

            "id":
                evidence_id,

            "type":
                "EVIDENCE",

            "label":
                item.get(
                    "description",
                    evidence_id,
                ),
        })

    for event in timeline:

        if not isinstance(event, dict):
            continue

        event_id = event.get(
            "id",
            "UNKNOWN",
        )

        nodes.append({

            "id":
                event_id,

            "type":
                "EVENT",

            "label":
                event.get(
                    "event",
                    event_id,
                ),
        })

    for theory in theories:

        if not isinstance(theory, dict):
            continue

        theory_id = theory.get(
            "id",
            "UNKNOWN",
        )

        nodes.append({

            "id":
                theory_id,

            "type":
                "THEORY",

            "label":
                theory.get(
                    "title",
                    theory_id,
                ),
        })

        for evidence_id in theory.get(
            "supporting_evidence",
            [],
        ):

            edges.append({

                "source":
                    evidence_id,

                "target":
                    theory_id,

                "relationship":
                    "SUPPORTS",
            })

    return {

        "nodes":
            nodes,

        "edges":
            edges,
    }


# ============================================================
# REMOVE EVIDENCE SIMULATION
# ============================================================

def build_remove_evidence_simulation(
    evidence,
    theories,
):

    simulations = []

    for item in evidence:

        if not isinstance(item, dict):
            continue

        evidence_id = item.get(
            "id",
            "UNKNOWN",
        )

        influence = 0

        for theory in theories:

            if not isinstance(theory, dict):
                continue

            supporting = theory.get(
                "supporting_evidence",
                [],
            )

            if evidence_id in supporting:
                influence += 1

        simulations.append({

            "removed_evidence":
                evidence_id,

            "affected_theories":
                influence,

            "impact":
                (
                    "HIGH"
                    if influence >= 2
                    else
                    "MEDIUM"
                    if influence == 1
                    else
                    "LOW"
                ),

            "note":
                (
                    "Removing this evidence should trigger "
                    "a re-evaluation of dependent theories."
                ),
        })

    return simulations


# ============================================================
# INVESTIGATOR ALERTS
# ============================================================

def build_investigator_alerts(
    contradictions,
    evidence_gaps,
    blind_spots,
):

    alerts = []

    for item in contradictions or []:

        alerts.append({

            "severity":
                "HIGH",

            "type":
                "CONTRADICTION",

            "message":
                str(item),
        })

    for item in evidence_gaps or []:

        alerts.append({

            "severity":
                "MEDIUM",

            "type":
                "EVIDENCE_GAP",

            "message":
                str(item),
        })

    for item in blind_spots or []:

        if not isinstance(item, dict):
            continue

        if item.get("severity") == "HIGH":

            alerts.append({

                "severity":
                    "HIGH",

                "type":
                    "BLIND_SPOT",

                "message":
                    item.get(
                        "description",
                        "Critical visibility gap detected.",
                    ),
            })

    return alerts


# ============================================================
# MAIN LUNA PIPELINE
# ============================================================

async def run_luna_pipeline(
    case_text: str = "",
    evidence=None,
    timeline=None,
    contradictions=None,
    gaps=None,
):

    case_text = case_text or ""

    evidence = evidence or []
    timeline = timeline or []
    contradictions = contradictions or []
    gaps = gaps or []

    # ========================================================
    # API KEY
    # ========================================================

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add GEMINI_API_KEY=YOUR_KEY "
            "to backend/.env"
        )

    # ========================================================
    # GEMINI
    # ========================================================

    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=api_key
    )

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are LUNA — Law-enforcement Unified Network for Advanced Investigation.

You are an investigative reasoning system.

You must NOT accuse people.

You must distinguish:

OBSERVED FACT
INFERENCE
ASSUMPTION
UNKNOWN

Your task:

1. Extract evidence.
2. Reconstruct the incident timeline.
3. Generate competing explanations.
4. Attack those explanations.
5. Identify contradictions.
6. Identify unsupported claims.
7. Identify alternative explanations.
8. Identify evidence gaps.
9. Identify unknown events.
10. Recommend the next best evidence.
11. Explain what evidence would change the conclusion.

IMPORTANT:

Never invent evidence.

Never invent timestamps.

Never invent identities.

If exact timing is unavailable use "UNKNOWN".

Every meaningful event should still appear in the timeline.

Generate at least two theories when meaningful alternatives exist.

Return ONLY valid JSON.

============================================================
OUTPUT
============================================================

{{
  "case_summary": "",

  "evidence": [
    {{
      "id": "EV-001",
      "type": "",
      "source": "",
      "description": "",
      "quality": 0.0,
      "reliability": 0.0,
      "directness": 0.0
    }}
  ],

  "timeline": [
    {{
      "id": "EVENT-001",
      "timestamp": "",
      "event": "",
      "source": "",
      "confidence": 0.0
    }}
  ],

  "theories": [
    {{
      "id": "T-001",
      "title": "",
      "explanation": "",
      "supporting_evidence": [],
      "contradicting_evidence": [],
      "assumptions": [],
      "score": 0.0,
      "confidence": "low"
    }}
  ],

  "red_team": [
    {{
      "theory_id": "T-001",
      "challenge": ""
    }}
  ],

  "unsupported_claims": [],

  "alternative_explanations": [],

  "critical_questions": [],

  "evidence_gaps": [],

  "next_best_evidence": [
    {{
      "priority": 1,
      "action": "",
      "reason": ""
    }}
  ],

  "contradictions": []
}}

============================================================
CASE MATERIAL
============================================================

{case_text}
"""

    # ========================================================
    # GEMINI REQUEST
    # ========================================================

    try:

        print(
            "\\n[LUNA] Sending case to Gemini..."
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=16384,
                response_mime_type="application/json",
            ),
        )

        raw = (
            response.text
            if response and response.text
            else ""
        )

        print(
            "[LUNA] Gemini response received."
        )

        print(
            "[LUNA] Response length:",
            len(raw),
        )

    except Exception as exc:

        print(
            "[LUNA GEMINI ERROR]",
            repr(exc),
        )

        raise RuntimeError(
            f"Gemini analysis failed: {exc}"
        ) from exc

    # ========================================================
    # PARSE
    # ========================================================

    result = extract_json(raw)

    if not isinstance(result, dict):

        result = {

            "case_summary":
                "LUNA received case material but could not parse the generated analysis.",

            "evidence": [],

            "timeline": [],

            "theories": [],

            "red_team": [],

            "unsupported_claims": [],

            "alternative_explanations": [],

            "critical_questions": [],

            "evidence_gaps": [],

            "next_best_evidence": [],

            "contradictions": [],
        }

    # ========================================================
    # NORMALIZE
    # ========================================================

    result["evidence"] = normalize_evidence(
        result.get("evidence")
    )

    result["theories"] = normalize_theories(
        result.get("theories")
    )

    result["red_team"] = normalize_red_team(
        result.get("red_team")
    )

    result["unsupported_claims"] = as_list(
        result.get("unsupported_claims")
    )

    result["alternative_explanations"] = as_list(
        result.get("alternative_explanations")
    )

    result["critical_questions"] = as_list(
        result.get("critical_questions")
    )

    result["evidence_gaps"] = as_list(
        result.get("evidence_gaps")
    )

    result["contradictions"] = as_list(
        result.get("contradictions")
    )

    result["next_best_evidence"] = as_list(
        result.get("next_best_evidence")
    )

    # ========================================================
    # TIMELINE
    # ========================================================

    normalized_timeline = normalize_timeline(
        result.get("timeline")
    )

    if not normalized_timeline:

        normalized_timeline = normalize_timeline(
            timeline
        )

    if not normalized_timeline:

        normalized_timeline = build_timeline_from_text(
            case_text
        )

    if not normalized_timeline:

        normalized_timeline = build_timeline_from_evidence(
            result["evidence"]
        )

    if not normalized_timeline and case_text.strip():

        normalized_timeline = [{

            "id":
                "EVENT-001",

            "timestamp":
                "UNKNOWN",

            "event":
                "Case material received and processed by LUNA.",

            "source":
                "CASE-TEXT",

            "confidence":
                0.5,
        }]

    result["timeline"] = normalized_timeline

    # ========================================================
    # ADVANCED REASONING
    # ========================================================

    result["evidence_dna"] = build_evidence_dna(
        result["evidence"]
    )

    result["evidence_dependencies"] = (
        build_evidence_dependencies(
            result["evidence"],
            result["theories"],
        )
    )

    result["theory_collisions"] = (
        build_theory_collisions(
            result["theories"]
        )
    )

    result["counterfactuals"] = (
        build_counterfactuals(
            result["theories"]
        )
    )

    result["unknown_events"] = (
        build_unknown_events(
            result["timeline"],
            result["contradictions"],
        )
    )

    result["blind_spots"] = build_blind_spots(
        case_text,
        result["evidence"],
    )

    result["confidence"] = build_confidence(
        result["evidence"],
        result["theories"],
        result["timeline"],
    )

    result["information_gain"] = (
        build_information_gain(
            result["evidence_gaps"],
            result["next_best_evidence"],
        )
    )

    result["remove_evidence_simulation"] = (
        build_remove_evidence_simulation(
            result["evidence"],
            result["theories"],
        )
    )

    result["investigator_alerts"] = (
        build_investigator_alerts(
            result["contradictions"],
            result["evidence_gaps"],
            result["blind_spots"],
        )
    )

    result["identity_lock"] = (
        build_identity_lock()
    )

    result["investigation_graph"] = (
        build_investigation_graph(
            result["evidence"],
            result["timeline"],
            result["theories"],
        )
    )

    result["incident_replay"] = (
        build_incident_replay(
            result["timeline"]
        )
    )

    # ========================================================
    # INVESTIGATION METRICS
    # ========================================================

    evidence_scores = [
        safe_float(
            item.get("quality", 0)
        )
        for item in result["evidence"]
        if isinstance(item, dict)
    ]

    theory_scores = [
        safe_float(
            item.get("score", 0)
        )
        for item in result["theories"]
        if isinstance(item, dict)
    ]

    result["investigation_metrics"] = {

        "evidence_count":
            len(result["evidence"]),

        "theory_count":
            len(result["theories"]),

        "timeline_event_count":
            len(result["timeline"]),

        "evidence_gap_count":
            len(result["evidence_gaps"]),

        "contradiction_count":
            len(result["contradictions"]),

        "unknown_event_count":
            len(result["unknown_events"]),

        "average_evidence_quality":
            round(
                sum(evidence_scores)
                / len(evidence_scores)
                if evidence_scores
                else 0,
                3,
            ),

        "average_theory_robustness":
            round(
                sum(theory_scores)
                / len(theory_scores)
                if theory_scores
                else 0,
                3,
            ),
    }

    # ========================================================
    # CASE METADATA
    # ========================================================

    result["case_id"] = (
        result.get("case_id")
        or f"LUNA-{uuid.uuid4().hex[:8].upper()}"
    )

    result["status"] = (
        "CONDITIONALLY_RESOLVED"
        if result["theories"]
        else "ANALYSIS_COMPLETE"
    )

    result["generated_at"] = (
        datetime.utcnow().isoformat()
        + "Z"
    )

    # ========================================================
    # FINAL LOG
    # ========================================================

    print(
        "\\n[LUNA] Analysis complete."
    )

    print(
        "[LUNA] Case:",
        result["case_id"],
    )

    print(
        "[LUNA] Evidence:",
        len(result["evidence"]),
    )

    print(
        "[LUNA] Timeline:",
        len(result["timeline"]),
    )

    print(
        "[LUNA] Theories:",
        len(result["theories"]),
    )

    print(
        "[LUNA] Contradictions:",
        len(result["contradictions"]),
    )

    print(
        "[LUNA] Evidence gaps:",
        len(result["evidence_gaps"]),
    )

    return result