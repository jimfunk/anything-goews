"""
Tests for OpenSCAD integration and model generation
"""
import pytest
import os
from server.openscad import build_fused_model, OpenSCADError


@pytest.fixture
def sample_stl_path():
    """Create a sample STL file for testing."""
    import struct
    import tempfile
    # Create minimal binary STL
    header = b"Test STL" + b"\x00" * 72  # 80 bytes
    num_faces = struct.pack('<I', 1)
    face_data = (
        struct.pack('<fff', 0.0, 0.0, 0.0) +  # Normal
        struct.pack('<fff', 0.0, 0.0, 0.0) +  # Vertex 1
        struct.pack('<fff', 10.0, 0.0, 0.0) +  # Vertex 2
        struct.pack('<fff', 0.0, 10.0, 0.0) +  # Vertex 3
        struct.pack('<H', 0)  # Attribute
    )
    stl_content = header + num_faces + face_data

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".stl")
    temp_file.write(stl_content)
    temp_file.close()
    filepath = temp_file.name

    yield filepath

    # Cleanup
    if os.path.exists(filepath):
        os.unlink(filepath)


@pytest.mark.asyncio
async def test_build_fused_model_with_sample_stl(sample_stl_path):
    """Test building a fused model with a sample STL."""
    result = await build_fused_model(
        content_hash="test_sample",
        uploaded_stl_path=sample_stl_path,
        variant=0,
        hanger_tolerance=0.15,
        plate_units=1,
        plate_thickness=3,
        extend_bottom=0,
        offset_x=0,
        offset_y=0,
        offset_z=0,
        rotate_x=0,
        rotate_y=0,
        rotate_z=0,
    )

    assert result is not None
    assert len(result) > 0
    assert isinstance(result, bytes)


@pytest.mark.asyncio
async def test_build_fused_model_different_variants(sample_stl_path):
    """Test building models with different variants."""
    result_original = await build_fused_model(
        content_hash="test_variant_0",
        uploaded_stl_path=sample_stl_path,
        variant=0,  # Original
        hanger_tolerance=0.15,
        plate_units=1,
        plate_thickness=3,
        extend_bottom=0,
        offset_x=0,
        offset_y=0,
        offset_z=0,
        rotate_x=0,
        rotate_y=0,
        rotate_z=0,
    )

    result_thicker = await build_fused_model(
        content_hash="test_variant_1",
        uploaded_stl_path=sample_stl_path,
        variant=1,  # Thicker cleats
        hanger_tolerance=0.15,
        plate_units=1,
        plate_thickness=3,
        extend_bottom=0,
        offset_x=0,
        offset_y=0,
        offset_z=0,
        rotate_x=0,
        rotate_y=0,
        rotate_z=0,
    )

    # Both should produce valid STL data
    assert len(result_original) > 0
    assert len(result_thicker) > 0


@pytest.mark.asyncio
async def test_build_fused_model_with_transforms(sample_stl_path):
    """Test building model with transforms applied."""
    result = await build_fused_model(
        content_hash="test_transforms",
        uploaded_stl_path=sample_stl_path,
        variant=0,
        hanger_tolerance=0.15,
        plate_units=1,
        plate_thickness=3,
        extend_bottom=0,
        offset_x=10,
        offset_y=20,
        offset_z=30,
        rotate_x=0,
        rotate_y=0,
        rotate_z=0,
    )

    assert result is not None
    assert len(result) > 0


@pytest.mark.asyncio
async def test_build_fused_model_missing_file():
    """Test that missing file is handled (OpenSCAD continues without the import)."""
    result = await build_fused_model(
        content_hash="test_missing",
        uploaded_stl_path="/nonexistent/path/file.stl",
        variant=0,
        hanger_tolerance=0.15,
        plate_units=1,
        plate_thickness=3,
        extend_bottom=0,
        offset_x=0,
        offset_y=0,
        offset_z=0,
        rotate_x=0,
        rotate_y=0,
        rotate_z=0,
    )

    assert result is not None
    assert len(result) > 0
    assert isinstance(result, bytes)


@pytest.mark.asyncio
async def test_build_fused_model_caching(sample_stl_path):
    """Test that build_fused_model uses caching."""
    result1 = await build_fused_model(
        content_hash="test_cache_a",
        uploaded_stl_path=sample_stl_path,
        variant=0,
        hanger_tolerance=0.15,
        plate_units=1,
        plate_thickness=3,
        extend_bottom=0,
        offset_x=0,
        offset_y=0,
        offset_z=0,
        rotate_x=0,
        rotate_y=0,
        rotate_z=0,
    )

    result2 = await build_fused_model(
        content_hash="test_cache_a",
        uploaded_stl_path=sample_stl_path,
        variant=0,
        hanger_tolerance=0.15,
        plate_units=1,
        plate_thickness=3,
        extend_bottom=0,
        offset_x=0,
        offset_y=0,
        offset_z=0,
        rotate_x=0,
        rotate_y=0,
        rotate_z=0,
    )

    assert result1 is result2


@pytest.mark.asyncio
async def test_build_fused_model_different_params_bypass_cache(sample_stl_path):
    """Test that different parameters bypass cache."""
    result1 = await build_fused_model(
        content_hash="test_diff_1",
        uploaded_stl_path=sample_stl_path,
        variant=0,
        hanger_tolerance=0.15,
        plate_units=1,
        plate_thickness=3,
        extend_bottom=0,
        offset_x=0,
        offset_y=0,
        offset_z=0,
        rotate_x=0,
        rotate_y=0,
        rotate_z=0,
    )

    result2 = await build_fused_model(
        content_hash="test_diff_2",
        uploaded_stl_path=sample_stl_path,
        variant=0,
        hanger_tolerance=0.15,
        plate_units=2,  # Different units
        plate_thickness=3,
        extend_bottom=0,
        offset_x=0,
        offset_y=0,
        offset_z=0,
        rotate_x=0,
        rotate_y=0,
        rotate_z=0,
    )

    assert result1 != result2
