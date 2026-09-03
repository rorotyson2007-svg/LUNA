from app.models.evidence import Evidence

from app.engines.evidence_dependency import (
    build_dependency_graph,
    get_upstream_dependencies,
    calculate_dependency_factor,
    calculate_theory_robustness,
)


def test_dependency_graph():

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
            observation="Person enters corridor",
            dependencies=["EV-001"],
        ),

        Evidence(
            id="EV-003",
            type="CCTV",
            timestamp="18:42",
            source="CAM-03",
            observation="Person reaches room",
            dependencies=["EV-002"],
        ),
    ]

    graph = build_dependency_graph(evidence)

    assert graph["EV-002"] == ["EV-001"]
    assert graph["EV-003"] == ["EV-002"]


def test_upstream_dependencies():

    graph = {
        "EV-001": [],
        "EV-002": ["EV-001"],
        "EV-003": ["EV-002"],
    }

    dependencies = get_upstream_dependencies(
        "EV-003",
        graph,
    )

    assert "EV-002" in dependencies
    assert "EV-001" in dependencies


def test_dependency_factor():

    evidence = Evidence(
        id="EV-002",
        type="CCTV",
        timestamp="18:41",
        source="CAM-02",
        observation="Person enters corridor",
        dependencies=["EV-001"],
    )

    factor = calculate_dependency_factor(
        evidence,
        {"EV-001"},
    )

    assert factor == 1.0

    factor = calculate_dependency_factor(
        evidence,
        set(),
    )

    assert factor == 0.0


def test_theory_robustness():

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

    robustness = calculate_theory_robustness(
        evidence,
        {"EV-001", "EV-002"},
    )

    assert robustness == 1.0

    robustness = calculate_theory_robustness(
        evidence,
        {"EV-002"},
    )

    assert robustness == 0.5