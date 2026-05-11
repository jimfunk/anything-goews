from pydantic import BaseModel, Field
from sanic import response
from sanic.request import Request
from sanic_ext import openapi
from typing import Annotated
import hashlib
import logging
import os
import struct
import tempfile

from server.openscad import build_fused_model, MAX_UPLOAD_SIZE
from server.enums import Variant
from server.api import api_bp


logger = logging.getLogger("anything")


def is_valid_stl(data: bytes) -> bool:
    """Basic validation that data appears to be a valid STL file (binary or ASCII)."""
    if len(data) < 84:
        return data.lower().startswith(b'solid')

    # Check for ASCII STL
    header = data[:80]
    if header.startswith(b'solid') and b'\x00' not in header:
        return b'facet' in data

    # Check for binary STL: 84-byte header + 50 bytes per face
    num_faces = struct.unpack('<I', data[80:84])[0]
    expected_size = 84 + num_faces * 50
    return expected_size == len(data) and num_faces > 0


@openapi.component
class AnythingDefinition(BaseModel):
    plate_units: Annotated[int, Field(ge=1, description="Number of 42mm plate units")] = 1
    plate_thickness: Annotated[float, Field(ge=0, description="Plate thickness in mm")] = 0
    extend_bottom: Annotated[float, Field(ge=0, description="Extend bottom of plate in mm")] = 0
    variant: Variant = Variant.ORIGINAL
    hanger_tolerance: Annotated[float, Field(ge=0)] = 0.15
    offset_x: Annotated[float, Field(description="X offset in mm")] = 0
    offset_y: Annotated[float, Field(description="Y offset in mm")] = 0
    offset_z: Annotated[float, Field(description="Z offset in mm")] = 0
    rotate_x: Annotated[float, Field(description="X rotation in degrees")] = 0
    rotate_y: Annotated[float, Field(description="Y rotation in degrees")] = 0
    rotate_z: Annotated[float, Field(description="Z rotation in degrees")] = 0


def make_anything_filename(body: AnythingDefinition, uploaded_name: str = "") -> str:
    # Base name from uploaded file, or fallback to "model"
    if uploaded_name:
        base = uploaded_name.rsplit(".", 1)[0]  # strip extension
    else:
        base = "model"

    variant = "-thicker-cleats" if body.variant.to_int() == 1 else ""

    return f"{base}-goews{variant}.stl"


@api_bp.post("/anything")
@openapi.body(AnythingDefinition)
@openapi.response(200, "model/stl")
@openapi.description("Create a fused model with GOEWS mounting plate")
async def anything(request: Request):
    # File upload is optional - can generate plate-only
    uploaded_file = None
    if request.files:
        uploaded_file = request.files.get("model")

    # Get parameters from form
    try:
        plate_units = int(request.form.get("plate_units", 1))
        plate_thickness = float(request.form.get("plate_thickness", 0))
        extend_bottom = float(request.form.get("extend_bottom", 0))
        hanger_tolerance = float(request.form.get("hanger_tolerance", 0.15))
        offset_x = float(request.form.get("offset_x", 0))
        offset_y = float(request.form.get("offset_y", 0))
        offset_z = float(request.form.get("offset_z", 0))
        rotate_x = float(request.form.get("rotate_x", 0))
        rotate_y = float(request.form.get("rotate_y", 0))
        rotate_z = float(request.form.get("rotate_z", 0))
    except ValueError as e:
        return response.json({"error": f"Invalid parameter: {e}"}, status=400)

    # Validate file (if provided)
    if uploaded_file:
        if not uploaded_file.name.lower().endswith(".stl"):
            return response.json({"error": "Only STL files are supported"}, status=400)

        # File size limit
        if len(uploaded_file.body) > MAX_UPLOAD_SIZE:
            return response.json({"error": f"File too large (max {MAX_UPLOAD_SIZE // (1024*1024)}MB)"}, status=400)

        # Validate file content
        if not is_valid_stl(uploaded_file.body):
            return response.json({"error": "Uploaded file does not appear to be a valid STL"}, status=400)

    # Validate variant
    try:
        variant = Variant(int(request.form.get("variant", 0)))
    except (ValueError, TypeError):
        return response.json({"error": "Invalid variant. Must be 0 (Original) or 1 (Thicker Cleats)"}, status=400)

    try:
        # Write uploaded file to a named temp file (auto-cleanup after use)
        uploaded_path = ""
        temp_file = None
        if uploaded_file:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".stl")
            temp_file.write(uploaded_file.body)
            temp_file.close()
            uploaded_path = temp_file.name
            logger.info(f"Wrote upload to temp file: {uploaded_path}")

        try:
            # Compute content hash for cache key (temp path changes per request)
            content_hash = hashlib.sha256(uploaded_file.body).hexdigest() if uploaded_file else "none"

            # Build fused model (or plate-only if no file)
            stl_data = await build_fused_model(
                content_hash=content_hash,
                uploaded_stl_path=uploaded_path,
                variant=variant.to_int(),
                hanger_tolerance=hanger_tolerance,
                plate_units=plate_units,
                plate_thickness=plate_thickness,
                extend_bottom=extend_bottom,
                offset_x=offset_x,
                offset_y=offset_y,
                offset_z=offset_z,
                rotate_x=rotate_x,
                rotate_y=rotate_y,
                rotate_z=rotate_z,
            )
        finally:
            # Clean up the temp file regardless of success or failure
            if temp_file and os.path.exists(uploaded_path):
                os.unlink(uploaded_path)
                logger.debug(f"Cleaned up temp file: {uploaded_path}")

        # Generate filename
        uploaded_original_name = uploaded_file.name if uploaded_file else ""
        filename = make_anything_filename(
            AnythingDefinition(
                plate_units=plate_units,
                plate_thickness=plate_thickness,
                extend_bottom=extend_bottom,
                variant=variant,
                hanger_tolerance=hanger_tolerance,
                offset_x=offset_x,
                offset_y=offset_y,
                offset_z=offset_z,
                rotate_x=rotate_x,
                rotate_y=rotate_y,
                rotate_z=rotate_z,
            ),
            uploaded_name=uploaded_original_name,
        )

        return response.raw(
            stl_data,
            content_type="model/stl",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        logger.exception("Error generating model")
        return response.json({"error": str(e)}, status=500)
