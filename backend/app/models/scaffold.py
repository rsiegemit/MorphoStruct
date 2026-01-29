"""
Type definitions for SHED scaffold generation.
Synchronized with frontend TypeScript types.
"""

from enum import Enum
from typing import Literal, Optional, Union, Dict, List, Any
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums
# ============================================================================


class ScaffoldType(str, Enum):
    """Supported scaffold types."""

    # Existing (5)
    VASCULAR_NETWORK = "vascular_network"
    POROUS_DISC = "porous_disc"
    TUBULAR_CONDUIT = "tubular_conduit"
    LATTICE = "lattice"
    PRIMITIVE = "primitive"

    # Skeletal (7)
    TRABECULAR_BONE = "trabecular_bone"
    OSTEOCHONDRAL = "osteochondral"
    ARTICULAR_CARTILAGE = "articular_cartilage"
    MENISCUS = "meniscus"
    TENDON_LIGAMENT = "tendon_ligament"
    INTERVERTEBRAL_DISC = "intervertebral_disc"
    HAVERSIAN_BONE = "haversian_bone"

    # Organ (6)
    HEPATIC_LOBULE = "hepatic_lobule"
    CARDIAC_PATCH = "cardiac_patch"
    KIDNEY_TUBULE = "kidney_tubule"
    LUNG_ALVEOLI = "lung_alveoli"
    PANCREATIC_ISLET = "pancreatic_islet"
    LIVER_SINUSOID = "liver_sinusoid"

    # Soft Tissue (4)
    MULTILAYER_SKIN = "multilayer_skin"
    SKELETAL_MUSCLE = "skeletal_muscle"
    CORNEA = "cornea"
    ADIPOSE = "adipose"

    # Tubular (5)
    BLOOD_VESSEL = "blood_vessel"
    NERVE_CONDUIT = "nerve_conduit"
    SPINAL_CORD = "spinal_cord"
    BLADDER = "bladder"
    TRACHEA = "trachea"

    # Dental (3)
    DENTIN_PULP = "dentin_pulp"
    EAR_AURICLE = "ear_auricle"
    NASAL_SEPTUM = "nasal_septum"

    # Advanced Lattice (5)
    GYROID = "gyroid"
    SCHWARZ_P = "schwarz_p"
    OCTET_TRUSS = "octet_truss"
    VORONOI = "voronoi"
    HONEYCOMB = "honeycomb"

    # Microfluidic (3)
    ORGAN_ON_CHIP = "organ_on_chip"
    GRADIENT_SCAFFOLD = "gradient_scaffold"
    PERFUSABLE_NETWORK = "perfusable_network"


class PorePattern(str, Enum):
    """Pore arrangement patterns for porous discs."""

    HEXAGONAL = "hexagonal"
    GRID = "grid"


class InnerTexture(str, Enum):
    """Inner surface texture types for tubular conduits."""

    SMOOTH = "smooth"
    GROOVED = "grooved"
    POROUS = "porous"


class UnitCell(str, Enum):
    """Lattice unit cell types."""

    CUBIC = "cubic"
    BCC = "bcc"


class PrimitiveShape(str, Enum):
    """Primitive shape types."""

    CYLINDER = "cylinder"
    SPHERE = "sphere"
    BOX = "box"
    CONE = "cone"


class ModificationOperation(str, Enum):
    """Modification operations for primitive shapes."""

    HOLE = "hole"
    SHELL = "shell"


class GradientType(str, Enum):
    """Gradient function types."""

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    SIGMOID = "sigmoid"


class ArchitectureType(str, Enum):
    """Muscle architecture types."""

    PARALLEL = "parallel"
    UNIPENNATE = "unipennate"
    BIPENNATE = "bipennate"


class OsteonPattern(str, Enum):
    """Osteon arrangement patterns for Haversian bone."""

    HEXAGONAL = "hexagonal"
    RANDOM = "random"


class CurveType(str, Enum):
    """Curve types for nasal septum."""

    SINGLE = "single"
    S_CURVE = "s_curve"


class NetworkType(str, Enum):
    """Vascular network types."""

    ARTERIAL = "arterial"
    VENOUS = "venous"
    CAPILLARY = "capillary"


# ============================================================================
# Base Parameters
# ============================================================================


class BaseParams(BaseModel):
    """Base parameters shared by all scaffold types."""

    resolution: int = Field(
        default=16,
        ge=6,
        le=32,
        description="Mesh resolution (6-32, default 16)",
    )


# ============================================================================
# Original Type-Specific Parameters
# ============================================================================


class VascularNetworkParams(BaseParams):
    """Parameters for vascular network scaffold."""

    type: Literal[ScaffoldType.VASCULAR_NETWORK] = ScaffoldType.VASCULAR_NETWORK

    inlets: int = Field(
        default=4, ge=1, le=25, description="Number of inlet branches (1-25)"
    )
    levels: int = Field(default=3, ge=0, le=8, description="Branching levels (0-8)")
    splits: int = Field(
        default=2, ge=1, le=6, description="Splits per branch (1-6)"
    )
    spread: float = Field(
        default=0.5, ge=0.1, le=0.8, description="Branch spread angle (0.1-0.8)"
    )
    ratio: float = Field(
        default=0.79,
        ge=0.5,
        le=0.95,
        description="Branch radius ratio (0.5-0.95, Murray's law = 0.79)",
    )
    curvature: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Branch curvature (0-1)"
    )
    tips_down: bool = Field(default=True, description="Tips point downward")
    deterministic: bool = Field(
        default=False, description="Use deterministic branching"
    )
    outer_radius_mm: float = Field(
        default=10.0, gt=0, description="Outer cylinder radius (mm)"
    )
    height_mm: float = Field(default=5.0, gt=0, description="Total height (mm)")
    inlet_radius_mm: float = Field(
        default=1.0, gt=0, description="Inlet branch radius (mm)"
    )
    seed: Optional[int] = Field(default=None, description="Random seed (optional)")

    @field_validator("inlet_radius_mm")
    @classmethod
    def validate_inlet_radius(cls, v: float, info) -> float:
        """Ensure inlet radius is smaller than outer radius."""
        outer_radius = info.data.get("outer_radius_mm")
        if outer_radius and v >= outer_radius:
            raise ValueError("inlet_radius_mm must be less than outer_radius_mm")
        return v


