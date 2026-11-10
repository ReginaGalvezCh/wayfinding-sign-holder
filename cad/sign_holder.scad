include <generated_params.scad>;

// Coordinates: x along the panel, y from mounting edge to the channel, z up.
channel_width = panel_thickness + thickness_clearance_total;
base_width = panel_width + 2 * width_clearance_each_side + 2 * end_margin;
front_y = base_depth - 2 * wall_thickness - channel_width;
back_y = base_depth - wall_thickness;

module holder() {
    difference() {
        union() {
            cube([base_width, base_depth, base_thickness]);
            translate([0, front_y, base_thickness])
                cube([base_width, wall_thickness, front_height]);
            translate([0, back_y, base_thickness])
                cube([base_width, wall_thickness, back_height]);
            // End stops limit side-to-side movement but keep the top open.
            translate([0, front_y + wall_thickness, base_thickness])
                cube([end_margin, channel_width, front_height]);
            translate([base_width - end_margin, front_y + wall_thickness, base_thickness])
                cube([end_margin, channel_width, front_height]);
        }
        for (hole_x = [mount_hole_edge_inset, base_width - mount_hole_edge_inset]) {
            translate([hole_x, mount_hole_y, -1])
                cylinder(h = base_thickness + 2, d = mount_hole_diameter, $fn = 48);
        }
    }
}

holder();
