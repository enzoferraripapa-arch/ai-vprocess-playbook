from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_routes(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    routes = data.get("routes")
    if not isinstance(routes, list):
        raise ValueError("expected a top-level 'routes' list")
    return routes


def render_markdown(routes: list[dict[str, str]]) -> str:
    lines = [
        "| Route | Trigger | Activity | Output candidate | Boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for route in routes:
        lines.append(
            "| {route} | {trigger} | {activity} | {output_candidate} | {boundary} |".format(
                route=route.get("route", ""),
                trigger=route.get("trigger", ""),
                activity=route.get("activity", ""),
                output_candidate=route.get("output_candidate", ""),
                boundary=route.get("boundary", ""),
            )
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a sample routing JSON file as Markdown.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    print(render_markdown(load_routes(args.input)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