class PorousDiscParams(BaseParams):
    """Parameters for porous disc scaffold."""

    type: Literal[ScaffoldType.POROUS_DISC] = ScaffoldType.POROUS_DISC

    diameter_mm: float = Field(
        default=10.0, ge=1.0, le=50.0, description="Disc diameter (mm, 1-50)"
    )
    height_mm: float = Field(
        default=2.0, ge=0.5, le=10.0, description="Disc height (mm, 0.5-10)"
    )
    pore_diameter_um: float = Field(
        default=200.0, ge=50.0, le=500.0, description="Pore diameter (um, 50-500)"
    )
    pore_spacing_um: float = Field(
        default=400.0, ge=100.0, le=1000.0, description="Pore spacing (um, 100-1000)"
    )
    pore_pattern: PorePattern = Field(
        default=PorePattern.HEXAGONAL, description="Pore arrangement pattern"
    )
    porosity_target: Optional[float] = Field(
        default=0.5, ge=0.2, le=0.8, description="Target porosity (0.2-0.8, optional)"
    )

    @field_validator("pore_spacing_um")
    @classmethod
    def validate_pore_spacing(cls, v: float, info) -> float:
        """Ensure pore spacing is greater than pore diameter."""
        pore_diameter = info.data.get("pore_diameter_um")
        if pore_diameter and v <= pore_diameter:
            raise ValueError("pore_spacing_um must be greater than pore_diameter_um")
        return v


class TubularConduitParams(BaseParams):
    """Parameters for tubular conduit scaffold."""

    type: Literal[ScaffoldType.TUBULAR_CONDUIT] = ScaffoldType.TUBULAR_CONDUIT

    outer_diameter_mm: float = Field(
        default=6.0, ge=1.0, le=20.0, description="Outer diameter (mm, 1-20)"
    )
    wall_thickness_mm: float = Field(
        default=1.0, ge=0.3, le=5.0, description="Wall thickness (mm, 0.3-5)"
    )
    length_mm: float = Field(
        default=20.0, ge=1.0, le=100.0, description="Total length (mm, 1-100)"
    )
    inner_texture: Optional[InnerTexture] = Field(
        default=InnerTexture.SMOOTH, description="Inner surface texture (optional)"
    )
    groove_count: Optional[int] = Field(
        default=None,
        ge=2,
        le=32,
        description="Groove count (optional, required if inner_texture = 'grooved')",
    )

    @field_validator("wall_thickness_mm")
    @classmethod
    def validate_wall_thickness(cls, v: float, info) -> float:
        """Ensure wall thickness is less than outer radius."""
        outer_diameter = info.data.get("outer_diameter_mm")
        if outer_diameter and v >= outer_diameter / 2:
            raise ValueError("wall_thickness_mm must be less than outer_diameter_mm/2")
        return v

    @field_validator("groove_count")
    @classmethod
    def validate_groove_count(cls, v: Optional[int], info) -> Optional[int]:
        """Require groove_count if inner_texture is 'grooved'."""
        inner_texture = info.data.get("inner_texture")
        if inner_texture == InnerTexture.GROOVED and v is None:
            raise ValueError("groove_count is required when inner_texture is 'grooved'")
        return v


class BoundingBoxDimensions(BaseModel):
    """Bounding box dimensions in millimeters."""

    x: float = Field(gt=0, description="X dimension (mm)")
    y: float = Field(gt=0, description="Y dimension (mm)")
    z: float = Field(gt=0, description="Z dimension (mm)")


class LatticeParams(BaseParams):
    """Parameters for lattice scaffold."""

    type: Literal[ScaffoldType.LATTICE] = ScaffoldType.LATTICE

    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=10),
        description="Bounding box dimensions (mm)",
    )
    unit_cell: UnitCell = Field(
        default=UnitCell.CUBIC, description="Lattice unit cell type"
    )
    cell_size_mm: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Unit cell size (mm, 0.5-5)"
    )
    strut_diameter_mm: float = Field(
        default=0.5, ge=0.2, le=1.0, description="Strut diameter (mm, 0.2-1)"
    )

    @field_validator("strut_diameter_mm")
    @classmethod
    def validate_strut_diameter(cls, v: float, info) -> float:
        """Ensure strut diameter is less than cell size."""
        cell_size = info.data.get("cell_size_mm")
        if cell_size and v >= cell_size:
            raise ValueError("strut_diameter_mm must be less than cell_size_mm")
        return v


class PrimitiveModification(BaseModel):
    """Modification to apply to primitive shape."""

    operation: ModificationOperation = Field(description="Modification operation type")
    params: Dict[str, float] = Field(description="Operation-specific parameters")


class PrimitiveParams(BaseParams):
    """Parameters for primitive shape scaffold."""

    type: Literal[ScaffoldType.PRIMITIVE] = ScaffoldType.PRIMITIVE

    shape: PrimitiveShape = Field(description="Primitive shape type")
    dimensions: Dict[str, float] = Field(description="Shape-specific dimensions")
    modifications: Optional[List[PrimitiveModification]] = Field(
        default=None, description="Optional modifications (holes, shells)"
    )


# ============================================================================
# Skeletal Tissue Parameters (7 types)
# ============================================================================


class TrabecularBoneParams(BaseParams):
    """Parameters for trabecular bone scaffold."""

    type: Literal[ScaffoldType.TRABECULAR_BONE] = ScaffoldType.TRABECULAR_BONE

    porosity: float = Field(
        default=0.7, ge=0.3, le=0.9, description="Target porosity (0.3-0.9)"
    )
    pore_size_um: float = Field(
        default=400.0, ge=100.0, le=800.0, description="Pore size (um, 100-800)"
    )
    strut_thickness_um: float = Field(
        default=200.0, ge=50.0, le=500.0, description="Strut thickness (um, 50-500)"
    )
    anisotropy_ratio: float = Field(
        default=1.5, ge=1.0, le=3.0, description="Anisotropy ratio (1-3)"
    )
    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=10),
        description="Bounding box dimensions (mm)",
    )
    seed: int = Field(default=42, description="Random seed for reproducibility")


class OsteochondralParams(BaseParams):
    """Parameters for osteochondral scaffold."""

    type: Literal[ScaffoldType.OSTEOCHONDRAL] = ScaffoldType.OSTEOCHONDRAL

    bone_depth: float = Field(
        default=3.0, ge=1.0, le=10.0, description="Bone zone depth (mm)"
    )
    cartilage_depth: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Cartilage zone depth (mm)"
    )
    transition_width: float = Field(
        default=1.0, ge=0.5, le=3.0, description="Transition zone width (mm)"
    )
    gradient_type: GradientType = Field(
        default=GradientType.LINEAR, description="Gradient function type"
    )
    diameter: float = Field(
        default=8.0, ge=3.0, le=20.0, description="Scaffold diameter (mm)"
    )
    bone_porosity: float = Field(
        default=0.7, ge=0.4, le=0.9, description="Bone zone porosity"
    )
    cartilage_porosity: float = Field(
        default=0.85, ge=0.5, le=0.95, description="Cartilage zone porosity"
    )


