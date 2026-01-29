/**
 * Type definitions for SHED scaffold generation
 * Synchronized with backend Python types
 */

// ============================================================================
// Enums
// ============================================================================

export enum ScaffoldType {
  // Existing
  VASCULAR_NETWORK = 'vascular_network',
  POROUS_DISC = 'porous_disc',
  TUBULAR_CONDUIT = 'tubular_conduit',
  LATTICE = 'lattice',
  PRIMITIVE = 'primitive',

  // Skeletal (7)
  TRABECULAR_BONE = 'trabecular_bone',
  OSTEOCHONDRAL = 'osteochondral',
  ARTICULAR_CARTILAGE = 'articular_cartilage',
  MENISCUS = 'meniscus',
  TENDON_LIGAMENT = 'tendon_ligament',
  INTERVERTEBRAL_DISC = 'intervertebral_disc',
  HAVERSIAN_BONE = 'haversian_bone',

  // Organ (6)
  HEPATIC_LOBULE = 'hepatic_lobule',
  CARDIAC_PATCH = 'cardiac_patch',
  KIDNEY_TUBULE = 'kidney_tubule',
  LUNG_ALVEOLI = 'lung_alveoli',
  PANCREATIC_ISLET = 'pancreatic_islet',
  LIVER_SINUSOID = 'liver_sinusoid',

  // Soft Tissue (4)
  MULTILAYER_SKIN = 'multilayer_skin',
  SKELETAL_MUSCLE = 'skeletal_muscle',
  CORNEA = 'cornea',
  ADIPOSE = 'adipose',

  // Tubular (5)
  BLOOD_VESSEL = 'blood_vessel',
  NERVE_CONDUIT = 'nerve_conduit',
  SPINAL_CORD = 'spinal_cord',
  BLADDER = 'bladder',
  TRACHEA = 'trachea',

  // Dental (3)
  DENTIN_PULP = 'dentin_pulp',
  EAR_AURICLE = 'ear_auricle',
  NASAL_SEPTUM = 'nasal_septum',

  // Advanced Lattice (5)
  GYROID = 'gyroid',
  SCHWARZ_P = 'schwarz_p',
  OCTET_TRUSS = 'octet_truss',
  VORONOI = 'voronoi',
  HONEYCOMB = 'honeycomb',

  // Microfluidic (3)
  ORGAN_ON_CHIP = 'organ_on_chip',
  GRADIENT_SCAFFOLD = 'gradient_scaffold',
  PERFUSABLE_NETWORK = 'perfusable_network',
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
}

export enum ModificationOperation {
  HOLE = 'hole',
  SHELL = 'shell',
}

export enum GradientType {
  LINEAR = 'linear',
  EXPONENTIAL = 'exponential',
}

