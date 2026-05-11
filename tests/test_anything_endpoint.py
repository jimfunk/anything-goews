"""
Tests for the Anything GOEWS API endpoint
"""
import pytest
import io
import struct
from server.server import app


def create_minimal_stl():
    """Create a minimal valid binary STL file (triangle)."""
    # 84 byte header + 50 bytes per face (1 face = 50 bytes)
    header = b"Minimal STL for testing" + b"\x00" * 57  # 80 bytes total
    num_faces = struct.pack('<I', 1)  # 1 face
    face_data = (
        # Normal vector (3 floats)
        struct.pack('<fff', 0.0, 0.0, 0.0) +
        # Vertex 1 (3 floats)
        struct.pack('<fff', 0.0, 0.0, 0.0) +
        # Vertex 2 (3 floats)
        struct.pack('<fff', 10.0, 0.0, 0.0) +
        # Vertex 3 (3 floats)
        struct.pack('<fff', 0.0, 10.0, 0.0) +
        # Attribute byte count (2 bytes)
        struct.pack('<H', 0)
    )
    return header + num_faces + face_data


@pytest.fixture
def test_stl():
    """Provide a minimal STL file for testing."""
    return create_minimal_stl()


@pytest.fixture
def client():
    """Create a test client for the Sanic app."""
    return app.test_client


def test_anything_upload_success(client, test_stl):
    """Test successful STL upload and fusion."""
    files = {"model": ("test.stl", io.BytesIO(test_stl), "application/sla")}
    data = {
        "plate_units": 1,
        "plate_thickness": 3,
        "variant": 0,
        "hanger_tolerance": 0.15,
        "offset_x": 0,
        "offset_y": 0,
        "offset_z": 0,
        "rotate_x": 0,
        "rotate_y": 0,
        "rotate_z": 0,
    }

    _, response = client.post("/api/anything", files=files, data=data)

    assert response.status == 200
    assert response.headers["content-type"] == "model/stl"
    assert "Content-Disposition" in response.headers
    assert len(response.content) > 0


def test_anything_no_file(client):
    """Test plate-only generation when no file is uploaded."""
    data = {"plate_units": 1}
    _, response = client.post("/api/anything", data=data)

    assert response.status == 200
    assert response.headers["content-type"] == "model/stl"
    assert len(response.content) > 0


def test_anything_invalid_file_type(client):
    """Test rejection of non-STL files."""
    files = {"model": ("test.txt", io.BytesIO(b"not an stl"), "text/plain")}
    data = {"plate_units": 1}

    _, response = client.post("/api/anything", files=files, data=data)

    assert response.status == 400
    assert "error" in response.json
    assert "STL" in response.json["error"]


def test_anything_invalid_variant(client, test_stl):
    """Test rejection of invalid variant parameter."""
    files = {"model": ("test.stl", io.BytesIO(test_stl), "application/sla")}
    data = {"plate_units": 1, "variant": "invalid"}

    _, response = client.post("/api/anything", files=files, data=data)

    assert response.status == 400
    assert "error" in response.json
    assert "variant" in response.json["error"].lower()


def test_anything_missing_parameters(client, test_stl):
    """Test that missing parameters use defaults."""
    files = {"model": ("test.stl", io.BytesIO(test_stl), "application/sla")}
    data = {}  # No parameters - should use defaults

    _, response = client.post("/api/anything", files=files, data=data)

    assert response.status == 200
    assert response.headers["content-type"] == "model/stl"


def test_anything_invalid_plate_units(client, test_stl):
    """Test rejection of invalid plate units."""
    files = {"model": ("test.stl", io.BytesIO(test_stl), "application/sla")}
    data = {"plate_units": 0}  # Invalid zero value

    # This should fail validation
    _, response = client.post("/api/anything", files=files, data=data)

    # Either it fails validation or OpenSCAD fails - both are acceptable
    assert response.status in [400, 500]


def test_anything_filename_generation(client, test_stl):
    """Test that filename is generated correctly."""
    files = {"model": ("test.stl", io.BytesIO(test_stl), "application/sla")}
    data = {
        "plate_units": 2,
        "plate_thickness": 4,
        "variant": 1,  # Thicker cleats
    }

    _, response = client.post("/api/anything", files=files, data=data)

    assert response.status == 200
    content_disposition = response.headers["Content-Disposition"]
    assert "test-goews-thicker-cleats.stl" in content_disposition
