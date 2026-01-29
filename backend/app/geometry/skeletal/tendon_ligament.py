"""
Tendon/ligament scaffold generator with aligned parallel fiber bundles.

Creates a structure with aligned parallel fibers exhibiting characteristic
crimped (sinusoidal) patterns typical of tendon and ligament tissue.
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class TendonLigamentParams:
    """Parameters for tendon/ligament scaffold generation."""
    fiber_diameter: float = 0.15
    fiber_spacing: float = 0.4
    crimp_amplitude: float = 0.3
    crimp_wavelength: float = 2.0
    bundle_count: int = 5
    length: float = 20.0
    width: float = 5.0
    thickness: float = 2.0
    resolution: int = 12


def generate_tendon_ligament(params: TendonLigamentParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a tendon/ligament scaffold with aligned crimped fibers.

    Creates parallel fiber bundles with sinusoidal crimp pattern:
    - Fibers aligned along length direction
    - Crimp amplitude creates characteristic wave pattern
    - Multiple bundles organized in parallel

    Args:
        params: TendonLigamentParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, fiber_count,
                     bundle_count, scaffold_type
    """
    fiber_radius = params.fiber_diameter / 2
    all_fibers = []

    # Calculate fiber distribution
    fibers_per_bundle = max(2, int((params.width * params.thickness) / (params.fiber_spacing ** 2)))

    for bundle_idx in range(params.bundle_count):
        # Bundle position (stacked vertically or side-by-side)
        if params.bundle_count > 1:
            bundle_offset_y = (bundle_idx - (params.bundle_count - 1) / 2) * (params.width / params.bundle_count)
        else:
            bundle_offset_y = 0

        # Create fibers in this bundle
        bundle_fibers = create_crimped_fiber_bundle(
            length=params.length,
            width=params.width / params.bundle_count,
            thickness=params.thickness,
            fiber_radius=fiber_radius,
            fiber_spacing=params.fiber_spacing,
            crimp_amplitude=params.crimp_amplitude,
            crimp_wavelength=params.crimp_wavelength,
            fibers_per_bundle=fibers_per_bundle,
            bundle_offset_y=bundle_offset_y,
            resolution=params.resolution
        )
        all_fibers.extend(bundle_fibers)

    if not all_fibers:
        raise ValueError("No fibers generated")

    # Union all fibers
    result = batch_union(all_fibers)

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'fiber_count': len(all_fibers),
        'bundle_count': params.bundle_count,
        'scaffold_type': 'tendon_ligament'
    }

    return result, stats


def create_crimped_fiber_bundle(
    length: float,
    width: float,
    thickness: float,
    fiber_radius: float,
    fiber_spacing: float,
    crimp_amplitude: float,
    crimp_wavelength: float,
    fibers_per_bundle: int,
    bundle_offset_y: float,
    resolution: int
) -> list[m3d.Manifold]:
    """
    Create a bundle of crimped parallel fibers.

    Args:
        length: Length along fiber direction (X axis)
        width: Width of bundle (Y axis)
        thickness: Thickness of bundle (Z axis)
        fiber_radius: Radius of individual fibers
        fiber_spacing: Spacing between fiber centers
        crimp_amplitude: Amplitude of sinusoidal crimp
        crimp_wavelength: Wavelength of crimp pattern
        fibers_per_bundle: Number of fibers in this bundle
        bundle_offset_y: Y-axis offset for this bundle
        resolution: Angular and path resolution

    Returns:
        List of crimped fiber manifolds
    """
    fibers = []

    # Distribute fibers in cross-section
    n_width = max(1, int(width / fiber_spacing))
    n_thickness = max(1, int(thickness / fiber_spacing))

    fiber_idx = 0
    for i in range(n_width):
        for j in range(n_thickness):
            if fiber_idx >= fibers_per_bundle:
                break

            # Fiber position in cross-section
            y_pos = bundle_offset_y + (i - (n_width - 1) / 2) * fiber_spacing
            z_pos = (j - (n_thickness - 1) / 2) * fiber_spacing

            # Add slight random offset for natural appearance
            y_pos += (np.random.random() - 0.5) * fiber_spacing * 0.2
            z_pos += (np.random.random() - 0.5) * fiber_spacing * 0.2

            # Create crimped fiber path
            fiber = create_crimped_fiber(
                length=length,
                y_base=y_pos,
                z_base=z_pos,
                radius=fiber_radius,
                crimp_amplitude=crimp_amplitude,
                crimp_wavelength=crimp_wavelength,
                resolution=resolution
            )

            if fiber.num_vert() > 0:
                fibers.append(fiber)
                fiber_idx += 1

    return fibers