class ArticularCartilageParams(BaseParams):
    """Parameters for articular cartilage scaffold."""

    type: Literal[ScaffoldType.ARTICULAR_CARTILAGE] = ScaffoldType.ARTICULAR_CARTILAGE

    total_thickness: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Total thickness (mm)"
    )
    zone_ratios: List[float] = Field(
        default=[0.2, 0.4, 0.4],
        description="Zone ratios [superficial, middle, deep]",
    )
    pore_gradient: List[float] = Field(
        default=[0.15, 0.25, 0.35],
        description="Pore radius per zone (mm)",
    )
    diameter: float = Field(
        default=8.0, ge=3.0, le=20.0, description="Scaffold diameter (mm)"
    )


class MeniscusParams(BaseParams):
    """Parameters for meniscus scaffold."""

    type: Literal[ScaffoldType.MENISCUS] = ScaffoldType.MENISCUS

    inner_radius: float = Field(
        default=12.0, ge=5.0, le=25.0, description="Inner radius (mm)"
    )
    outer_radius: float = Field(
        default=20.0, ge=10.0, le=35.0, description="Outer radius (mm)"
    )
    height: float = Field(
        default=8.0, ge=3.0, le=15.0, description="Height (mm)"
    )
    wedge_angle_deg: float = Field(
        default=20.0, ge=10.0, le=40.0, description="Wedge angle (degrees)"
    )
    zone_count: int = Field(
        default=3, ge=2, le=5, description="Number of radial zones"
    )
    fiber_diameter: float = Field(
        default=0.2, ge=0.1, le=0.5, description="Fiber diameter (mm)"
    )
    arc_degrees: float = Field(
        default=300.0, ge=180.0, le=360.0, description="Arc extent (degrees)"
    )


class TendonLigamentParams(BaseParams):
    """Parameters for tendon/ligament scaffold."""

    type: Literal[ScaffoldType.TENDON_LIGAMENT] = ScaffoldType.TENDON_LIGAMENT

    fiber_diameter: float = Field(
        default=0.15, ge=0.05, le=0.5, description="Fiber diameter (mm)"
    )
    fiber_spacing: float = Field(
        default=0.4, ge=0.1, le=1.0, description="Fiber spacing (mm)"
    )
    crimp_amplitude: float = Field(
        default=0.3, ge=0.1, le=1.0, description="Crimp amplitude (mm)"
    )
    crimp_wavelength: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Crimp wavelength (mm)"
    )
    bundle_count: int = Field(
        default=5, ge=1, le=10, description="Number of fiber bundles"
    )
    length: float = Field(
        default=20.0, ge=5.0, le=50.0, description="Length (mm)"
    )
    width: float = Field(
        default=5.0, ge=1.0, le=15.0, description="Width (mm)"
    )
    thickness: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Thickness (mm)"
    )


class IntervertebralDiscParams(BaseParams):
    """Parameters for intervertebral disc scaffold."""

    type: Literal[ScaffoldType.INTERVERTEBRAL_DISC] = ScaffoldType.INTERVERTEBRAL_DISC

    disc_diameter: float = Field(
        default=40.0, ge=20.0, le=60.0, description="Disc diameter (mm)"
    )
    disc_height: float = Field(
        default=10.0, ge=5.0, le=20.0, description="Disc height (mm)"
    )
    af_ring_count: int = Field(
        default=5, ge=3, le=10, description="Annulus fibrosus ring count"
    )
    np_diameter: float = Field(
        default=15.0, ge=5.0, le=25.0, description="Nucleus pulposus diameter (mm)"
    )
    af_layer_angle: float = Field(
        default=30.0, ge=15.0, le=45.0, description="AF fiber angle (degrees)"
    )
    fiber_diameter: float = Field(
        default=0.15, ge=0.05, le=0.3, description="Fiber diameter (mm)"
    )
    np_porosity: float = Field(
        default=0.9, ge=0.7, le=0.95, description="Nucleus pulposus porosity"
    )


class HaversianBoneParams(BaseParams):
    """Parameters for Haversian bone scaffold."""

    type: Literal[ScaffoldType.HAVERSIAN_BONE] = ScaffoldType.HAVERSIAN_BONE

    canal_diameter_um: float = Field(
        default=50.0, ge=20.0, le=100.0, description="Haversian canal diameter (um)"
    )
    canal_spacing_um: float = Field(
        default=250.0, ge=100.0, le=500.0, description="Canal spacing (um)"
    )
    cortical_thickness: float = Field(
        default=5.0, ge=2.0, le=10.0, description="Cortical thickness (mm)"
    )
    osteon_pattern: OsteonPattern = Field(
        default=OsteonPattern.HEXAGONAL, description="Osteon arrangement pattern"
    )
    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=15),
        description="Bounding box dimensions (mm)",
    )


# ============================================================================
# Organ Parameters (6 types)
# ============================================================================


class HepaticLobuleParams(BaseParams):
    """Parameters for hepatic lobule scaffold."""

    type: Literal[ScaffoldType.HEPATIC_LOBULE] = ScaffoldType.HEPATIC_LOBULE

    num_lobules: int = Field(
        default=1, ge=1, le=19, description="Number of lobules"
    )
    lobule_radius: float = Field(
        default=1.5, ge=0.5, le=3.0, description="Lobule radius (mm)"
    )
    lobule_height: float = Field(
        default=3.0, ge=1.0, le=6.0, description="Lobule height (mm)"
    )
    wall_thickness: float = Field(
        default=0.1, ge=0.05, le=0.3, description="Wall thickness (mm)"
    )
    central_vein_radius: float = Field(
        default=0.15, ge=0.05, le=0.3, description="Central vein radius (mm)"
    )
    portal_vein_radius: float = Field(
        default=0.12, ge=0.03, le=0.25, description="Portal vein radius (mm)"
    )
    show_sinusoids: bool = Field(
        default=False, description="Show sinusoidal channels"
    )
    sinusoid_radius: float = Field(
        default=0.025, ge=0.01, le=0.1, description="Sinusoid radius (mm)"
    )