export enum MuscleArchitecture {
  PARALLEL = 'parallel',
  UNIPENNATE = 'unipennate',
  BIPENNATE = 'bipennate',
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
// Existing Type-Specific Parameters
// ============================================================================

export interface VascularNetworkParams extends BaseParams {
  inlets: number;
  levels: number;
  splits: number;
  spread: number;
  ratio: number;
  curvature: number;
  tips_down: boolean;
  deterministic: boolean;
  outer_radius_mm: number;
  height_mm: number;
  inlet_radius_mm: number;
  seed?: number;
}

export interface PorousDiscParams extends BaseParams {
  diameter_mm: number;
  height_mm: number;
  pore_diameter_um: number;
  pore_spacing_um: number;
  pore_pattern: PorePattern;
  porosity_target?: number;
}

export interface TubularConduitParams extends BaseParams {
  outer_diameter_mm: number;
  wall_thickness_mm: number;
  length_mm: number;
  inner_texture?: InnerTexture;
  groove_count?: number;
}

export interface LatticeParams extends BaseParams {
  bounding_box: { x: number; y: number; z: number };
  unit_cell: UnitCell;
  cell_size_mm: number;
  strut_diameter_mm: number;
}

export interface PrimitiveModification {
  operation: ModificationOperation;
  params: Record<string, number>;
}

export interface PrimitiveParams extends BaseParams {
  shape: PrimitiveShape;
  dimensions: Record<string, number>;
  modifications?: PrimitiveModification[];
}

// ============================================================================
// Skeletal Tissue Parameters
// ============================================================================

export interface TrabecularBoneParams extends BaseParams {
  porosity: number;
  pore_size_um: number;
  strut_thickness_um: number;
  anisotropy_ratio: number;
  bounding_box: { x: number; y: number; z: number };
  seed: number;
}

export interface OsteochondralParams extends BaseParams {
  bone_depth: number;
  cartilage_depth: number;
  transition_width: number;
  gradient_type: GradientType;
  diameter: number;
  bone_porosity: number;
  cartilage_porosity: number;
}

export interface ArticularCartilageParams extends BaseParams {
  total_thickness: number;
  zone_ratios: [number, number, number];
  pore_gradient: [number, number, number];
  diameter: number;
}

export interface MeniscusParams extends BaseParams {
  inner_radius: number;
  outer_radius: number;
  height: number;
  wedge_angle_deg: number;
  zone_count: number;
  fiber_diameter: number;
  arc_degrees: number;
}

export interface TendonLigamentParams extends BaseParams {
  fiber_diameter: number;
  fiber_spacing: number;
  crimp_amplitude: number;
  crimp_wavelength: number;
  bundle_count: number;
  length: number;
  width: number;
  thickness: number;
}

export interface IntervertebralDiscParams extends BaseParams {
  disc_diameter: number;
  disc_height: number;
  af_ring_count: number;
  np_diameter: number;
  af_layer_angle: number;
  fiber_diameter: number;
  np_porosity: number;
}

export interface HaversianBoneParams extends BaseParams {
  canal_diameter_um: number;
  canal_spacing_um: number;
  cortical_thickness: number;
  osteon_pattern: OsteonPattern;
  bounding_box: { x: number; y: number; z: number };
}

// ============================================================================
// Organ-Specific Parameters
// ============================================================================

export interface HepaticLobuleParams extends BaseParams {
  num_lobules: number;
  lobule_radius: number;
  lobule_height: number;
  wall_thickness: number;
  central_vein_radius: number;
  portal_vein_radius: number;
  show_sinusoids: boolean;
  sinusoid_radius: number;
}

export interface CardiacPatchParams extends BaseParams {
  fiber_spacing: number;
  fiber_diameter: number;
  patch_size: { x: number; y: number; z: number };
  layer_count: number;
  alignment_angle: number;
}

export interface KidneyTubuleParams extends BaseParams {
  tubule_diameter: number;
  wall_thickness: number;
  convolution_amplitude: number;
  convolution_frequency: number;
  length: number;
}

export interface LungAlveoliParams extends BaseParams {
  branch_generations: number;
  alveoli_diameter: number;
  airway_diameter: number;
  branch_angle: number;
  bounding_box: { x: number; y: number; z: number };
}

export interface PancreaticIsletParams extends BaseParams {
  islet_diameter: number;
  shell_thickness: number;
  pore_size: number;
  cluster_count: number;
  spacing: number;
}

export interface LiverSinusoidParams extends BaseParams {
  sinusoid_diameter: number;
  length: number;
  fenestration_size: number;
  fenestration_density: number;
}

// ============================================================================
// Soft Tissue Parameters
// ============================================================================

export interface MultilayerSkinParams extends BaseParams {
  epidermis_thickness_mm: number;
  dermis_thickness_mm: number;
  hypodermis_thickness_mm: number;
  diameter_mm: number;
  pore_gradient: [number, number, number];
  vascular_channel_diameter_mm: number;
  vascular_channel_count: number;
}

export interface SkeletalMuscleParams extends BaseParams {
  fiber_diameter_um: number;
  fiber_spacing_um: number;
  pennation_angle_deg: number;
  fascicle_count: number;
  architecture_type: MuscleArchitecture;
  length_mm: number;
  width_mm: number;
  height_mm: number;
}

export interface CorneaParams extends BaseParams {
  diameter_mm: number;
  thickness_mm: number;
  radius_of_curvature_mm: number;
  lamella_count: number;
}

export interface AdiposeParams extends BaseParams {
  cell_size_um: number;
  wall_thickness_um: number;
  vascular_channel_spacing_mm: number;
  vascular_channel_diameter_mm: number;
  height_mm: number;
  diameter_mm: number;
}

// ============================================================================
// Tubular Organ Parameters
// ============================================================================

export interface BloodVesselParams extends BaseParams {
  inner_diameter_mm: number;
  wall_thickness_mm: number;
  layer_ratios: [number, number, number];
  length_mm: number;
  bifurcation_angle_deg?: number;
}

export interface NerveConduitParams extends BaseParams {
  outer_diameter_mm: number;
  channel_count: number;
  channel_diameter_um: number;
  wall_thickness_mm: number;
  length_mm: number;
}

export interface SpinalCordParams extends BaseParams {
  cord_diameter_mm: number;
  channel_diameter_um: number;
  channel_count: number;
  gray_matter_ratio: number;
  length_mm: number;
}

export interface BladderParams extends BaseParams {
  diameter_mm: number;
  wall_thickness_mm: number;
  layer_count: number;
  dome_curvature: number;
}

export interface TracheaParams extends BaseParams {
  outer_diameter_mm: number;
  ring_thickness_mm: number;
  ring_spacing_mm: number;
  ring_count: number;
  length_mm?: number;
  posterior_gap_angle_deg: number;
}

// ============================================================================
// Dental/Craniofacial Parameters
// ============================================================================

export interface DentinPulpParams extends BaseParams {
  tooth_height: number;
  crown_diameter: number;
  root_length: number;
  root_diameter: number;
  pulp_chamber_size: number;
  dentin_thickness: number;
}

export interface EarAuricleParams extends BaseParams {
  scale_factor: number;
  thickness: number;
  helix_definition: number;
  antihelix_depth: number;
}

export interface NasalSeptumParams extends BaseParams {
  length: number;
  height: number;
  thickness: number;
  curvature_radius: number;
  curve_type: CurveType;
}

// ============================================================================
// Advanced Lattice Parameters
// ============================================================================

export interface GyroidParams extends BaseParams {
  bounding_box_mm: { x: number; y: number; z: number };
  cell_size_mm: number;
  wall_thickness_mm: number;
  isovalue: number;
  samples_per_cell: number;
}

export interface SchwarzPParams extends BaseParams {
  bounding_box_mm: { x: number; y: number; z: number };
  cell_size_mm: number;
  wall_thickness_mm: number;
  isovalue: number;
  samples_per_cell: number;
}

export interface OctetTrussParams extends BaseParams {
  bounding_box_mm: { x: number; y: number; z: number };
  cell_size_mm: number;
  strut_diameter_mm: number;
}

export interface VoronoiParams extends BaseParams {
  bounding_box_mm: { x: number; y: number; z: number };
  cell_count: number;
  strut_diameter_mm: number;
  seed?: number;
  margin_factor: number;
}

export interface HoneycombParams extends BaseParams {
  bounding_box_mm: { x: number; y: number; z: number };
  cell_size_mm: number;
  wall_thickness_mm: number;
  height_mm?: number;
}

// ============================================================================
// Microfluidic Parameters
// ============================================================================

export interface OrganOnChipParams extends BaseParams {
  channel_width_mm: number;
  channel_depth_mm: number;
  chamber_size_mm: { x: number; y: number; z: number };
  chamber_count: number;
  inlet_count: number;
  chip_size_mm: { x: number; y: number; z: number };
}

export interface GradientScaffoldParams extends BaseParams {
  dimensions_mm: { x: number; y: number; z: number };
  gradient_direction: GradientDirection;
  start_porosity: number;
  end_porosity: number;
  gradient_type: GradientFunctionType;
  pore_base_size_mm: number;
  grid_spacing_mm: number;
}

export interface PerfusableNetworkParams extends BaseParams {
  inlet_diameter_mm: number;
  branch_generations: number;
  murray_ratio: number;
  network_type: NetworkType;
  bounding_box_mm: { x: number; y: number; z: number };
  branching_angle_deg: number;
}

// ============================================================================
// Discriminated Union
// ============================================================================

export type ScaffoldParams =
  // Existing
  | ({ type: ScaffoldType.VASCULAR_NETWORK } & VascularNetworkParams)
  | ({ type: ScaffoldType.POROUS_DISC } & PorousDiscParams)
  | ({ type: ScaffoldType.TUBULAR_CONDUIT } & TubularConduitParams)
  | ({ type: ScaffoldType.LATTICE } & LatticeParams)
  | ({ type: ScaffoldType.PRIMITIVE } & PrimitiveParams)
  // Skeletal
  | ({ type: ScaffoldType.TRABECULAR_BONE } & TrabecularBoneParams)
  | ({ type: ScaffoldType.OSTEOCHONDRAL } & OsteochondralParams)
  | ({ type: ScaffoldType.ARTICULAR_CARTILAGE } & ArticularCartilageParams)
  | ({ type: ScaffoldType.MENISCUS } & MeniscusParams)
  | ({ type: ScaffoldType.TENDON_LIGAMENT } & TendonLigamentParams)
  | ({ type: ScaffoldType.INTERVERTEBRAL_DISC } & IntervertebralDiscParams)
  | ({ type: ScaffoldType.HAVERSIAN_BONE } & HaversianBoneParams)
  // Organ
  | ({ type: ScaffoldType.HEPATIC_LOBULE } & HepaticLobuleParams)
  | ({ type: ScaffoldType.CARDIAC_PATCH } & CardiacPatchParams)
  | ({ type: ScaffoldType.KIDNEY_TUBULE } & KidneyTubuleParams)
  | ({ type: ScaffoldType.LUNG_ALVEOLI } & LungAlveoliParams)
  | ({ type: ScaffoldType.PANCREATIC_ISLET } & PancreaticIsletParams)
  | ({ type: ScaffoldType.LIVER_SINUSOID } & LiverSinusoidParams)
  // Soft Tissue
  | ({ type: ScaffoldType.MULTILAYER_SKIN } & MultilayerSkinParams)
  | ({ type: ScaffoldType.SKELETAL_MUSCLE } & SkeletalMuscleParams)
  | ({ type: ScaffoldType.CORNEA } & CorneaParams)
  | ({ type: ScaffoldType.ADIPOSE } & AdiposeParams)
  // Tubular
  | ({ type: ScaffoldType.BLOOD_VESSEL } & BloodVesselParams)
  | ({ type: ScaffoldType.NERVE_CONDUIT } & NerveConduitParams)
  | ({ type: ScaffoldType.SPINAL_CORD } & SpinalCordParams)
  | ({ type: ScaffoldType.BLADDER } & BladderParams)
  | ({ type: ScaffoldType.TRACHEA } & TracheaParams)
  // Dental
  | ({ type: ScaffoldType.DENTIN_PULP } & DentinPulpParams)
  | ({ type: ScaffoldType.EAR_AURICLE } & EarAuricleParams)
  | ({ type: ScaffoldType.NASAL_SEPTUM } & NasalSeptumParams)
  // Advanced Lattice
  | ({ type: ScaffoldType.GYROID } & GyroidParams)
  | ({ type: ScaffoldType.SCHWARZ_P } & SchwarzPParams)
  | ({ type: ScaffoldType.OCTET_TRUSS } & OctetTrussParams)
  | ({ type: ScaffoldType.VORONOI } & VoronoiParams)
  | ({ type: ScaffoldType.HONEYCOMB } & HoneycombParams)
  // Microfluidic
  | ({ type: ScaffoldType.ORGAN_ON_CHIP } & OrganOnChipParams)
  | ({ type: ScaffoldType.GRADIENT_SCAFFOLD } & GradientScaffoldParams)
  | ({ type: ScaffoldType.PERFUSABLE_NETWORK } & PerfusableNetworkParams);

// ============================================================================
// Generation Results
// ============================================================================

export interface MeshData {
  vertices: number[];
  indices: number[];
  normals: number[];
}

export interface BoundingBox {
  min: [number, number, number];
  max: [number, number, number];
}

export interface GenerationResult {
  mesh_data: MeshData;
  stl_base64?: string;
  triangle_count: number;
  bounding_box: BoundingBox;
  volume_mm3: number;
  generation_time_ms: number;
}

// ============================================================================
// Validation Results
// ============================================================================

export interface ValidationCheck {
  passed: boolean;
  message?: string;
}

export interface MinWallThicknessCheck extends ValidationCheck {
  measured_mm: number;
  required_mm: number;
}

export interface OverhangCheck extends ValidationCheck {
  max_angle_deg: number;
}

export interface DimensionsCheck extends ValidationCheck {
  bounding_box: BoundingBox;
}

export interface ValidationChecks {
  watertight: ValidationCheck;
  min_wall_thickness: MinWallThicknessCheck;
  overhang: OverhangCheck;
  dimensions: DimensionsCheck;
}

export interface ValidationResult {
  is_valid: boolean;
  is_printable: boolean;
  checks: ValidationChecks;
  warnings: string[];
  errors: string[];
}

// ============================================================================
// Chat Interface
// ============================================================================

export type ChatRole = 'user' | 'assistant';

export interface ChatMessage {
  role: ChatRole;
  content: string;
  timestamp: string;
  params_change?: Partial<ScaffoldParams>;
  suggestions?: string[];
}

// ============================================================================
// Type Guards (existing + new)
// ============================================================================

export function isVascularNetworkParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.VASCULAR_NETWORK } & VascularNetworkParams {
  return params.type === ScaffoldType.VASCULAR_NETWORK;
}