def create_crimped_fiber(
    length: float,
    y_base: float,
    z_base: float,
    radius: float,
    crimp_amplitude: float,
    crimp_wavelength: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a single crimped fiber following sinusoidal path.

    Args:
        length: Total length of fiber
        y_base: Base Y position
        z_base: Base Z position (crimp oscillates in Z direction)
        radius: Fiber radius
        crimp_amplitude: Amplitude of sine wave
        crimp_wavelength: Wavelength of crimp
        resolution: Number of segments for smooth curve

    Returns:
        Manifold representing crimped fiber
    """
    # Number of segments along length
    n_segments = max(10, int(length / (crimp_wavelength / 4)))

    # Generate path points
    path_points = []
    for i in range(n_segments + 1):
        x = (i / n_segments) * length
        # Sinusoidal crimp in Z direction
        z = z_base + crimp_amplitude * np.sin(2 * np.pi * x / crimp_wavelength)
        path_points.append(np.array([x, y_base, z]))

    # Create cylinders between consecutive points
    segments = []
    for i in range(len(path_points) - 1):
        p1 = path_points[i]
        p2 = path_points[i + 1]

        segment = make_segment(p1, p2, radius, resolution)
        if segment.num_vert() > 0:
            segments.append(segment)

    # Union all segments
    if not segments:
        return m3d.Manifold()

    if len(segments) == 1:
        return segments[0]

    result = segments[0]
    for seg in segments[1:]:
        result = result + seg

    return result


def make_segment(p1: np.ndarray, p2: np.ndarray, radius: float, resolution: int) -> m3d.Manifold:
    """
    Create a cylindrical segment between two points.

    Args:
        p1: Starting point (x, y, z)
        p2: Ending point (x, y, z)
        radius: Segment radius
        resolution: Number of segments around cylinder

    Returns:
        Manifold representing the segment cylinder
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 1e-6:
        return m3d.Manifold()

    # Create cylinder along Z axis
    segment = m3d.Manifold.cylinder(length, radius, radius, resolution)

    # Calculate rotation to align with direction vector
    h = np.sqrt(dx*dx + dy*dy)
    if h > 0.001 or abs(dz) > 0.001:
        angle_y = np.arctan2(h, dz) * 180 / np.pi
        angle_z = np.arctan2(dy, dx) * 180 / np.pi

        segment = segment.rotate([0, angle_y, 0])
        segment = segment.rotate([0, 0, angle_z])

    return segment.translate([p1[0], p1[1], p1[2]])


def generate_tendon_ligament_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate tendon/ligament from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching TendonLigamentParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_tendon_ligament(TendonLigamentParams(
        fiber_diameter=params.get('fiber_diameter', 0.15),
        fiber_spacing=params.get('fiber_spacing', 0.4),
        crimp_amplitude=params.get('crimp_amplitude', 0.3),
        crimp_wavelength=params.get('crimp_wavelength', 2.0),
        bundle_count=params.get('bundle_count', 5),
        length=params.get('length', 20.0),
        width=params.get('width', 5.0),
        thickness=params.get('thickness', 2.0),
        resolution=params.get('resolution', 12)
    ))
