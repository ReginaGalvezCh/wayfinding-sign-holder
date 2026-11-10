# Wayfinding Sign Holder

[![Check sign holder](https://github.com/ReginaGalvezCh/wayfinding-sign-holder/actions/workflows/check.yml/badge.svg)](https://github.com/ReginaGalvezCh/wayfinding-sign-holder/actions/workflows/check.yml)

A parametric, 3D-printable holder for a removable event or venue sign. The project pairs a small **Python validation tool** with an **OpenSCAD model** and a **Gmsh section mesh**: edit a JSON design, check its dimensions, export an STL, and mesh a 2D slice.

> **Status:** portfolio learning project. Automated checks cover dimensions, OpenSCAD STL export, and Gmsh section meshing. It has not been printed or load tested.

## The design problem

Temporary wayfinding signs need to be easy to replace without rebuilding the holder. This model uses a taller back wall, a shorter front lip, and end stops to form an open-top channel. Two holes in the base allow mounting ahead of the panel.

```text
Side view (not to scale)

                         back wall
                         ┌─────┐
               sign      │     │
             ┌──────┐    │     │
   front lip │      │    │     │
       ┌─────┤      │    │     │
       │     │      │    │     │
═══════╧═════╧══════╧════╧═════╧══ base
  mounting area       channel
```

The default configuration targets a 160 × 3 mm panel. It allows 0.5 mm at each end and 0.4 mm across the panel thickness. The resulting base is 177 × 55 mm. These are starting dimensions, not a certified fit for a particular material or printer.

## Quick start

Requirements: Python 3.10+. OpenSCAD is needed for the STL export; Gmsh is needed for the 2D mesh.

```sh
python3 -m unittest discover -s tests -v
python3 build.py examples/default.json --check
python3 build.py examples/default.json --out build
python3 build.py examples/default.json --out build --render --mesh
```

The build writes `cad/generated_params.scad`, `build/dimensions.json`, and `build/cross_section.geo`. The last command also exports `build/sign-holder.stl`, `build/cross_section.msh`, and `build/mesh_report.json`. You can run the exports separately:

```sh
python3 build.py examples/default.json --out build --render
python3 build.py examples/default.json --out build --mesh
# or, after generating the geometry files:
openscad -o build/sign-holder.stl cad/sign_holder.scad
gmsh build/cross_section.geo -2 -format msh2 -o build/cross_section.msh
```

Open the STL in a slicer or the `.scad` file in OpenSCAD to inspect the geometry. The `.scad` file depends on generated parameters, so run `build.py` first.

## Why a separate 2D mesh?

Gmsh meshes the holder's mid-span side section in the depth–height plane. This section contains the base, front lip, back wall, and channel floor. It excludes the two mounting holes and end stops, which sit away from the mid-span slice. The mesh provides a small, reproducible starting point for future numerical analysis; it is **not** a mesh of the full STL and does not establish structural strength.

The mesh has named physical groups for the mounting edge, panel channel floor, and solid section. `build.py --mesh` checks that triangles and both boundary groups exist, then compares the total triangle area with an independently calculated section area. This catches an empty or geometrically wrong mesh even if Gmsh exits successfully.

## What the validation checks

| Constraint | Why it matters |
| --- | --- |
| Finite, positive dimensions and minimum wall/base thickness | Rejects unusable inputs before rendering. |
| Front wall lower than back wall | Leaves the panel accessible from above. |
| Base depth for both walls and the channel | Prevents channel geometry from leaving the base. |
| Symmetric screw holes with edge clearance | Keeps holes in the mounting region and apart from each other. |
| Hole clearance from the front wall and channel | Avoids cutting into the panel support. |

Run the unit tests to see valid and invalid cases. The GitHub Actions workflow exports an STL with OpenSCAD, generates a Gmsh mesh, and checks the mesh area and boundary groups.
Each successful run also offers a `sign-holder-model-and-mesh` artifact containing the STL, mesh, geometry script, and dimension reports for inspection.

## Files

- `examples/default.json` — editable dimensions, in millimetres.
- `build.py` — JSON validation, derived dimensions, parameter export, optional render command.
- `cad/sign_holder.scad` — parametric solid model.
- `mesh_section.py` — Gmsh geometry generation and MSH2 mesh validation.
- `tests/test_design.py` — boundary checks and deterministic export checks.
- `.github/workflows/check.yml` — tests, STL export, and mesh validation on GitHub.

## Try it yourself

Change `panel_thickness` from `3.0` to `4.0` in a copy of `examples/default.json`. Run `--check` first, then `--render --mesh`. Compare the generated `dimensions.json` and `mesh_report.json` with the default: the channel widens and shifts the front lip, while the section area stays the same because the wall and base material dimensions have not changed. Open both models to see the difference before using the design for a real panel.

## Limits and authorship

The model does not prove structural strength, printability, or a real-world fit. A physical prototype would need a material choice, printer tolerance check, screw selection, and load test. This is a new portfolio study; it is not a claim of prior professional OpenSCAD experience or a contribution to an established open-source project. Anyone presenting it should review the code, run the 3D export, and be able to explain the design decisions.

OpenSCAD CLI reference: [Using OpenSCAD in a command line environment](https://files.openscad.org/documentation/manual/Using_OpenSCAD_in_a_command_line_environment.html).

Gmsh reference: [command-line meshing and physical groups](https://gmsh.info/doc/texinfo/gmsh.html).