export function isPorousDiscParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.POROUS_DISC } & PorousDiscParams {
  return params.type === ScaffoldType.POROUS_DISC;
}

export function isTubularConduitParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.TUBULAR_CONDUIT } & TubularConduitParams {
  return params.type === ScaffoldType.TUBULAR_CONDUIT;
}

export function isLatticeParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.LATTICE } & LatticeParams {
  return params.type === ScaffoldType.LATTICE;
}

export function isPrimitiveParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.PRIMITIVE } & PrimitiveParams {
  return params.type === ScaffoldType.PRIMITIVE;
}

// Skeletal type guards
export function isTrabecularBoneParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.TRABECULAR_BONE } & TrabecularBoneParams {
  return params.type === ScaffoldType.TRABECULAR_BONE;
}

export function isOsteochondralParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.OSTEOCHONDRAL } & OsteochondralParams {
  return params.type === ScaffoldType.OSTEOCHONDRAL;
}

export function isArticularCartilageParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.ARTICULAR_CARTILAGE } & ArticularCartilageParams {
  return params.type === ScaffoldType.ARTICULAR_CARTILAGE;
}

export function isMeniscusParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.MENISCUS } & MeniscusParams {
  return params.type === ScaffoldType.MENISCUS;
}

export function isTendonLigamentParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.TENDON_LIGAMENT } & TendonLigamentParams {
  return params.type === ScaffoldType.TENDON_LIGAMENT;
}

