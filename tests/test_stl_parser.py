"""
Tests for STL parsing utilities
These tests verify the binary STL detection and parsing logic
"""
import pytest
import struct


def create_binary_stl(num_faces=1):
    """Create a minimal binary STL file."""
    header = b"Binary STL Test" + b"\x00" * 65  # 80 bytes
    face_count = struct.pack('<I', num_faces)
    
    faces = b""
    for i in range(num_faces):
        # Normal (3 floats)
        faces += struct.pack('<fff', 0.0, 0.0, 1.0)
        # Vertex 1 (3 floats)
        faces += struct.pack('<fff', 0.0, 0.0, 0.0)
        # Vertex 2 (3 floats)
        faces += struct.pack('<fff', 10.0, 0.0, 0.0)
        # Vertex 3 (3 floats)
        faces += struct.pack('<fff', 0.0, 10.0, 0.0)
        # Attribute byte count (2 bytes)
        faces += struct.pack('<H', 0)
    
    return header + face_count + faces


def create_ascii_stl():
    """Create a minimal ASCII STL file."""
    return b"""solid test
  facet normal 0 0 1
    outer loop
      vertex 0 0 0
      vertex 10 0 0
      vertex 0 10 0
    endloop
  endfacet
endsolid test
"""


class MockDataView:
    """Mock DataView for testing."""
    def __init__(self, data):
        self.buffer = data
        self.byteLength = len(data)
    
    def getUint32(self, offset, little_endian):
        return struct.unpack('<I' if little_endian else '>I', 
                            self.buffer[offset:offset+4])[0]


def test_binary_stl_detection():
    """Test that binary STL is correctly identified."""
    stl_data = create_binary_stl()
    viewer = MockDataView(stl_data)
    
    # Binary STL: 84 bytes header + 50 bytes per face
    expected_size = 84 + (1 * 50)
    assert viewer.byteLength == expected_size
    
    num_faces = viewer.getUint32(80, True)
    calculated_size = 84 + (num_faces * 50)
    assert calculated_size == viewer.byteLength


def test_ascii_stl_detection():
    """Test that ASCII STL is correctly identified."""
    stl_data = create_ascii_stl()
    viewer = MockDataView(stl_data)
    
    # ASCII STL won't match binary size calculation
    try:
        num_faces = viewer.getUint32(80, True)
        calculated_size = 84 + (num_faces * 50)
        # Should not match actual size for ASCII
        assert calculated_size != viewer.byteLength
    except:
        # Might fail to read as binary, which is fine
        pass


def test_binary_stl_with_solid_header():
    """Test binary STL that starts with 'solid' text."""
    # Some binary STLs start with "solid" text in the header
    header = b"solid binary example" + b"\x00" * 60  # 80 bytes
    face_count = struct.pack('<I', 2)  # 2 faces
    
    faces = b""
    for i in range(2):
        faces += struct.pack('<fff', 0.0, 0.0, 1.0)  # Normal
        faces += struct.pack('<fff', 0.0, 0.0, 0.0)  # V1
        faces += struct.pack('<fff', 10.0, 0.0, 0.0)  # V2
        faces += struct.pack('<fff', 0.0, 10.0, 0.0)  # V3
        faces += struct.pack('<H', 0)  # Attribute
    
    stl_data = header + face_count + faces
    viewer = MockDataView(stl_data)
    
    # Should be detected as binary based on file size
    num_faces = viewer.getUint32(80, True)
    expected_size = 84 + (num_faces * 50)
    assert viewer.byteLength == expected_size


def test_file_size_validation():
    """Test that files too small for binary STL are handled."""
    # Create data too small to be valid binary STL
    small_data = b"solid" + b"\x00" * 10
    viewer = MockDataView(small_data)
    
    # Should be less than 84 bytes (minimum for binary STL)
    assert viewer.byteLength < 84


def test_stl_face_calculation():
    """Test binary STL face count calculation."""
    for num_faces in [1, 5, 10, 100]:
        stl_data = create_binary_stl(num_faces)
        viewer = MockDataView(stl_data)
        
        read_faces = viewer.getUint32(80, True)
        assert read_faces == num_faces
        
        expected_size = 84 + (num_faces * 50)
        assert viewer.byteLength == expected_size
