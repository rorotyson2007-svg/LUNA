from typing import List

from app.models.evidence import Evidence
from app.models.contradiction import Contradiction


def detect_contradictions(
    evidence: List[Evidence],
) -> List[Contradiction]:

    contradictions = []

    # ---------------------------------------------------------
    # Rule 1:
    # Look for conflicting observations about the same person
    # carrying / not carrying the same object.
    # ---------------------------------------------------------

    for i, evidence_a in enumerate(evidence):

        for evidence_b in evidence[i + 1:]:

            if evidence_a.id == evidence_b.id:
                continue

            # Same person mentioned in both
            common_people = set(evidence_a.people) & set(evidence_b.people)

            # Same object mentioned in both
            common_objects = set(evidence_a.objects) & set(evidence_b.objects)

            if not common_people or not common_objects:
                continue

            observation_a = evidence_a.observation.lower()
            observation_b = evidence_b.observation.lower()

            carrying_words = [
                "carrying",
                "holding",
                "with the laptop",
                "with laptop"
            ]

            not_carrying_words = [
                "not visibly carried",
                "empty-handed",
                "without the laptop",
                "without laptop"
            ]

            a_carrying = any(
                word in observation_a
                for word in carrying_words
            )

            b_carrying = any(
                word in observation_b
                for word in carrying_words
            )

            a_not_carrying = any(
                word in observation_a
                for word in not_carrying_words
            )

            b_not_carrying = any(
                word in observation_b
                for word in not_carrying_words
            )

            if (a_carrying and b_not_carrying) or (
                b_carrying and a_not_carrying
            ):

                contradiction = Contradiction(
                    id=f"C{len(contradictions) + 1:02d}",

                    description=(
                        f"Evidence {evidence_a.id} and "
                        f"{evidence_b.id} provide conflicting "
                        f"observations about whether "
                        f"Person #{list(common_people)[0]} "
                        f"was carrying the object."
                    ),

                    evidence_a=evidence_a.id,
                    evidence_b=evidence_b.id,

                    severity="high"
                )

                contradictions.append(contradiction)

    # ---------------------------------------------------------
    # Rule 2:
    # Detect evidence that explicitly says something is unknown
    # or not visible.
    #
    # These aren't contradictions, but they are important
    # investigation gaps. For now we simply report them.
    # ---------------------------------------------------------

    return contradictions