export function isIntervertebralDiscParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.INTERVERTEBRAL_DISC } & IntervertebralDiscParams {
  return params.type === ScaffoldType.INTERVERTEBRAL_DISC;
}

export function isHaversianBoneParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.HAVERSIAN_BONE } & HaversianBoneParams {
  return params.type === ScaffoldType.HAVERSIAN_BONE;
}

// Organ type guards
export function isHepaticLobuleParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.HEPATIC_LOBULE } & HepaticLobuleParams {
  return params.type === ScaffoldType.HEPATIC_LOBULE;
}

export function isCardiacPatchParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.CARDIAC_PATCH } & CardiacPatchParams {
  return params.type === ScaffoldType.CARDIAC_PATCH;
}

export function isKidneyTubuleParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.KIDNEY_TUBULE } & KidneyTubuleParams {
  return params.type === ScaffoldType.KIDNEY_TUBULE;
}

export function isLungAlveoliParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.LUNG_ALVEOLI } & LungAlveoliParams {
  return params.type === ScaffoldType.LUNG_ALVEOLI;
}

export function isPancreaticIsletParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.PANCREATIC_ISLET } & PancreaticIsletParams {
  return params.type === ScaffoldType.PANCREATIC_ISLET;
}

export function isLiverSinusoidParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.LIVER_SINUSOID } & LiverSinusoidParams {
  return params.type === ScaffoldType.LIVER_SINUSOID;
}

