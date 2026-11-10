"""Generate and check a Gmsh mesh of the holder's mid-span side section."""

from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from build import Design


def expected_area(design: Design) -> float:
    """Section at the middle of the panel, away from end stops and holes."""
    return design.base_depth * design.base_thickness + design.wall_thickness * (
        design.back_height + design.front_height
    )


def cross_section_geo(design: Design) -> str:
    """Trace the material boundary in the (depth, height) plane."""
    depth = design.base_depth
    base = design.base_thickness
    wall = design.wall_thickness
    front = design.front_y
    size = min(base, wall, design.channel_width) / 2
    points = [
        (0, 0),
        (depth, 0),
        (depth, base + design.back_height),
        (depth - wall, base + design.back_height),
        (depth - wall, base),
        (front + wall, base),
        (front + wall, base + design.front_height),
        (front, base + design.front_height),
        (front, base),
        (0, base),
    ]
    fmt = lambda value: format(value, ".12g")
    lines = [
        "// Mid-span 2D section derived from examples/default.json via build.py.",
        "// End stops and screw holes are intentionally outside this slice.",
        'SetFactory("Built-in");',
    ]
    lines.extend(
        f"Point({index}) = {{{fmt(x)}, {fmt(y)}, 0, {fmt(size)}}};"
        for index, (x, y) in enumerate(points, start=1)
    )
    lines.extend(
        f"Line({index}) = {{{index}, {index % len(points) + 1}}};"
        for index in range(1, len(points) + 1)
    )
    lines += [
        "Curve Loop(1) = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};",
        "Plane Surface(1) = {1};",
        'Physical Curve("mounting_edge", 1) = {1};',
        'Physical Curve("panel_channel_floor", 2) = {5};',
        'Physical Surface("holder_section", 3) = {1};',
    ]
    return "\n".join(lines) + "\n"


def _section(lines: list[str], name: str) -> list[str]:
    try:
        start = lines.index(f"${name}") + 1
        end = lines.index(f"$End{name}", start)
    except ValueError as error:
        raise ValueError(f"missing MSH2 section {name}") from error
    return lines[start:end]


def validate_msh2(path: Path, design: Design) -> dict[str, float | int]:
    """Check that Gmsh exported the intended section, not just a nonempty file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not _section(lines, "MeshFormat")[0].startswith("2.2 0 "):
        raise ValueError("expected ASCII MSH2 format")

    raw_nodes = _section(lines, "Nodes")
    node_count = int(raw_nodes[0])
    if len(raw_nodes) - 1 != node_count:
        raise ValueError("node count does not match mesh header")
    nodes = {}
    for line in raw_nodes[1:]:
        node_id, x, y, z = line.split()
        nodes[int(node_id)] = (float(x), float(y), float(z))
    if len(nodes) != node_count:
        raise ValueError("duplicate node IDs")

    raw_elements = _section(lines, "Elements")
    if len(raw_elements) - 1 != int(raw_elements[0]):
        raise ValueError("element count does not match mesh header")
    triangle_count = 0
    boundary_groups: set[int] = set()
    area = 0.0
    for line in raw_elements[1:]:
        fields = [int(value) for value in line.split()]
        element_type, tag_count = fields[1], fields[2]
        tags = fields[3 : 3 + tag_count]
        node_ids = fields[3 + tag_count :]
        if not tags:
            raise ValueError("mesh element has no physical group")
        if element_type == 1 and tags[0] in (1, 2):
            boundary_groups.add(tags[0])
        if element_type == 2:
            if tags[0] != 3 or len(node_ids) != 3:
                raise ValueError("unexpected triangle physical group or shape")
            a, b, c = (nodes[node_id] for node_id in node_ids)
            area += abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2
            triangle_count += 1
    if triangle_count == 0 or boundary_groups != {1, 2}:
        raise ValueError("mesh needs triangles and both named boundary groups")
    target = expected_area(design)
    if not math.isclose(area, target, rel_tol=0.005, abs_tol=0.01):
        raise ValueError(f"mesh area {area:.3f} mm² differs from expected {target:.3f} mm²")
    return {"nodes": node_count, "triangles": triangle_count, "area_mm2": round(area, 3), "expected_area_mm2": round(target, 3)}
