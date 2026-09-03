from app.models.evidence import Evidence
from app.engines.evidence_dna import build_evidence_dna


def test_evidence_dna():

    evidence = Evidence(
        id="EV-001",
        type="CCTV",
        timestamp="18:42:15",
        source="CAM-01",
        observation="Unknown individual enters corridor",

        reliability=0.9,
        directness=0.8,
        timestamp_confidence=0.7,

        supports_theories=["T-001"],
        refutes_theories=["T-002"],

        dependencies=["EV-000"],
        contradictions=["EV-005"],
    )

    dna = build_evidence_dna(
        evidence,
        ["T-001", "T-002", "T-003"]
    )

    assert dna["id"] == "EV-001"

    assert dna["quality"] > 0

    assert dna["contribution_scores"]["T-001"] > 0

    assert dna["contribution_scores"]["T-002"] < 0

    assert dna["contribution_scores"]["T-003"] == 0