// Soft tissue type guards
export function isMultilayerSkinParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.MULTILAYER_SKIN } & MultilayerSkinParams {
  return params.type === ScaffoldType.MULTILAYER_SKIN;
}

export function isSkeletalMuscleParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.SKELETAL_MUSCLE } & SkeletalMuscleParams {
  return params.type === ScaffoldType.SKELETAL_MUSCLE;
}

export function isCorneaParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.CORNEA } & CorneaParams {
  return params.type === ScaffoldType.CORNEA;
}

export function isAdiposeParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.ADIPOSE } & AdiposeParams {
  return params.type === ScaffoldType.ADIPOSE;
}

// Tubular type guards
export function isBloodVesselParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.BLOOD_VESSEL } & BloodVesselParams {
  return params.type === ScaffoldType.BLOOD_VESSEL;
}

export function isNerveConduitParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.NERVE_CONDUIT } & NerveConduitParams {
  return params.type === ScaffoldType.NERVE_CONDUIT;
}

export function isSpinalCordParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.SPINAL_CORD } & SpinalCordParams {
  return params.type === ScaffoldType.SPINAL_CORD;
}

export function isBladderParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.BLADDER } & BladderParams {
  return params.type === ScaffoldType.BLADDER;
}

export function isTracheaParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.TRACHEA } & TracheaParams {
  return params.type === ScaffoldType.TRACHEA;
}

// Dental type guards
export function isDentinPulpParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.DENTIN_PULP } & DentinPulpParams {
  return params.type === ScaffoldType.DENTIN_PULP;
}

export function isEarAuricleParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.EAR_AURICLE } & EarAuricleParams {
  return params.type === ScaffoldType.EAR_AURICLE;
}

export function isNasalSeptumParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.NASAL_SEPTUM } & NasalSeptumParams {
  return params.type === ScaffoldType.NASAL_SEPTUM;
}

// Advanced lattice type guards
export function isGyroidParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.GYROID } & GyroidParams {
  return params.type === ScaffoldType.GYROID;
}

export function isSchwarzPParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.SCHWARZ_P } & SchwarzPParams {
  return params.type === ScaffoldType.SCHWARZ_P;
}

export function isOctetTrussParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.OCTET_TRUSS } & OctetTrussParams {
  return params.type === ScaffoldType.OCTET_TRUSS;
}

