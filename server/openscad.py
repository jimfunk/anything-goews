import asyncio
from async_lru import alru_cache
import logging
from pathlib import Path
import os


logger = logging.getLogger("openscad")


top_dir = (Path(__file__) / "../..").resolve()
openscad_dir = top_dir / "openscad"

# Configuration constants
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 100 * 1024 * 1024))  # Default 100MB
MAX_CONCURRENT_PROCESSES = 32


class OpenSCADError(Exception):
    pass


# Allow up to 32 processes at once
process_semaphore = asyncio.Semaphore(MAX_CONCURRENT_PROCESSES)


@alru_cache(maxsize=256)
async def build_fused_model(
    content_hash: str,
    uploaded_stl_path: str,
    variant: int,
    hanger_tolerance: float,
    plate_units: int,
    plate_thickness: float,
    extend_bottom: float,
    offset_x: float,
    offset_y: float,
    offset_z: float,
    rotate_x: float,
    rotate_y: float,
    rotate_z: float,
) -> bytes:
    """Build a fused model combining uploaded STL with GOEWS mounting plate."""
    
    cmd = [
        "openscad",
        "--backend",
        "manifold",
        str(openscad_dir / "anything.scad"),
        "-o",
        "-",
        "--export-format",
        "stl",
    ]
    
    # Add parameters
    params = {
        "model_path": uploaded_stl_path,
        "variant": variant,
        "hanger_tolerance": hanger_tolerance,
        "hanger_units": plate_units,
        "plate_thickness": plate_thickness,
        "extend_bottom": extend_bottom,
        "offset_x": offset_x,
        "offset_y": offset_y,
        "offset_z": offset_z,
        "rotate_x": rotate_x,
        "rotate_y": rotate_y,
        "rotate_z": rotate_z,
    }
    
    for name, value in params.items():
        if value is not None:
            if isinstance(value, str):
                # Escape quotes in paths
                escaped_value = value.replace('"', '\\"')
                cmd += ["-D", f'{name}="{escaped_value}"']
            elif isinstance(value, bool):
                cmd += ["-D", f'{name}={str(value).lower()}']
            else:
                cmd += ["-D", f"{name}={value}"]

    async with process_semaphore:
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
        except asyncio.CancelledError:
            proc.kill()
            raise
        except Exception:
            proc.kill()
            logger.exception("Got exception running openscad")
            raise OpenSCADError("Model generation failed")

    if proc.returncode != 0:
        logger.error(f"OpenSCAD build failed: {stderr.decode()}")
        raise OpenSCADError("Model generation failed")

    return stdout

