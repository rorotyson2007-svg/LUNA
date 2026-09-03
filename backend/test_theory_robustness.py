from app.models.evidence import Evidence
from app.models.theory import Theory

from app.engines.evidence_dependency import (
    simulate_evidence_removal,
)


def test_remove_evidence_simulation():

    evidence = [
        Evidence(
            id="EV-001",
            type="CCTV",
            timestamp="18:40",
            source="CAM-01",
            observation="Door opens",
        ),

        Evidence(
            id="EV-002",
            type="CCTV",
            timestamp="18:41",
            source="CAM-02",
            observation="Person enters",
            dependencies=["EV-001"],
        ),
    ]

    theory = Theory(
        id="T-001",
        title="Unauthorized Entry",
        explanation="Person entered without authorization",
        supporting_evidence=[
            "EV-001",
            "EV-002",
        ],
    )

    result = simulate_evidence_removal(
        theory,
        evidence,
        "EV-001",
    )

    assert result["theory_id"] == "T-001"

    assert result["removed_evidence"] == "EV-001"

    assert result["original_robustness"] == 1.0

    assert result["new_robustness"] == 0.5

    assert result["impact"] == 0.5

    assert result["remaining_evidence"] == ["EV-002"]