class CardiacPatchParams(BaseParams):
    """Parameters for cardiac patch scaffold."""

    type: Literal[ScaffoldType.CARDIAC_PATCH] = ScaffoldType.CARDIAC_PATCH

    fiber_spacing: float = Field(
        default=300.0, ge=100.0, le=500.0, description="Fiber spacing (um)"
    )
    fiber_diameter: float = Field(
        default=100.0, ge=50.0, le=200.0, description="Fiber diameter (um)"
    )
    patch_size: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=1),
        description="Patch dimensions (mm)",
    )
    layer_count: int = Field(
        default=3, ge=1, le=10, description="Number of layers"
    )
    alignment_angle: float = Field(
        default=0.0, ge=-90.0, le=90.0, description="Alignment angle between layers (degrees)"
    )


class KidneyTubuleParams(BaseParams):
    """Parameters for kidney tubule scaffold."""

    type: Literal[ScaffoldType.KIDNEY_TUBULE] = ScaffoldType.KIDNEY_TUBULE

    tubule_diameter: float = Field(
        default=100.0, ge=50.0, le=200.0, description="Tubule diameter (um)"
    )
    wall_thickness: float = Field(
        default=15.0, ge=5.0, le=50.0, description="Wall thickness (um)"
    )
    convolution_amplitude: float = Field(
        default=500.0, ge=100.0, le=1000.0, description="Convolution amplitude (um)"
    )
    convolution_frequency: float = Field(
        default=3.0, ge=1.0, le=10.0, description="Convolution frequency"
    )
    length: float = Field(
        default=10.0, ge=5.0, le=30.0, description="Length (mm)"
    )


class LungAlveoliParams(BaseParams):
    """Parameters for lung alveoli scaffold."""

    type: Literal[ScaffoldType.LUNG_ALVEOLI] = ScaffoldType.LUNG_ALVEOLI

    branch_generations: int = Field(
        default=3, ge=1, le=5, description="Branching generations"
    )
    alveoli_diameter: float = Field(
        default=200.0, ge=100.0, le=400.0, description="Alveoli diameter (um)"
    )
    airway_diameter: float = Field(
        default=1.0, ge=0.3, le=3.0, description="Initial airway diameter (mm)"
    )
    branch_angle: float = Field(
        default=35.0, ge=20.0, le=60.0, description="Branch angle (degrees)"
    )
    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=10),
        description="Bounding box dimensions (mm)",
    )


class PancreaticIsletParams(BaseParams):
    """Parameters for pancreatic islet scaffold."""

    type: Literal[ScaffoldType.PANCREATIC_ISLET] = ScaffoldType.PANCREATIC_ISLET

    islet_diameter: float = Field(
        default=200.0, ge=100.0, le=300.0, description="Islet diameter (um)"
    )
    shell_thickness: float = Field(
        default=50.0, ge=20.0, le=100.0, description="Shell thickness (um)"
    )
    pore_size: float = Field(
        default=20.0, ge=5.0, le=50.0, description="Pore size (um)"
    )
    cluster_count: int = Field(
        default=7, ge=1, le=19, description="Number of islets in cluster"
    )
    spacing: float = Field(
        default=300.0, ge=150.0, le=500.0, description="Spacing between islets (um)"
    )


class LiverSinusoidParams(BaseParams):
    """Parameters for liver sinusoid scaffold."""

    type: Literal[ScaffoldType.LIVER_SINUSOID] = ScaffoldType.LIVER_SINUSOID

    sinusoid_diameter: float = Field(
        default=20.0, ge=10.0, le=30.0, description="Sinusoid diameter (um)"
    )
    length: float = Field(
        default=5.0, ge=1.0, le=15.0, description="Length (mm)"
    )
    fenestration_size: float = Field(
        default=1.0, ge=0.5, le=3.0, description="Fenestration size (um)"
    )
    fenestration_density: float = Field(
        default=0.2, ge=0.0, le=0.5, description="Fenestration density (0-0.5)"
    )


# ============================================================================
# Soft Tissue Parameters (4 types)
# ============================================================================


class MultilayerSkinParams(BaseParams):
    """Parameters for multilayer skin scaffold."""

    type: Literal[ScaffoldType.MULTILAYER_SKIN] = ScaffoldType.MULTILAYER_SKIN

    epidermis_thickness_mm: float = Field(
        default=0.15, ge=0.05, le=0.3, description="Epidermis thickness (mm)"
    )
    dermis_thickness_mm: float = Field(
        default=1.5, ge=0.5, le=3.0, description="Dermis thickness (mm)"
    )
    hypodermis_thickness_mm: float = Field(
        default=3.0, ge=1.0, le=6.0, description="Hypodermis thickness (mm)"
    )
    diameter_mm: float = Field(
        default=10.0, ge=5.0, le=30.0, description="Diameter (mm)"
    )
    pore_gradient: List[float] = Field(
        default=[0.3, 0.5, 0.7],
        description="Porosity gradient [epidermis, dermis, hypodermis]",
    )
    vascular_channel_diameter_mm: float = Field(
        default=0.2, ge=0.1, le=0.5, description="Vascular channel diameter (mm)"
    )
    vascular_channel_count: int = Field(
        default=8, ge=0, le=16, description="Number of vascular channels"
    )


class SkeletalMuscleParams(BaseParams):
    """Parameters for skeletal muscle scaffold."""

    type: Literal[ScaffoldType.SKELETAL_MUSCLE] = ScaffoldType.SKELETAL_MUSCLE

    fiber_diameter_um: float = Field(
        default=75.0, ge=50.0, le=150.0, description="Fiber diameter (um)"
    )
    fiber_spacing_um: float = Field(
        default=150.0, ge=75.0, le=300.0, description="Fiber spacing (um)"
    )
    pennation_angle_deg: float = Field(
        default=15.0, ge=0.0, le=45.0, description="Pennation angle (degrees)"
    )
    fascicle_count: int = Field(
        default=3, ge=1, le=10, description="Number of fascicles"
    )
    architecture_type: ArchitectureType = Field(
        default=ArchitectureType.PARALLEL, description="Muscle architecture type"
    )
    length_mm: float = Field(
        default=10.0, ge=5.0, le=30.0, description="Length (mm)"
    )
    width_mm: float = Field(
        default=5.0, ge=2.0, le=15.0, description="Width (mm)"
    )
    height_mm: float = Field(
        default=5.0, ge=2.0, le=15.0, description="Height (mm)"
    )


