include <BOSL2/std.scad>

include <constants.scad>
use <hanger.scad>


/* [Primary parameters] */
// Path to original STL model
model_path = "";

// Which variant to use
variant = 0; // [0: Original, 1: Thicker cleats]

// Hanger tolerance
hanger_tolerance = 0.15;

/* [Plate parameters] */
// Number of 42mm plate units
hanger_units = 1;

// Plate thickness in mm
plate_thickness = 0;

// Extend bottom of plate in mm
extend_bottom = 0;

/* [Original model transform parameters] */
// X offset of original model
offset_x = 0;

// Y offset of original model
offset_y = 0;

// Z offset of original model
offset_z = 0;

// X rotation of original model
rotate_x = 0;

// Y rotation of original model
rotate_y = 0;

// Z rotation of original model
rotate_z = 0;

/* [Hidden] */
$fa=0.5;
$fs=0.5;


module anything(
    model_path="",
    variant=variant_original,
    hanger_tolerance=0.15,
    hanger_units=1,
    plate_thickness=3,
    extend_bottom=0,
    offset_x=0,
    offset_y=0,
    offset_z=0,
    rotate_x=0,
    rotate_y=0,
    rotate_z=0,
) {
    actual_plate_width = get_hanger_plate_width(hanger_units * plate_width);

    hanger_plate_offset = get_hanger_plate_offset(variant, hanger_tolerance);
    total_thickness = plate_thickness + hanger_thickness + hanger_plate_offset;

    union() {
        translate([0, -total_thickness, 0])
            hanger_plate(
                variant=variant,
                plate_thickness=plate_thickness,
                hanger_units=hanger_units,
                hanger_tolerance=hanger_tolerance,
                outer_radius=plate_outer_radius,
                extend_bottom=extend_bottom,
            );

        if (model_path != "") {
            translate([offset_x, offset_y, offset_z])
                rotate([rotate_x, rotate_y, rotate_z])
                    import(model_path);
        }
    }
}


anything(
    model_path=model_path,
    variant=variant,
    hanger_tolerance=hanger_tolerance,
    hanger_units=hanger_units,
    plate_thickness=plate_thickness,
    extend_bottom=extend_bottom,
    offset_x=offset_x,
    offset_y=offset_y,
    offset_z=offset_z,
    rotate_x=rotate_x,
    rotate_y=rotate_y,
    rotate_z=rotate_z,
);
