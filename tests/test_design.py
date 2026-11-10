import dataclasses
import json
import unittest
from pathlib import Path

from build import load_design, report, scad_parameters


CONFIG = Path(__file__).resolve().parents[1] / "examples" / "default.json"


class DesignTests(unittest.TestCase):
    def setUp(self):
        self.design = load_design(CONFIG)

    def test_default_holes_clear_channel_and_are_symmetric(self):
        result = report(self.design)
        left, right = result["mount_hole_centres_x_mm"]
        self.assertAlmostEqual(left + right, result["base_width_mm"])
        self.assertLess(self.design.mount_hole_y + self.design.mount_hole_diameter / 2 + self.design.wall_thickness, self.design.front_y)

    def test_shallow_base_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "too shallow"):
            dataclasses.replace(self.design, base_depth=10).validate()

    def test_hole_intersecting_channel_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "clear the panel channel"):
            dataclasses.replace(self.design, mount_hole_y=self.design.front_y).validate()

    def test_invalid_numeric_value_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "finite number"):
            dataclasses.replace(self.design, panel_width=float("nan")).validate()

    def test_parameter_export_is_deterministic(self):
        self.assertEqual(scad_parameters(self.design), scad_parameters(load_design(CONFIG)))
        self.assertIn("panel_width = 160;", scad_parameters(self.design))

    def test_unexpected_configuration_key_is_rejected(self):
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        data["unknown"] = 1
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "extra=\\['unknown'\\]"):
                load_design(path)


if __name__ == "__main__":
    unittest.main()