class CorneaParams(BaseParams):
    """Parameters for cornea scaffold."""

    type: Literal[ScaffoldType.CORNEA] = ScaffoldType.CORNEA

    diameter_mm: float = Field(
        default=11.0, ge=8.0, le=14.0, description="Diameter (mm)"
    )
    thickness_mm: float = Field(
        default=0.55, ge=0.3, le=1.0, description="Thickness (mm)"
    )
    radius_of_curvature_mm: float = Field(
        default=7.8, ge=6.0, le=10.0, description="Radius of curvature (mm)"
    )
    lamella_count: int = Field(
        default=5, ge=1, le=10, description="Number of lamella layers"
    )


class AdiposeParams(BaseParams):
    """Parameters for adipose tissue scaffold."""

    type: Literal[ScaffoldType.ADIPOSE] = ScaffoldType.ADIPOSE

    cell_size_um: float = Field(
        default=150.0, ge=100.0, le=200.0, description="Cell size (um)"
    )
    wall_thickness_um: float = Field(
        default=30.0, ge=10.0, le=50.0, description="Wall thickness (um)"
    )
    vascular_channel_spacing_mm: float = Field(
        default=2.0, ge=1.0, le=5.0, description="Vascular channel spacing (mm)"
    )
    vascular_channel_diameter_mm: float = Field(
        default=0.3, ge=0.1, le=0.5, description="Vascular channel diameter (mm)"
    )
    height_mm: float = Field(
        default=5.0, ge=2.0, le=15.0, description="Height (mm)"
    )
    diameter_mm: float = Field(
        default=10.0, ge=5.0, le=30.0, description="Diameter (mm)"
    )


# ============================================================================
# Tubular Organ Parameters (5 types)
# ============================================================================


class BloodVesselParams(BaseParams):
    """Parameters for blood vessel scaffold."""

    type: Literal[ScaffoldType.BLOOD_VESSEL] = ScaffoldType.BLOOD_VESSEL

    inner_diameter_mm: float = Field(
        default=5.0, ge=1.0, le=25.0, description="Inner diameter (mm)"
    )
    wall_thickness_mm: float = Field(
        default=1.0, ge=0.3, le=3.0, description="Wall thickness (mm)"
    )
    layer_ratios: List[float] = Field(
        default=[0.1, 0.5, 0.4],
        description="Layer ratios [intima, media, adventitia]",
    )
    length_mm: float = Field(
        default=30.0, ge=10.0, le=100.0, description="Length (mm)"
    )
    bifurcation_angle_deg: Optional[float] = Field(
        default=None, ge=20.0, le=90.0, description="Bifurcation angle (degrees, optional)"
    )


class NerveConduitParams(BaseParams):
    """Parameters for nerve conduit scaffold."""

    type: Literal[ScaffoldType.NERVE_CONDUIT] = ScaffoldType.NERVE_CONDUIT

    outer_diameter_mm: float = Field(
        default=4.0, ge=1.0, le=10.0, description="Outer diameter (mm)"
    )
    channel_count: int = Field(
        default=7, ge=1, le=19, description="Number of guidance channels"
    )
    channel_diameter_um: float = Field(
        default=200.0, ge=50.0, le=500.0, description="Channel diameter (um)"
    )
    wall_thickness_mm: float = Field(
        default=0.5, ge=0.2, le=1.5, description="Wall thickness (mm)"
    )
    length_mm: float = Field(
        default=20.0, ge=5.0, le=50.0, description="Length (mm)"
    )


class SpinalCordParams(BaseParams):
    """Parameters for spinal cord scaffold."""

    type: Literal[ScaffoldType.SPINAL_CORD] = ScaffoldType.SPINAL_CORD

    cord_diameter_mm: float = Field(
        default=12.0, ge=8.0, le=18.0, description="Cord diameter (mm)"
    )
    channel_diameter_um: float = Field(
        default=300.0, ge=100.0, le=500.0, description="White matter channel diameter (um)"
    )
    channel_count: int = Field(
        default=24, ge=8, le=48, description="Number of channels"
    )
    gray_matter_ratio: float = Field(
        default=0.4, ge=0.2, le=0.6, description="Gray matter ratio"
    )
    length_mm: float = Field(
        default=50.0, ge=20.0, le=100.0, description="Length (mm)"
    )


class BladderParams(BaseParams):
    """Parameters for bladder scaffold."""

    type: Literal[ScaffoldType.BLADDER] = ScaffoldType.BLADDER

    diameter_mm: float = Field(
        default=70.0, ge=30.0, le=120.0, description="Diameter (mm)"
    )
    wall_thickness_mm: float = Field(
        default=3.0, ge=1.0, le=6.0, description="Wall thickness (mm)"
    )
    layer_count: int = Field(
        default=3, ge=2, le=4, description="Number of layers"
    )
    dome_curvature: float = Field(
        default=0.7, ge=0.3, le=1.0, description="Dome curvature (0.5=hemisphere)"
    )


class TracheaParams(BaseParams):
    """Parameters for trachea scaffold."""

    type: Literal[ScaffoldType.TRACHEA] = ScaffoldType.TRACHEA

    outer_diameter_mm: float = Field(
        default=20.0, ge=10.0, le=30.0, description="Outer diameter (mm)"
    )
    ring_thickness_mm: float = Field(
        default=3.0, ge=1.0, le=5.0, description="Ring thickness (mm)"
    )
    ring_spacing_mm: float = Field(
        default=4.0, ge=2.0, le=8.0, description="Ring spacing (mm)"
    )
    ring_count: int = Field(
        default=10, ge=3, le=25, description="Number of rings"
    )
    length_mm: Optional[float] = Field(
        default=None, description="Length (mm, auto-calculated if None)"
    )
    posterior_gap_angle_deg: float = Field(
        default=90.0, ge=45.0, le=135.0, description="Posterior gap angle (degrees)"
    )


# ============================================================================
# Dental/Craniofacial Parameters (3 types)
# ============================================================================


class DentinPulpParams(BaseParams):
    """Parameters for dentin-pulp scaffold."""

    type: Literal[ScaffoldType.DENTIN_PULP] = ScaffoldType.DENTIN_PULP

    tooth_height: float = Field(
        default=12.0, ge=5.0, le=25.0, description="Tooth height (mm)"
    )
    crown_diameter: float = Field(
        default=10.0, ge=5.0, le=15.0, description="Crown diameter (mm)"
    )
    root_length: float = Field(
        default=12.0, ge=5.0, le=20.0, description="Root length (mm)"
    )
    root_diameter: float = Field(
        default=5.0, ge=2.0, le=8.0, description="Root diameter (mm)"
    )
    pulp_chamber_size: float = Field(
        default=0.4, ge=0.2, le=0.7, description="Pulp chamber size ratio (0-1)"
    )
    dentin_thickness: float = Field(
        default=3.0, ge=1.0, le=5.0, description="Dentin thickness (mm)"
    )


