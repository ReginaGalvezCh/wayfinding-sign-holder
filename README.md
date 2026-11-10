# Wayfinding Sign Holder

A parametric, 3D-printable holder for a removable event or venue sign. The project pairs a small **Python validation tool** with an **OpenSCAD model**: edit a JSON design, check its dimensions, and export an STL.

> **Status:** portfolio learning project. The default design passes dimensional tests, but it has not been rendered in OpenSCAD here, printed, or load tested.

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

Requirements: Python 3.10+. OpenSCAD is needed for the STL export.

```sh
python3 -m unittest discover -s tests -v
python3 build.py examples/default.json --check
python3 build.py examples/default.json --out build
```

The final command writes `cad/generated_params.scad` and `build/dimensions.json`. Then export the model with either command:

```sh
python3 build.py examples/default.json --out build --render
# or, after generating the parameters:
openscad -o build/sign-holder.stl cad/sign_holder.scad
```

Open the STL in a slicer or the `.scad` file in OpenSCAD to inspect the geometry. The `.scad` file depends on generated parameters, so run `build.py` first.

## What the validation checks

| Constraint | Why it matters |
| --- | --- |
| Finite, positive dimensions and minimum wall/base thickness | Rejects unusable inputs before rendering. |
| Front wall lower than back wall | Leaves the panel accessible from above. |
| Base depth for both walls and the channel | Prevents channel geometry from leaving the base. |
| Symmetric screw holes with edge clearance | Keeps holes in the mounting region and apart from each other. |
| Hole clearance from the front wall and channel | Avoids cutting into the panel support. |

Run the unit tests to see valid and invalid cases. The GitHub Actions workflow also attempts an OpenSCAD STL export and checks that the file is nonempty. That workflow has not run yet.

## Files

- `examples/default.json` — editable dimensions, in millimetres.
- `build.py` — JSON validation, derived dimensions, parameter export, optional render command.
- `cad/sign_holder.scad` — parametric solid model.
- `tests/test_design.py` — boundary checks and deterministic export checks.
- `.github/workflows/check.yml` — tests and STL export on GitHub.

## Limits and authorship

The model does not prove structural strength, printability, or a real-world fit. A physical prototype would need a material choice, printer tolerance check, screw selection, and load test. This project was created with AI assistance and is a new portfolio study; it is not a claim of prior professional OpenSCAD experience or a contribution to an established open-source project. Anyone presenting it should review the code, run the 3D export, and be able to explain the design decisions.

OpenSCAD CLI reference: [Using OpenSCAD in a command line environment](https://files.openscad.org/documentation/manual/Using_OpenSCAD_in_a_command_line_environment.html).