export function isVoronoiParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.VORONOI } & VoronoiParams {
  return params.type === ScaffoldType.VORONOI;
}

export function isHoneycombParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.HONEYCOMB } & HoneycombParams {
  return params.type === ScaffoldType.HONEYCOMB;
}

// Microfluidic type guards
export function isOrganOnChipParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.ORGAN_ON_CHIP } & OrganOnChipParams {
  return params.type === ScaffoldType.ORGAN_ON_CHIP;
}

export function isGradientScaffoldParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.GRADIENT_SCAFFOLD } & GradientScaffoldParams {
  return params.type === ScaffoldType.GRADIENT_SCAFFOLD;
}

export function isPerfusableNetworkParams(
  params: ScaffoldParams
): params is { type: ScaffoldType.PERFUSABLE_NETWORK } & PerfusableNetworkParams {
  return params.type === ScaffoldType.PERFUSABLE_NETWORK;
}

// ============================================================================
// Default Values (existing + new)
// ============================================================================

export const DEFAULT_RESOLUTION = 16;

export const DEFAULT_VASCULAR_NETWORK: VascularNetworkParams = {
  resolution: DEFAULT_RESOLUTION,
  inlets: 4,
  levels: 3,
  splits: 2,
  spread: 0.5,
  ratio: 0.79,
  curvature: 0.3,
  tips_down: true,
  deterministic: false,
  outer_radius_mm: 10,
  height_mm: 5,
  inlet_radius_mm: 1,
};

export const DEFAULT_POROUS_DISC: PorousDiscParams = {
  resolution: DEFAULT_RESOLUTION,
  diameter_mm: 10,
  height_mm: 2,
  pore_diameter_um: 200,
  pore_spacing_um: 400,
  pore_pattern: PorePattern.HEXAGONAL,
  porosity_target: 0.5,
};

export const DEFAULT_TUBULAR_CONDUIT: TubularConduitParams = {
  resolution: DEFAULT_RESOLUTION,
  outer_diameter_mm: 6,
  wall_thickness_mm: 1,
  length_mm: 20,
  inner_texture: InnerTexture.SMOOTH,
};

export const DEFAULT_LATTICE: LatticeParams = {
  resolution: DEFAULT_RESOLUTION,
  bounding_box: { x: 10, y: 10, z: 10 },
  unit_cell: UnitCell.CUBIC,
  cell_size_mm: 2,
  strut_diameter_mm: 0.5,
};

export const DEFAULT_PRIMITIVE: PrimitiveParams = {
  resolution: DEFAULT_RESOLUTION,
  shape: PrimitiveShape.CYLINDER,
  dimensions: { radius: 5, height: 10 },
};

// Skeletal defaults
export const DEFAULT_TRABECULAR_BONE: TrabecularBoneParams = {
  resolution: 8,
  porosity: 0.7,
  pore_size_um: 400.0,
  strut_thickness_um: 200.0,
  anisotropy_ratio: 1.5,
  bounding_box: { x: 10.0, y: 10.0, z: 10.0 },
  seed: 42,
};

export const DEFAULT_OSTEOCHONDRAL: OsteochondralParams = {
  resolution: DEFAULT_RESOLUTION,
  bone_depth: 3.0,
  cartilage_depth: 2.0,
  transition_width: 1.0,
  gradient_type: GradientType.LINEAR,
  diameter: 8.0,
  bone_porosity: 0.7,
  cartilage_porosity: 0.85,
};

export const DEFAULT_ARTICULAR_CARTILAGE: ArticularCartilageParams = {
  resolution: DEFAULT_RESOLUTION,
  total_thickness: 2.0,
  zone_ratios: [0.2, 0.4, 0.4],
  pore_gradient: [0.15, 0.25, 0.35],
  diameter: 8.0,
};

export const DEFAULT_MENISCUS: MeniscusParams = {
  resolution: 32,
  inner_radius: 12.0,
  outer_radius: 20.0,
  height: 8.0,
  wedge_angle_deg: 20.0,
  zone_count: 3,
  fiber_diameter: 0.2,
  arc_degrees: 300.0,
};

export const DEFAULT_TENDON_LIGAMENT: TendonLigamentParams = {
  resolution: 12,
  fiber_diameter: 0.15,
  fiber_spacing: 0.4,
  crimp_amplitude: 0.3,
  crimp_wavelength: 2.0,
  bundle_count: 5,
  length: 20.0,
  width: 5.0,
  thickness: 2.0,
};