class EarAuricleParams(BaseParams):
    """Parameters for ear auricle scaffold."""

    type: Literal[ScaffoldType.EAR_AURICLE] = ScaffoldType.EAR_AURICLE

    scale_factor: float = Field(
        default=1.0, ge=0.5, le=1.5, description="Overall size multiplier"
    )
    thickness: float = Field(
        default=2.0, ge=1.0, le=4.0, description="Cartilage thickness (mm)"
    )
    helix_definition: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Helix rim prominence (0-1)"
    )
    antihelix_depth: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Antihelix ridge depth (0-1)"
    )


class NasalSeptumParams(BaseParams):
    """Parameters for nasal septum scaffold."""

    type: Literal[ScaffoldType.NASAL_SEPTUM] = ScaffoldType.NASAL_SEPTUM

    length: float = Field(
        default=40.0, ge=20.0, le=60.0, description="Length (mm)"
    )
    height: float = Field(
        default=30.0, ge=15.0, le=45.0, description="Height (mm)"
    )
    thickness: float = Field(
        default=3.0, ge=1.0, le=5.0, description="Thickness (mm)"
    )
    curvature_radius: float = Field(
        default=75.0, ge=30.0, le=200.0, description="Curvature radius (mm)"
    )
    curve_type: CurveType = Field(
        default=CurveType.SINGLE, description="Curve type"
    )


# ============================================================================
# Advanced Lattice Parameters (5 types)
# ============================================================================


class GyroidParams(BaseParams):
    """Parameters for gyroid TPMS scaffold."""

    type: Literal[ScaffoldType.GYROID] = ScaffoldType.GYROID

    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=10),
        description="Bounding box dimensions (mm)",
    )
    cell_size_mm: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Unit cell size (mm)"
    )
    wall_thickness_mm: float = Field(
        default=0.3, ge=0.1, le=1.0, description="Wall thickness (mm)"
    )
    isovalue: float = Field(
        default=0.0, ge=-1.0, le=1.0, description="Isovalue (-1 to 1)"
    )
    samples_per_cell: int = Field(
        default=20, ge=10, le=40, description="Samples per unit cell"
    )


class SchwarzPParams(BaseParams):
    """Parameters for Schwarz P TPMS scaffold."""

    type: Literal[ScaffoldType.SCHWARZ_P] = ScaffoldType.SCHWARZ_P

    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=10),
        description="Bounding box dimensions (mm)",
    )
    cell_size_mm: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Unit cell size (mm)"
    )
    wall_thickness_mm: float = Field(
        default=0.3, ge=0.1, le=1.0, description="Wall thickness (mm)"
    )
    isovalue: float = Field(
        default=0.0, ge=-2.9, le=2.9, description="Isovalue (-2.9 to 2.9)"
    )
    samples_per_cell: int = Field(
        default=20, ge=10, le=40, description="Samples per unit cell"
    )


class OctetTrussParams(BaseParams):
    """Parameters for octet truss lattice scaffold."""

    type: Literal[ScaffoldType.OCTET_TRUSS] = ScaffoldType.OCTET_TRUSS

    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=10),
        description="Bounding box dimensions (mm)",
    )
    cell_size_mm: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Unit cell size (mm)"
    )
    strut_diameter_mm: float = Field(
        default=0.3, ge=0.1, le=0.8, description="Strut diameter (mm)"
    )


class VoronoiParams(BaseParams):
    """Parameters for Voronoi lattice scaffold."""

    type: Literal[ScaffoldType.VORONOI] = ScaffoldType.VORONOI

    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=10),
        description="Bounding box dimensions (mm)",
    )
    cell_count: int = Field(
        default=30, ge=10, le=100, description="Number of Voronoi cells"
    )
    strut_diameter_mm: float = Field(
        default=0.3, ge=0.1, le=0.8, description="Strut diameter (mm)"
    )
    seed: Optional[int] = Field(
        default=None, description="Random seed for reproducibility"
    )
    margin_factor: float = Field(
        default=0.2, ge=0.1, le=0.5, description="Margin factor for boundary handling"
    )


class HoneycombParams(BaseParams):
    """Parameters for honeycomb lattice scaffold."""

    type: Literal[ScaffoldType.HONEYCOMB] = ScaffoldType.HONEYCOMB

    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=5),
        description="Bounding box dimensions (mm)",
    )
    cell_size_mm: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Cell size (flat-to-flat, mm)"
    )
    wall_thickness_mm: float = Field(
        default=0.3, ge=0.1, le=0.8, description="Wall thickness (mm)"
    )
    height_mm: Optional[float] = Field(
        default=None, description="Extrusion height (mm, uses bbox z if None)"
    )


# ============================================================================
# Microfluidic Parameters (3 types)
# ============================================================================


class OrganOnChipParams(BaseParams):
    """Parameters for organ-on-chip scaffold."""

    type: Literal[ScaffoldType.ORGAN_ON_CHIP] = ScaffoldType.ORGAN_ON_CHIP

    channel_width_mm: float = Field(
        default=0.3, ge=0.1, le=1.0, description="Channel width (mm)"
    )
    channel_depth_mm: float = Field(
        default=0.1, ge=0.05, le=0.5, description="Channel depth (mm)"
    )
    chamber_size: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=3, y=2, z=0.15),
        description="Chamber dimensions (mm)",
    )
    chamber_count: int = Field(
        default=2, ge=1, le=6, description="Number of chambers"
    )
    inlet_count: int = Field(
        default=2, ge=1, le=6, description="Number of inlets"
    )
    chip_size: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=15, y=10, z=2),
        description="Chip dimensions (mm)",
    )


class GradientScaffoldParams(BaseParams):
    """Parameters for gradient scaffold."""

    type: Literal[ScaffoldType.GRADIENT_SCAFFOLD] = ScaffoldType.GRADIENT_SCAFFOLD

    dimensions: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=10),
        description="Scaffold dimensions (mm)",
    )
    gradient_direction: Literal['x', 'y', 'z'] = Field(
        default='z', description="Gradient direction"
    )
    start_porosity: float = Field(
        default=0.2, ge=0.1, le=0.9, description="Porosity at start"
    )
    end_porosity: float = Field(
        default=0.8, ge=0.1, le=0.9, description="Porosity at end"
    )
    gradient_type: GradientType = Field(
        default=GradientType.LINEAR, description="Gradient function type"
    )
    pore_base_size_mm: float = Field(
        default=0.5, ge=0.2, le=1.0, description="Base pore size (mm)"
    )
    grid_spacing_mm: float = Field(
        default=1.5, ge=0.5, le=3.0, description="Grid spacing (mm)"
    )


