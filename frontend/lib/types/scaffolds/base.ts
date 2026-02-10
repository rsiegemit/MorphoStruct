/**
 * Base type definitions for MorphoStruct scaffold generation
 * Synchronized with backend Python types
 */

// ============================================================================
// Enums
// ============================================================================

export enum ScaffoldType {
  // Dental (3)
  DENTIN_PULP = 'dentin_pulp',
  EAR_AURICLE = 'ear_auricle',
  NASAL_SEPTUM = 'nasal_septum',

  // Lattice (6)
  GYROID = 'gyroid',
  HONEYCOMB = 'honeycomb',
  LATTICE = 'lattice',
  OCTET_TRUSS = 'octet_truss',
  SCHWARZ_P = 'schwarz_p',
  VORONOI = 'voronoi',

  // Legacy (3)
  POROUS_DISC = 'porous_disc',
  PRIMITIVE = 'primitive',
  VASCULAR_NETWORK = 'vascular_network',

  // Microfluidic (3)
  GRADIENT_SCAFFOLD = 'gradient_scaffold',
  ORGAN_ON_CHIP = 'organ_on_chip',
  PERFUSABLE_NETWORK = 'perfusable_network',

  // Organ (6)
  CARDIAC_PATCH = 'cardiac_patch',
  HEPATIC_LOBULE = 'hepatic_lobule',
  KIDNEY_TUBULE = 'kidney_tubule',
  LIVER_SINUSOID = 'liver_sinusoid',
  LUNG_ALVEOLI = 'lung_alveoli',
  PANCREATIC_ISLET = 'pancreatic_islet',

  // Skeletal (7)
  ARTICULAR_CARTILAGE = 'articular_cartilage',
  HAVERSIAN_BONE = 'haversian_bone',
  INTERVERTEBRAL_DISC = 'intervertebral_disc',
  MENISCUS = 'meniscus',
  OSTEOCHONDRAL = 'osteochondral',
  TENDON_LIGAMENT = 'tendon_ligament',
  TRABECULAR_BONE = 'trabecular_bone',

  // Soft Tissue (4)
  ADIPOSE = 'adipose',
  CORNEA = 'cornea',
  MULTILAYER_SKIN = 'multilayer_skin',
  SKELETAL_MUSCLE = 'skeletal_muscle',

  // Tubular (7)
  BLADDER = 'bladder',
  BLOOD_VESSEL = 'blood_vessel',
  NERVE_CONDUIT = 'nerve_conduit',
  SPINAL_CORD = 'spinal_cord',
  TRACHEA = 'trachea',
  TUBULAR_CONDUIT = 'tubular_conduit',
  VASCULAR_PERFUSION_DISH = 'vascular_perfusion_dish',
}

export enum PorePattern {
  HEXAGONAL = 'hexagonal',
  GRID = 'grid',
}

export enum InnerTexture {
  SMOOTH = 'smooth',
  GROOVED = 'grooved',
  POROUS = 'porous',
}

export enum UnitCell {
  CUBIC = 'cubic',
  BCC = 'bcc',
}

export enum PrimitiveShape {
  CYLINDER = 'cylinder',
  SPHERE = 'sphere',
  BOX = 'box',
  CONE = 'cone',

  // Geometric (8 new)
  TORUS = 'torus',
  CAPSULE = 'capsule',
  PYRAMID = 'pyramid',
  WEDGE = 'wedge',
  PRISM = 'prism',
  TUBE = 'tube',
  ELLIPSOID = 'ellipsoid',
  HEMISPHERE = 'hemisphere',

  // Architectural (7 new)
  FILLET = 'fillet',
  CHAMFER = 'chamfer',
  SLOT = 'slot',
  COUNTERBORE = 'counterbore',
  COUNTERSINK = 'countersink',
  BOSS = 'boss',
  RIB = 'rib',

  // Organic/Bio (8 new)
  BRANCH = 'branch',
  BIFURCATION = 'bifurcation',
  PORE = 'pore',
  CHANNEL = 'channel',
  FIBER = 'fiber',
  MEMBRANE = 'membrane',
  LATTICE_CELL = 'lattice_cell',
  PORE_ARRAY = 'pore_array',
}

export enum ModificationOperation {
  HOLE = 'hole',
  SHELL = 'shell',
  FILLET_EDGES = 'fillet_edges',
  CHAMFER_EDGES = 'chamfer_edges',
  TAPER = 'taper',
  TWIST = 'twist',
}

export enum GradientType {
  LINEAR = 'linear',
  EXPONENTIAL = 'exponential',
}

export enum MuscleArchitecture {
  PARALLEL = 'parallel',
  UNIPENNATE = 'unipennate',
  BIPENNATE = 'bipennate',
  MULTIPENNATE = 'multipennate',
  CIRCULAR = 'circular',
  CONVERGENT = 'convergent',
}

export enum OsteonPattern {
  HEXAGONAL = 'hexagonal',
  RANDOM = 'random',
}

export enum CurveType {
  SINGLE = 'single',
  S_CURVE = 's_curve',
}

export enum NetworkType {
  ARTERIAL = 'arterial',
  VENOUS = 'venous',
  CAPILLARY = 'capillary',
}

export enum GradientDirection {
  X = 'x',
  Y = 'y',
  Z = 'z',
}

export enum GradientFunctionType {
  LINEAR = 'linear',
  EXPONENTIAL = 'exponential',
  SIGMOID = 'sigmoid',
}

// ============================================================================
// Base Parameters
// ============================================================================

export interface BaseParams {
  /** Mesh resolution (6-32, default 16) */
  resolution: number;
}

// ============================================================================
// Shared Helper Interfaces
// ============================================================================

export interface PrimitiveModification {
  operation: ModificationOperation;
  params: Record<string, number>;
}
