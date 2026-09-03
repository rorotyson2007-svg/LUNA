import json

from app.models.evidence import Evidence
from app.engines.timeline import build_timeline


def load_demo_case():
    with open("data/demo_case.json", "r") as file:
        return json.load(file)


data = load_demo_case()

evidence = [
    Evidence(**item)
    for item in data["evidence"]
]

timeline = build_timeline(evidence)

print("\n===== LUNA TIMELINE =====\n")

for event in timeline:
    print(
        f"{event.timestamp} | "
        f"{event.event_type:<12} | "
        f"{event.description}"
    )