class PerfusableNetworkParams(BaseParams):
    """Parameters for perfusable network scaffold."""

    type: Literal[ScaffoldType.PERFUSABLE_NETWORK] = ScaffoldType.PERFUSABLE_NETWORK

    inlet_diameter_mm: float = Field(
        default=2.0, ge=0.5, le=5.0, description="Inlet diameter (mm)"
    )
    branch_generations: int = Field(
        default=3, ge=1, le=5, description="Branch generations"
    )
    murray_ratio: float = Field(
        default=0.79, ge=0.5, le=0.95, description="Murray's law ratio"
    )
    network_type: NetworkType = Field(
        default=NetworkType.ARTERIAL, description="Network type"
    )
    bounding_box: BoundingBoxDimensions = Field(
        default=BoundingBoxDimensions(x=10, y=10, z=10),
        description="Bounding box dimensions (mm)",
    )
    branching_angle_deg: float = Field(
        default=30.0, ge=15.0, le=60.0, description="Branching angle (degrees)"
    )


# ============================================================================
# Discriminated Union
# ============================================================================

ScaffoldParams = Union[
    # Original 5
    VascularNetworkParams,
    PorousDiscParams,
    TubularConduitParams,
    LatticeParams,
    PrimitiveParams,
    # Skeletal 7
    TrabecularBoneParams,
    OsteochondralParams,
    ArticularCartilageParams,
    MeniscusParams,
    TendonLigamentParams,
    IntervertebralDiscParams,
    HaversianBoneParams,
    # Organ 6
    HepaticLobuleParams,
    CardiacPatchParams,
    KidneyTubuleParams,
    LungAlveoliParams,
    PancreaticIsletParams,
    LiverSinusoidParams,
    # Soft Tissue 4
    MultilayerSkinParams,
    SkeletalMuscleParams,
    CorneaParams,
    AdiposeParams,
    # Tubular 5
    BloodVesselParams,
    NerveConduitParams,
    SpinalCordParams,
    BladderParams,
    TracheaParams,
    # Dental 3
    DentinPulpParams,
    EarAuricleParams,
    NasalSeptumParams,
    # Advanced Lattice 5
    GyroidParams,
    SchwarzPParams,
    OctetTrussParams,
    VoronoiParams,
    HoneycombParams,
    # Microfluidic 3
    OrganOnChipParams,
    GradientScaffoldParams,
    PerfusableNetworkParams,
]


# ============================================================================
# Generation Results
# ============================================================================


class MeshData(BaseModel):
    """3D mesh data."""

    vertices: List[float] = Field(description="Flattened vertex array [x,y,z,...]")
    indices: List[int] = Field(description="Triangle indices")
    normals: List[float] = Field(description="Vertex normals [nx,ny,nz,...]")


class BoundingBox(BaseModel):
    """3D bounding box."""

    min: tuple[float, float, float] = Field(description="Minimum corner [x,y,z]")
    max: tuple[float, float, float] = Field(description="Maximum corner [x,y,z]")


class GenerationResult(BaseModel):
    """Result of scaffold generation."""

    mesh_data: MeshData = Field(description="3D mesh data")
    stl_base64: Optional[str] = Field(
        default=None, description="Base64-encoded STL file (optional, for export)"
    )
    triangle_count: int = Field(description="Number of triangles in mesh")
    bounding_box: BoundingBox = Field(description="Mesh bounding box")
    volume_mm3: float = Field(description="Calculated volume (mm3)")
    generation_time_ms: float = Field(description="Generation time (milliseconds)")


# ============================================================================
# Validation Results
# ============================================================================


class ValidationCheck(BaseModel):
    """Base validation check result."""

    passed: bool = Field(description="Whether the check passed")
    message: Optional[str] = Field(default=None, description="Optional message")


class MinWallThicknessCheck(ValidationCheck):
    """Minimum wall thickness validation check."""

    measured_mm: float = Field(description="Measured minimum wall thickness (mm)")
    required_mm: float = Field(description="Required minimum wall thickness (mm)")


class OverhangCheck(ValidationCheck):
    """Overhang angle validation check."""

    max_angle_deg: float = Field(description="Maximum overhang angle (degrees)")


class DimensionsCheck(ValidationCheck):
    """Dimensions validation check."""

    bounding_box: BoundingBox = Field(description="Measured bounding box")


class ValidationChecks(BaseModel):
    """Collection of validation checks."""

    watertight: ValidationCheck = Field(description="Watertight mesh check")
    min_wall_thickness: MinWallThicknessCheck = Field(
        description="Minimum wall thickness check"
    )
    overhang: OverhangCheck = Field(description="Overhang angle check")
    dimensions: DimensionsCheck = Field(description="Dimensions check")


class ValidationResult(BaseModel):
    """Result of scaffold validation."""

    is_valid: bool = Field(description="Overall validity")
    is_printable: bool = Field(description="3D printability assessment")
    checks: ValidationChecks = Field(description="Detailed validation checks")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")
    errors: List[str] = Field(default_factory=list, description="Critical errors")


# ============================================================================
# Chat Interface
# ============================================================================


class ChatMessage(BaseModel):
    """Chat message in the assistant interface."""

    role: Literal["user", "assistant"] = Field(description="Message role")
    content: str = Field(description="Message content")
    timestamp: str = Field(description="ISO timestamp")
    params_change: Optional[Dict[str, Any]] = Field(
        default=None, description="Parameter changes suggested by assistant"
    )
    suggestions: Optional[List[str]] = Field(
        default=None, description="Clickable suggestion chips"
    )


# ============================================================================
# Default Values
# ============================================================================

DEFAULT_RESOLUTION = 16

DEFAULT_VASCULAR_NETWORK = VascularNetworkParams(
    type=ScaffoldType.VASCULAR_NETWORK,
    resolution=DEFAULT_RESOLUTION,
    inlets=4,
    levels=3,
    splits=2,
    spread=0.5,
    ratio=0.79,
    curvature=0.3,
    tips_down=True,
    deterministic=False,
    outer_radius_mm=10.0,
    height_mm=5.0,
    inlet_radius_mm=1.0,
)

