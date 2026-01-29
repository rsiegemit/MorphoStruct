"""
Perfusable vascular network generator for thick tissue engineering.

Creates branching vascular trees following Murray's law for optimal perfusion.
Designed for thick tissue constructs requiring internal vascularization.

Features:
- Murray's law branching: r_parent³ = Σ r_child³
- Configurable branch generations
- Arterial, venous, and capillary network types
- Optimized for tissue perfusion applications
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from typing import Literal, Optional, List, Tuple
from ..core import batch_union


@dataclass
class PerfusableNetworkParams:
    """Parameters for perfusable vascular network generation."""
    inlet_diameter_mm: float = 1.5  # 1.5mm default (reduced from 2.0)
    branch_generations: int = 2  # Number of branching levels (reduced from 3)
    murray_ratio: float = 0.79  # Murray's law ratio (child/parent radius)
    network_type: Literal['arterial', 'venous', 'capillary'] = 'arterial'
    bounding_box_mm: tuple[float, float, float] = (6.0, 6.0, 6.0)  # Reduced from 10.0, 10.0, 10.0
    branching_angle_deg: float = 30.0  # Angle between parent and child branches
    resolution: int = 8  # Reduced from 12


def make_vessel_segment(
    p1: np.ndarray,
    p2: np.ndarray,
    r1: float,
    r2: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a tapered cylindrical vessel segment.

    Args:
        p1: Starting point (x, y, z)
        p2: Ending point (x, y, z)
        r1: Radius at start point
        r2: Radius at end point
        resolution: Number of segments around cylinder

    Returns:
        Manifold representing the vessel segment
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 1e-6:
        return m3d.Manifold()

    # Create cylinder along Z axis
    # manifold3d cylinder(height, bottom_radius, top_radius)
    vessel = m3d.Manifold.cylinder(length, r1, r2, resolution)

    # Calculate rotation to align with direction vector
    h = np.sqrt(dx*dx + dy*dy)  # horizontal distance

    if h > 0.001 or abs(dz) > 0.001:
        # Rotate to align with direction
        angle_y = np.arctan2(h, dz) * 180 / np.pi
        angle_z = np.arctan2(dy, dx) * 180 / np.pi

        vessel = vessel.rotate([0, angle_y, 0])
        vessel = vessel.rotate([0, 0, angle_z])

    return vessel.translate([p1[0], p1[1], p1[2]])


def calculate_child_radius(parent_radius: float, num_children: int, murray_ratio: float) -> float:
    """
    Calculate child vessel radius using Murray's law.

    Murray's law: r_parent³ = Σ r_child³
    For symmetric branching: r_parent³ = n * r_child³
    Therefore: r_child = r_parent / (n^(1/3))

    Args:
        parent_radius: Radius of parent vessel
        num_children: Number of child branches
        murray_ratio: Ratio override (typically 0.79 for biological vessels)

    Returns:
        Radius for each child vessel
    """
    # Use murray_ratio directly (empirical optimal value)
    # This accounts for non-ideal biological branching
    return parent_radius * murray_ratio


def create_branch_recursive(
    position: np.ndarray,
    direction: np.ndarray,
    radius: float,
    generation: int,
    max_generations: int,
    params: PerfusableNetworkParams,
    bounding_box: tuple[float, float, float],
    segments: List[m3d.Manifold],
    rng: np.random.Generator
) -> None:
    """
    Recursively generate branching vascular tree.

    Args:
        position: Current branch start position
        direction: Current branch direction (normalized)
        radius: Current branch radius
        generation: Current generation level
        max_generations: Maximum generation depth
        params: Network parameters
        bounding_box: Bounding box dimensions
        segments: List to append vessel segments to
        rng: Random number generator
    """
    # Termination conditions
    if generation >= max_generations or radius < 0.05:
        return

    # Calculate segment length based on generation
    # Earlier generations = longer segments
    base_length = bounding_box[2] / (max_generations * 1.5)
    segment_length = base_length * (1.5 - generation / max_generations)

    # Add some randomness to length (except first generation)
    if generation > 0:
        segment_length *= rng.uniform(0.7, 1.2)

    # Calculate end position
    end_position = position + direction * segment_length

    # Clamp to bounding box
    bbox_x, bbox_y, bbox_z = bounding_box
    end_position = np.clip(end_position, [-bbox_x/2, -bbox_y/2, -bbox_z/2],
                          [bbox_x/2, bbox_y/2, bbox_z/2])

    # Calculate child radius using Murray's law
    num_children = 2  # Binary branching
    child_radius = calculate_child_radius(radius, num_children, params.murray_ratio)

    # Create vessel segment
    segment = make_vessel_segment(
        position,
        end_position,
        radius,
        child_radius,
        params.resolution
    )

    if segment.num_vert() > 0:
        segments.append(segment)

        # Add junction sphere for smooth connection
        junction = m3d.Manifold.sphere(radius * 1.05, params.resolution)
        junction = junction.translate([end_position[0], end_position[1], end_position[2]])
        segments.append(junction)

    # Generate child branches if not at max generation
    if generation < max_generations - 1:
        # Calculate branching angles
        branching_angle = params.branching_angle_deg * np.pi / 180

        # Create two child branches at angles
        for i in range(num_children):
            # Rotate direction for child branch
            angle_offset = branching_angle if i == 0 else -branching_angle

            # Random rotation axis perpendicular to current direction
            perp_axis = np.array([
                rng.uniform(-1, 1),
                rng.uniform(-1, 1),
                0
            ])
            perp_axis = perp_axis / (np.linalg.norm(perp_axis) + 1e-6)

            # Rodrigues rotation formula
            k = perp_axis
            cos_theta = np.cos(angle_offset)
            sin_theta = np.sin(angle_offset)

            child_direction = (
                direction * cos_theta +
                np.cross(k, direction) * sin_theta +
                k * np.dot(k, direction) * (1 - cos_theta)
            )

            # Normalize
            child_direction = child_direction / (np.linalg.norm(child_direction) + 1e-6)

            # Recurse for child branch
            create_branch_recursive(
                end_position,
                child_direction,
                child_radius,
                generation + 1,
                max_generations,
                params,
                bounding_box,
                segments,
                rng
            )


def generate_perfusable_network(params: PerfusableNetworkParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a perfusable vascular network.

    Creates a branching tree structure following Murray's law for optimal
    fluid flow characteristics. Suitable for thick tissue engineering scaffolds.

    Args:
        params: PerfusableNetworkParams specifying network structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D vascular network geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, segment_count,
                     generation_count, network_type, scaffold_type

    Raises:
        ValueError: If no vessel segments are generated
    """
    # Initialize random generator for organic variation
    rng = np.random.default_rng(42)

    # Calculate inlet radius from diameter
    inlet_radius = params.inlet_diameter_mm / 2

    # Starting position (top center of bounding box)
    bbox_x, bbox_y, bbox_z = params.bounding_box_mm
    start_position = np.array([0.0, 0.0, bbox_z/2])

    # Starting direction (downward)
    start_direction = np.array([0.0, 0.0, -1.0])

    # Collect vessel segments
    segments: List[m3d.Manifold] = []

    # Create inlet sphere
    inlet_sphere = m3d.Manifold.sphere(inlet_radius, params.resolution)
    inlet_sphere = inlet_sphere.translate([start_position[0], start_position[1], start_position[2]])
    segments.append(inlet_sphere)

    # Generate branching tree
    create_branch_recursive(
        start_position,
        start_direction,
        inlet_radius,
        generation=0,
        max_generations=params.branch_generations,
        params=params,
        bounding_box=params.bounding_box_mm,
        segments=segments,
        rng=rng
    )

    if not segments:
        raise ValueError("No vessel segments generated")

    # Union all segments
    result = batch_union(segments)

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'segment_count': len(segments),
        'generation_count': params.branch_generations,
        'network_type': params.network_type,
        'scaffold_type': 'perfusable_network'
    }

    return result, stats


def generate_perfusable_network_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate perfusable network from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching PerfusableNetworkParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    # Handle bounding_box variations
    bbox = params.get('bounding_box_mm', params.get('bounding_box', (10.0, 10.0, 10.0)))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_perfusable_network(PerfusableNetworkParams(
        inlet_diameter_mm=params.get('inlet_diameter_mm', params.get('inlet_diameter', 1.5)),
        branch_generations=params.get('branch_generations', params.get('generations', 2)),
        murray_ratio=params.get('murray_ratio', 0.79),
        network_type=params.get('network_type', 'arterial'),
        bounding_box_mm=tuple(bbox) if bbox != (10.0, 10.0, 10.0) else (6.0, 6.0, 6.0),
        branching_angle_deg=params.get('branching_angle_deg', params.get('branching_angle', 30.0)),
        resolution=params.get('resolution', 8)
    ))
