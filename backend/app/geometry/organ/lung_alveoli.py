"""
Lung alveoli scaffold generator.

Creates branching airway structures terminating in alveolar sacs:
- Recursive branching tree (dichotomous branching)
- Airways narrow with each generation
- Spherical alveoli at terminal branches (~200µm)
- Controlled branch generations and angles
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class LungAlveoliParams:
    """Parameters for lung alveoli scaffold generation."""
    branch_generations: int = 2  # 1-5 generations (reduced from 3, gives 4 terminal branches instead of 8)
    alveoli_diameter: float = 200.0  # µm, terminal sac size
    airway_diameter: float = 0.8  # mm (reduced from 1.0)
    branch_angle: float = 35.0  # degrees, angle between branches
    bounding_box: tuple[float, float, float] = (6.0, 6.0, 6.0)  # mm (reduced from 10x10x10)
    resolution: int = 8  # reduced from 12


class BranchNode:
    """Represents a node in the branching tree."""
    def __init__(self, position: np.ndarray, radius: float, generation: int):
        self.position = position
        self.radius = radius
        self.generation = generation
        self.children = []


def create_airway_segment(start: np.ndarray, end: np.ndarray, radius: float, resolution: int) -> m3d.Manifold:
    """
    Create an airway segment (cylinder) between two points.

    Args:
        start: Start position (x, y, z)
        end: End position (x, y, z)
        radius: Airway radius
        resolution: Number of segments around cylinder

    Returns:
        Airway cylinder manifold
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 1e-6:
        return m3d.Manifold()

    cyl = m3d.Manifold.cylinder(length, radius, radius, resolution)

    h = np.sqrt(dx*dx + dy*dy)
    if h > 0.001 or abs(dz) > 0.001:
        tilt = np.arctan2(h, dz) * 180 / np.pi
        azim = np.arctan2(dy, dx) * 180 / np.pi
        cyl = cyl.rotate([0, tilt, 0]).rotate([0, 0, azim])

    return cyl.translate([start[0], start[1], start[2]])


def create_alveolus(position: np.ndarray, radius: float, resolution: int) -> m3d.Manifold:
    """
    Create a spherical alveolus.

    Args:
        position: Center position (x, y, z)
        radius: Alveolus radius
        resolution: Sphere resolution

    Returns:
        Sphere manifold
    """
    sphere = m3d.Manifold.sphere(radius, resolution)
    return sphere.translate([position[0], position[1], position[2]])


def generate_branching_tree(root_pos: np.ndarray, root_radius: float, max_generations: int,
                            branch_angle: float, direction: np.ndarray) -> BranchNode:
    """
    Generate a recursive branching tree structure.

    Args:
        root_pos: Starting position
        root_radius: Starting radius
        max_generations: Maximum depth of branching
        branch_angle: Angle between branches (degrees)
        direction: Initial direction vector

    Returns:
        Root node of branching tree
    """
    root = BranchNode(root_pos, root_radius, 0)

    def build_branch(node: BranchNode, parent_dir: np.ndarray):
        if node.generation >= max_generations:
            return

        # Branch length decreases with generation
        length = root_radius * 3.0 * (0.7 ** node.generation)

        # Child radius (decreases with each generation)
        child_radius = node.radius * 0.7

        # Create two child branches
        angle_rad = np.radians(branch_angle)

        # Normalize parent direction
        parent_dir = parent_dir / (np.linalg.norm(parent_dir) + 1e-10)

        # Find perpendicular vector
        if abs(parent_dir[2]) < 0.9:
            perp = np.array([0, 0, 1])
        else:
            perp = np.array([1, 0, 0])

        right = np.cross(parent_dir, perp)
        right = right / (np.linalg.norm(right) + 1e-10)

        # Create two branches by rotating around 'right' axis
        for sign in [-1, 1]:
            # Rotate parent_dir around right axis by ±branch_angle
            cos_a, sin_a = np.cos(angle_rad * sign), np.sin(angle_rad * sign)

            # Use Rodrigues rotation formula
            child_dir = parent_dir * np.cos(angle_rad)
            child_dir += np.cross(right, parent_dir) * np.sin(angle_rad) * sign
            child_dir += right * np.dot(right, parent_dir) * (1 - np.cos(angle_rad))

            child_dir = child_dir / (np.linalg.norm(child_dir) + 1e-10)

            child_pos = node.position + child_dir * length
            child = BranchNode(child_pos, child_radius, node.generation + 1)
            node.children.append(child)

            build_branch(child, child_dir)

    build_branch(root, direction)
    return root