DEFAULT_POROUS_DISC = PorousDiscParams(
    type=ScaffoldType.POROUS_DISC,
    resolution=DEFAULT_RESOLUTION,
    diameter_mm=10.0,
    height_mm=2.0,
    pore_diameter_um=200.0,
    pore_spacing_um=400.0,
    pore_pattern=PorePattern.HEXAGONAL,
    porosity_target=0.5,
)

DEFAULT_TUBULAR_CONDUIT = TubularConduitParams(
    type=ScaffoldType.TUBULAR_CONDUIT,
    resolution=DEFAULT_RESOLUTION,
    outer_diameter_mm=6.0,
    wall_thickness_mm=1.0,
    length_mm=20.0,
    inner_texture=InnerTexture.SMOOTH,
)

DEFAULT_LATTICE = LatticeParams(
    type=ScaffoldType.LATTICE,
    resolution=DEFAULT_RESOLUTION,
    bounding_box=BoundingBoxDimensions(x=10, y=10, z=10),
    unit_cell=UnitCell.CUBIC,
    cell_size_mm=2.0,
    strut_diameter_mm=0.5,
)

DEFAULT_PRIMITIVE = PrimitiveParams(
    type=ScaffoldType.PRIMITIVE,
    resolution=DEFAULT_RESOLUTION,
    shape=PrimitiveShape.CYLINDER,
    dimensions={"radius": 5.0, "height": 10.0},
)

# ============================================================================
# Skeletal Tissue Defaults (7 types)
# ============================================================================

DEFAULT_TRABECULAR_BONE = TrabecularBoneParams(
    type=ScaffoldType.TRABECULAR_BONE,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_OSTEOCHONDRAL = OsteochondralParams(
    type=ScaffoldType.OSTEOCHONDRAL,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_ARTICULAR_CARTILAGE = ArticularCartilageParams(
    type=ScaffoldType.ARTICULAR_CARTILAGE,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_MENISCUS = MeniscusParams(
    type=ScaffoldType.MENISCUS,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_TENDON_LIGAMENT = TendonLigamentParams(
    type=ScaffoldType.TENDON_LIGAMENT,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_INTERVERTEBRAL_DISC = IntervertebralDiscParams(
    type=ScaffoldType.INTERVERTEBRAL_DISC,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_HAVERSIAN_BONE = HaversianBoneParams(
    type=ScaffoldType.HAVERSIAN_BONE,
    resolution=DEFAULT_RESOLUTION,
)

# ============================================================================
# Organ Defaults (6 types)
# ============================================================================

DEFAULT_HEPATIC_LOBULE = HepaticLobuleParams(
    type=ScaffoldType.HEPATIC_LOBULE,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_CARDIAC_PATCH = CardiacPatchParams(
    type=ScaffoldType.CARDIAC_PATCH,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_KIDNEY_TUBULE = KidneyTubuleParams(
    type=ScaffoldType.KIDNEY_TUBULE,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_LUNG_ALVEOLI = LungAlveoliParams(
    type=ScaffoldType.LUNG_ALVEOLI,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_PANCREATIC_ISLET = PancreaticIsletParams(
    type=ScaffoldType.PANCREATIC_ISLET,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_LIVER_SINUSOID = LiverSinusoidParams(
    type=ScaffoldType.LIVER_SINUSOID,
    resolution=DEFAULT_RESOLUTION,
)

# ============================================================================
# Soft Tissue Defaults (4 types)
# ============================================================================

DEFAULT_MULTILAYER_SKIN = MultilayerSkinParams(
    type=ScaffoldType.MULTILAYER_SKIN,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_SKELETAL_MUSCLE = SkeletalMuscleParams(
    type=ScaffoldType.SKELETAL_MUSCLE,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_CORNEA = CorneaParams(
    type=ScaffoldType.CORNEA,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_ADIPOSE = AdiposeParams(
    type=ScaffoldType.ADIPOSE,
    resolution=DEFAULT_RESOLUTION,
)

# ============================================================================
# Tubular Organ Defaults (5 types)
# ============================================================================

DEFAULT_BLOOD_VESSEL = BloodVesselParams(
    type=ScaffoldType.BLOOD_VESSEL,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_NERVE_CONDUIT = NerveConduitParams(
    type=ScaffoldType.NERVE_CONDUIT,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_SPINAL_CORD = SpinalCordParams(
    type=ScaffoldType.SPINAL_CORD,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_BLADDER = BladderParams(
    type=ScaffoldType.BLADDER,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_TRACHEA = TracheaParams(
    type=ScaffoldType.TRACHEA,
    resolution=DEFAULT_RESOLUTION,
)

# ============================================================================
# Dental/Craniofacial Defaults (3 types)
# ============================================================================

DEFAULT_DENTIN_PULP = DentinPulpParams(
    type=ScaffoldType.DENTIN_PULP,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_EAR_AURICLE = EarAuricleParams(
    type=ScaffoldType.EAR_AURICLE,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_NASAL_SEPTUM = NasalSeptumParams(
    type=ScaffoldType.NASAL_SEPTUM,
    resolution=DEFAULT_RESOLUTION,
)

# ============================================================================
# Advanced Lattice Defaults (5 types)
# ============================================================================

DEFAULT_GYROID = GyroidParams(
    type=ScaffoldType.GYROID,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_SCHWARZ_P = SchwarzPParams(
    type=ScaffoldType.SCHWARZ_P,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_OCTET_TRUSS = OctetTrussParams(
    type=ScaffoldType.OCTET_TRUSS,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_VORONOI = VoronoiParams(
    type=ScaffoldType.VORONOI,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_HONEYCOMB = HoneycombParams(
    type=ScaffoldType.HONEYCOMB,
    resolution=DEFAULT_RESOLUTION,
)

# ============================================================================
# Microfluidic Defaults (3 types)
# ============================================================================

DEFAULT_ORGAN_ON_CHIP = OrganOnChipParams(
    type=ScaffoldType.ORGAN_ON_CHIP,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_GRADIENT_SCAFFOLD = GradientScaffoldParams(
    type=ScaffoldType.GRADIENT_SCAFFOLD,
    resolution=DEFAULT_RESOLUTION,
)

DEFAULT_PERFUSABLE_NETWORK = PerfusableNetworkParams(
    type=ScaffoldType.PERFUSABLE_NETWORK,
    resolution=DEFAULT_RESOLUTION,
)
