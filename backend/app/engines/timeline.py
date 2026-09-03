from datetime import datetime
from typing import List

from app.models.evidence import Evidence
from app.models.event import Event


def parse_timestamp(timestamp: str) -> datetime:
    """
    Convert an ISO-style timestamp into a datetime object.

    Currently supports HH:MM timestamps used by our MVP demo.
    """

    return datetime.strptime(timestamp, "%H:%M")


def build_timeline(evidence: List[Evidence]) -> List[Event]:
    """
    Convert raw evidence into a chronological list of observable events.

    Important:
    This function does NOT infer intent, guilt, or causality.
    It only organizes observations.
    """

    sorted_evidence = sorted(
        evidence,
        key=lambda item: parse_timestamp(item.timestamp)
    )

    timeline = []

    for index, item in enumerate(sorted_evidence, start=1):

        event = Event(
            id=f"EV{index:02d}",
            timestamp=item.timestamp,
            event_type=item.type,
            description=item.observation,
            evidence_ids=[item.id],
            people=item.people,
            objects=item.objects,
            location=item.location
        )

        timeline.append(event)

    return timeline