def collect_airways_and_alveoli(root: BranchNode, max_gen: int) -> tuple[list, list]:
    """
    Collect all airways and alveoli from branching tree.

    Args:
        root: Root node of tree
        max_gen: Maximum generation (for terminal detection)

    Returns:
        Tuple of (airway_segments, alveoli_positions)
        - airway_segments: List of (start, end, radius) tuples
        - alveoli_positions: List of (position, radius) tuples
    """
    airways = []
    alveoli = []

    def traverse(node: BranchNode):
        for child in node.children:
            # Add airway segment from node to child
            airways.append((node.position, child.position, child.radius))
            traverse(child)

        # Terminal node - add alveolus
        if node.generation == max_gen:
            alveoli.append((node.position, node.radius))

    traverse(root)
    return airways, alveoli


def generate_lung_alveoli(params: LungAlveoliParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a lung alveoli scaffold with branching airways.

    Args:
        params: LungAlveoliParams specifying geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, branch_count, alveoli_count, scaffold_type

    Raises:
        ValueError: If no geometry is generated
    """
    # Convert alveoli diameter from µm to mm
    alveoli_radius = params.alveoli_diameter / 2000.0
    airway_radius = params.airway_diameter / 2.0

    # Generate branching tree
    root_pos = np.array([0.0, 0.0, 0.0])
    initial_dir = np.array([0.0, 0.0, 1.0])

    root = generate_branching_tree(
        root_pos, airway_radius, params.branch_generations,
        params.branch_angle, initial_dir
    )

    # Collect airways and alveoli
    airway_segments, alveoli_positions = collect_airways_and_alveoli(root, params.branch_generations)

    # Create airway manifolds
    airway_manifolds = []
    for start, end, radius in airway_segments:
        seg = create_airway_segment(start, end, radius, params.resolution)
        if seg.num_vert() > 0:
            airway_manifolds.append(seg)

    # Create alveoli manifolds
    alveoli_manifolds = []
    for pos, radius in alveoli_positions:
        # Use fixed alveoli radius
        alv = create_alveolus(pos, alveoli_radius, params.resolution)
        if alv.num_vert() > 0:
            alveoli_manifolds.append(alv)

    all_parts = airway_manifolds + alveoli_manifolds

    if not all_parts:
        raise ValueError("No geometry generated")

    result = batch_union(all_parts)

    # Clip to bounding box
    bx, by, bz = params.bounding_box
    bbox = m3d.Manifold.cube([bx, by, bz])
    result = result ^ bbox

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'branch_count': len(airway_segments),
        'alveoli_count': len(alveoli_positions),
        'scaffold_type': 'lung_alveoli'
    }

    return result, stats


def generate_lung_alveoli_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate lung alveoli from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching LungAlveoliParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    # Handle bounding box variations
    bbox = params.get('bounding_box', (6.0, 6.0, 6.0))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_lung_alveoli(LungAlveoliParams(
        branch_generations=params.get('branch_generations', 2),
        alveoli_diameter=params.get('alveoli_diameter', 200.0),
        airway_diameter=params.get('airway_diameter', 0.8),
        branch_angle=params.get('branch_angle', 35.0),
        bounding_box=tuple(bbox),
        resolution=params.get('resolution', 8)
    ))
