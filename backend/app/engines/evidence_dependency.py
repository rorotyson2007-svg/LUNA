from typing import Dict, List

from app.models.evidence import Evidence


def build_dependency_graph(
    evidence_items: List[Evidence],
) -> Dict[str, List[str]]:
    """
    Builds an evidence dependency graph.
    """

    graph = {}

    for evidence in evidence_items:
        graph[evidence.id] = list(evidence.dependencies)

    return graph


def get_upstream_dependencies(
    evidence_id: str,
    graph: Dict[str, List[str]],
) -> List[str]:
    """
    Returns all evidence items that the given evidence
    ultimately depends on.
    """

    visited = set()
    result = []

    def visit(current_id: str):
        if current_id in visited:
            return

        visited.add(current_id)

        for dependency in graph.get(current_id, []):
            if dependency not in result:
                result.append(dependency)

            visit(dependency)

    visit(evidence_id)

    return result


def calculate_dependency_factor(
    evidence: Evidence,
    available_evidence_ids: set[str],
) -> float:
    """
    Calculates how much of an evidence item's dependency chain
    is still available.
    """

    if not evidence.dependencies:
        return 1.0

    available = sum(
        1
        for dependency in evidence.dependencies
        if dependency in available_evidence_ids
    )

    return round(
        available / len(evidence.dependencies),
        3,
    )


def calculate_theory_robustness(
    theory_evidence: List[Evidence],
    available_evidence_ids: set[str],
) -> float:
    """
    Calculates how resilient a theory is based on the
    availability of its evidence dependencies.
    """

    if not theory_evidence:
        return 0.0

    factors = []

    for evidence in theory_evidence:
        factor = calculate_dependency_factor(
            evidence,
            available_evidence_ids,
        )

        factors.append(factor)

    return round(
        sum(factors) / len(factors),
        3,
    )


def simulate_evidence_removal(
    theory,
    evidence_items: List[Evidence],
    remove_evidence_id: str,
) -> Dict:
    """
    Simulates removing one evidence item from a theory.

    Nothing is permanently deleted.
    """

    original_ids = {
        evidence.id
        for evidence in evidence_items
    }

    # The evidence is removed from the AVAILABLE evidence pool,
    # but dependent evidence is still retained.
    remaining_ids = original_ids - {remove_evidence_id}

    # Keep all supporting evidence so we can measure how the
    # remaining evidence is affected by the removal.
    theory_evidence = [
        evidence
        for evidence in evidence_items
        if evidence.id in theory.supporting_evidence
    ]

    original_evidence = [
        evidence
        for evidence in evidence_items
        if evidence.id in theory.supporting_evidence
    ]

    original_robustness = calculate_theory_robustness(
        original_evidence,
        original_ids,
    )

    new_robustness = calculate_theory_robustness(
        theory_evidence,
        remaining_ids,
    )

    impact = round(
        original_robustness - new_robustness,
        3,
    )

    return {
        "theory_id": theory.id,
        "removed_evidence": remove_evidence_id,

        "original_robustness": original_robustness,
        "new_robustness": new_robustness,

        "impact": impact,

        "remaining_evidence": [
            evidence.id
            for evidence in theory_evidence
            if evidence.id != remove_evidence_id
        ],
    }