export const DEFAULT_INTERVERTEBRAL_DISC: IntervertebralDiscParams = {
  resolution: 32,
  disc_diameter: 40.0,
  disc_height: 10.0,
  af_ring_count: 5,
  np_diameter: 15.0,
  af_layer_angle: 30.0,
  fiber_diameter: 0.15,
  np_porosity: 0.9,
};

export const DEFAULT_HAVERSIAN_BONE: HaversianBoneParams = {
  resolution: 12,
  canal_diameter_um: 50.0,
  canal_spacing_um: 250.0,
  cortical_thickness: 5.0,
  osteon_pattern: OsteonPattern.HEXAGONAL,
  bounding_box: { x: 10.0, y: 10.0, z: 15.0 },
};

// Organ defaults
export const DEFAULT_HEPATIC_LOBULE: HepaticLobuleParams = {
  resolution: 8,
  num_lobules: 1,
  lobule_radius: 1.5,
  lobule_height: 3.0,
  wall_thickness: 0.1,
  central_vein_radius: 0.15,
  portal_vein_radius: 0.12,
  show_sinusoids: false,
  sinusoid_radius: 0.025,
};

export const DEFAULT_CARDIAC_PATCH: CardiacPatchParams = {
  resolution: 8,
  fiber_spacing: 300.0,
  fiber_diameter: 100.0,
  patch_size: { x: 10.0, y: 10.0, z: 1.0 },
  layer_count: 3,
  alignment_angle: 0.0,
};

export const DEFAULT_KIDNEY_TUBULE: KidneyTubuleParams = {
  resolution: DEFAULT_RESOLUTION,
  tubule_diameter: 100.0,
  wall_thickness: 15.0,
  convolution_amplitude: 500.0,
  convolution_frequency: 3.0,
  length: 10.0,
};

export const DEFAULT_LUNG_ALVEOLI: LungAlveoliParams = {
  resolution: 12,
  branch_generations: 3,
  alveoli_diameter: 200.0,
  airway_diameter: 1.0,
  branch_angle: 35.0,
  bounding_box: { x: 10.0, y: 10.0, z: 10.0 },
};

export const DEFAULT_PANCREATIC_ISLET: PancreaticIsletParams = {
  resolution: DEFAULT_RESOLUTION,
  islet_diameter: 200.0,
  shell_thickness: 50.0,
  pore_size: 20.0,
  cluster_count: 7,
  spacing: 300.0,
};

export const DEFAULT_LIVER_SINUSOID: LiverSinusoidParams = {
  resolution: DEFAULT_RESOLUTION,
  sinusoid_diameter: 20.0,
  length: 5.0,
  fenestration_size: 1.0,
  fenestration_density: 0.2,
};

// Soft tissue defaults
export const DEFAULT_MULTILAYER_SKIN: MultilayerSkinParams = {
  resolution: DEFAULT_RESOLUTION,
  epidermis_thickness_mm: 0.15,
  dermis_thickness_mm: 1.5,
  hypodermis_thickness_mm: 3.0,
  diameter_mm: 10.0,
  pore_gradient: [0.3, 0.5, 0.7],
  vascular_channel_diameter_mm: 0.2,
  vascular_channel_count: 8,
};

export const DEFAULT_SKELETAL_MUSCLE: SkeletalMuscleParams = {
  resolution: 8,
  fiber_diameter_um: 75.0,
  fiber_spacing_um: 150.0,
  pennation_angle_deg: 15.0,
  fascicle_count: 3,
  architecture_type: MuscleArchitecture.PARALLEL,
  length_mm: 10.0,
  width_mm: 5.0,
  height_mm: 5.0,
};

export const DEFAULT_CORNEA: CorneaParams = {
  resolution: 32,
  diameter_mm: 11.0,
  thickness_mm: 0.55,
  radius_of_curvature_mm: 7.8,
  lamella_count: 5,
};

export const DEFAULT_ADIPOSE: AdiposeParams = {
  resolution: 6,
  cell_size_um: 150.0,
  wall_thickness_um: 30.0,
  vascular_channel_spacing_mm: 2.0,
  vascular_channel_diameter_mm: 0.3,
  height_mm: 5.0,
  diameter_mm: 10.0,
};

// Tubular defaults
export const DEFAULT_BLOOD_VESSEL: BloodVesselParams = {
  resolution: 32,
  inner_diameter_mm: 5.0,
  wall_thickness_mm: 1.0,
  layer_ratios: [0.1, 0.5, 0.4],
  length_mm: 30.0,
};

export const DEFAULT_NERVE_CONDUIT: NerveConduitParams = {
  resolution: DEFAULT_RESOLUTION,
  outer_diameter_mm: 4.0,
  channel_count: 7,
  channel_diameter_um: 200.0,
  wall_thickness_mm: 0.5,
  length_mm: 20.0,
};

export const DEFAULT_SPINAL_CORD: SpinalCordParams = {
  resolution: 32,
  cord_diameter_mm: 12.0,
  channel_diameter_um: 300.0,
  channel_count: 24,
  gray_matter_ratio: 0.4,
  length_mm: 50.0,
};

export const DEFAULT_BLADDER: BladderParams = {
  resolution: 32,
  diameter_mm: 70.0,
  wall_thickness_mm: 3.0,
  layer_count: 3,
  dome_curvature: 0.7,
};

export const DEFAULT_TRACHEA: TracheaParams = {
  resolution: 32,
  outer_diameter_mm: 20.0,
  ring_thickness_mm: 3.0,
  ring_spacing_mm: 4.0,
  ring_count: 10,
  posterior_gap_angle_deg: 90.0,
};

// Dental defaults
export const DEFAULT_DENTIN_PULP: DentinPulpParams = {
  resolution: 32,
  tooth_height: 12.0,
  crown_diameter: 10.0,
  root_length: 12.0,
  root_diameter: 5.0,
  pulp_chamber_size: 0.4,
  dentin_thickness: 3.0,
};

export const DEFAULT_EAR_AURICLE: EarAuricleParams = {
  resolution: 32,
  scale_factor: 1.0,
  thickness: 2.0,
  helix_definition: 0.7,
  antihelix_depth: 0.3,
};

export const DEFAULT_NASAL_SEPTUM: NasalSeptumParams = {
  resolution: 32,
  length: 40.0,
  height: 30.0,
  thickness: 3.0,
  curvature_radius: 75.0,
  curve_type: CurveType.SINGLE,
};

// Advanced lattice defaults
export const DEFAULT_GYROID: GyroidParams = {
  resolution: DEFAULT_RESOLUTION,
  bounding_box_mm: { x: 10.0, y: 10.0, z: 10.0 },
  cell_size_mm: 2.0,
  wall_thickness_mm: 0.3,
  isovalue: 0.0,
  samples_per_cell: 20,
};

export const DEFAULT_SCHWARZ_P: SchwarzPParams = {
  resolution: DEFAULT_RESOLUTION,
  bounding_box_mm: { x: 10.0, y: 10.0, z: 10.0 },
  cell_size_mm: 2.0,
  wall_thickness_mm: 0.3,
  isovalue: 0.0,
  samples_per_cell: 20,
};

export const DEFAULT_OCTET_TRUSS: OctetTrussParams = {
  resolution: 8,
  bounding_box_mm: { x: 10.0, y: 10.0, z: 10.0 },
  cell_size_mm: 2.0,
  strut_diameter_mm: 0.3,
};

export const DEFAULT_VORONOI: VoronoiParams = {
  resolution: 8,
  bounding_box_mm: { x: 10.0, y: 10.0, z: 10.0 },
  cell_count: 30,
  strut_diameter_mm: 0.3,
  margin_factor: 0.2,
};

export const DEFAULT_HONEYCOMB: HoneycombParams = {
  resolution: 1,
  bounding_box_mm: { x: 10.0, y: 10.0, z: 5.0 },
  cell_size_mm: 2.0,
  wall_thickness_mm: 0.3,
};

// Microfluidic defaults
export const DEFAULT_ORGAN_ON_CHIP: OrganOnChipParams = {
  resolution: 8,
  channel_width_mm: 0.3,
  channel_depth_mm: 0.1,
  chamber_size_mm: { x: 3.0, y: 2.0, z: 0.15 },
  chamber_count: 2,
  inlet_count: 2,
  chip_size_mm: { x: 15.0, y: 10.0, z: 2.0 },
};

export const DEFAULT_GRADIENT_SCAFFOLD: GradientScaffoldParams = {
  resolution: 12,
  dimensions_mm: { x: 10.0, y: 10.0, z: 10.0 },
  gradient_direction: GradientDirection.Z,
  start_porosity: 0.2,
  end_porosity: 0.8,
  gradient_type: GradientFunctionType.LINEAR,
  pore_base_size_mm: 0.5,
  grid_spacing_mm: 1.5,
};

export const DEFAULT_PERFUSABLE_NETWORK: PerfusableNetworkParams = {
  resolution: 12,
  inlet_diameter_mm: 2.0,
  branch_generations: 3,
  murray_ratio: 0.79,
  network_type: NetworkType.ARTERIAL,
  bounding_box_mm: { x: 10.0, y: 10.0, z: 10.0 },
  branching_angle_deg: 30.0,
};
