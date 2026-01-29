/**
 * Parameter metadata for dynamic control generation
 * Defines min/max/step/label/unit for each scaffold parameter
 */

import { ScaffoldType } from './types/scaffold';

export interface NumberParamMeta {
  type: 'number';
  label: string;
  min: number;
  max: number;
  step: number;
  unit?: string;
  description?: string;
}

export interface BooleanParamMeta {
  type: 'boolean';
  label: string;
  description?: string;
}

export interface EnumParamMeta {
  type: 'enum';
  label: string;
  options: { value: string; label: string }[];
  description?: string;
}

export interface ObjectParamMeta {
  type: 'object';
  label: string;
  properties: Record<string, NumberParamMeta>;
  description?: string;
}

export interface ArrayParamMeta {
  type: 'array';
  label: string;
  itemCount: number;
  itemLabels?: string[];
  min: number;
  max: number;
  step: number;
  description?: string;
}

export type ParamMeta = NumberParamMeta | BooleanParamMeta | EnumParamMeta | ObjectParamMeta | ArrayParamMeta;

// Common bounding box metadata
const boundingBoxMeta: ObjectParamMeta = {
  type: 'object',
  label: 'Bounding Box (mm)',
  properties: {
    x: { type: 'number', label: 'X', min: 1, max: 100, step: 1, unit: 'mm' },
    y: { type: 'number', label: 'Y', min: 1, max: 100, step: 1, unit: 'mm' },
    z: { type: 'number', label: 'Z', min: 1, max: 100, step: 1, unit: 'mm' },
  },
};

// Parameter metadata by scaffold type
export const PARAMETER_META: Record<ScaffoldType, Record<string, ParamMeta>> = {
  // === Existing Types ===
  [ScaffoldType.VASCULAR_NETWORK]: {
    inlets: { type: 'number', label: 'Inlets', min: 1, max: 25, step: 1 },
    levels: { type: 'number', label: 'Branching Levels', min: 0, max: 8, step: 1 },
    splits: { type: 'number', label: 'Splits per Branch', min: 1, max: 6, step: 1 },
    spread: { type: 'number', label: 'Spread', min: 0.1, max: 0.8, step: 0.05 },
    ratio: { type: 'number', label: 'Radius Ratio (Murray)', min: 0.5, max: 0.95, step: 0.01 },
    curvature: { type: 'number', label: 'Curvature', min: 0, max: 1, step: 0.05 },
    tips_down: { type: 'boolean', label: 'Tips Down' },
    deterministic: { type: 'boolean', label: 'Deterministic Pattern' },
    outer_radius_mm: { type: 'number', label: 'Outer Radius', min: 1, max: 50, step: 1, unit: 'mm' },
    height_mm: { type: 'number', label: 'Height', min: 1, max: 50, step: 1, unit: 'mm' },
    inlet_radius_mm: { type: 'number', label: 'Inlet Radius', min: 0.1, max: 5, step: 0.1, unit: 'mm' },
  },

  [ScaffoldType.POROUS_DISC]: {
    diameter_mm: { type: 'number', label: 'Diameter', min: 1, max: 50, step: 1, unit: 'mm' },
    height_mm: { type: 'number', label: 'Height', min: 0.5, max: 10, step: 0.5, unit: 'mm' },
    pore_diameter_um: { type: 'number', label: 'Pore Diameter', min: 50, max: 500, step: 10, unit: 'um' },
    pore_spacing_um: { type: 'number', label: 'Pore Spacing', min: 100, max: 1000, step: 50, unit: 'um' },
    pore_pattern: {
      type: 'enum',
      label: 'Pore Pattern',
      options: [
        { value: 'hexagonal', label: 'Hexagonal' },
        { value: 'grid', label: 'Grid' },
      ],
    },
    porosity_target: { type: 'number', label: 'Target Porosity', min: 0.2, max: 0.8, step: 0.05 },
  },

  [ScaffoldType.TUBULAR_CONDUIT]: {
    outer_diameter_mm: { type: 'number', label: 'Outer Diameter', min: 1, max: 20, step: 0.5, unit: 'mm' },
    wall_thickness_mm: { type: 'number', label: 'Wall Thickness', min: 0.3, max: 5, step: 0.1, unit: 'mm' },
    length_mm: { type: 'number', label: 'Length', min: 1, max: 100, step: 1, unit: 'mm' },
    inner_texture: {
      type: 'enum',
      label: 'Inner Texture',
      options: [
        { value: 'smooth', label: 'Smooth' },
        { value: 'grooved', label: 'Grooved' },
        { value: 'porous', label: 'Porous' },
      ],
    },
    groove_count: { type: 'number', label: 'Groove Count', min: 2, max: 32, step: 1 },
  },

  [ScaffoldType.LATTICE]: {
    bounding_box: boundingBoxMeta,
    unit_cell: {
      type: 'enum',
      label: 'Unit Cell',
      options: [
        { value: 'cubic', label: 'Cubic' },
        { value: 'bcc', label: 'BCC (Body-Centered)' },
      ],
    },
    cell_size_mm: { type: 'number', label: 'Cell Size', min: 0.5, max: 5, step: 0.1, unit: 'mm' },
    strut_diameter_mm: { type: 'number', label: 'Strut Diameter', min: 0.2, max: 1, step: 0.05, unit: 'mm' },
  },

  [ScaffoldType.PRIMITIVE]: {
    shape: {
      type: 'enum',
      label: 'Shape',
      options: [
        { value: 'cylinder', label: 'Cylinder' },
        { value: 'sphere', label: 'Sphere' },
        { value: 'box', label: 'Box' },
        { value: 'cone', label: 'Cone' },
      ],
    },
    // dimensions handled specially based on shape
  },

  // === Skeletal Types ===
  [ScaffoldType.TRABECULAR_BONE]: {
    porosity: { type: 'number', label: 'Porosity', min: 0, max: 1, step: 0.05, description: 'Void fraction' },
    pore_size_um: { type: 'number', label: 'Pore Size', min: 50, max: 1000, step: 50, unit: 'um' },
    strut_thickness_um: { type: 'number', label: 'Strut Thickness', min: 50, max: 500, step: 25, unit: 'um' },
    anisotropy_ratio: { type: 'number', label: 'Anisotropy Ratio', min: 1, max: 3, step: 0.1, description: '1.0 = isotropic' },
    bounding_box: boundingBoxMeta,
    seed: { type: 'number', label: 'Random Seed', min: 0, max: 9999, step: 1 },
  },

  [ScaffoldType.OSTEOCHONDRAL]: {
    bone_depth: { type: 'number', label: 'Bone Zone Depth', min: 1, max: 10, step: 0.5, unit: 'mm' },
    cartilage_depth: { type: 'number', label: 'Cartilage Zone Depth', min: 0.5, max: 5, step: 0.25, unit: 'mm' },
    transition_width: { type: 'number', label: 'Transition Width', min: 0.2, max: 3, step: 0.2, unit: 'mm' },
    gradient_type: {
      type: 'enum',
      label: 'Gradient Type',
      options: [
        { value: 'linear', label: 'Linear' },
        { value: 'exponential', label: 'Exponential' },
      ],
    },
    diameter: { type: 'number', label: 'Diameter', min: 3, max: 20, step: 1, unit: 'mm' },
    bone_porosity: { type: 'number', label: 'Bone Porosity', min: 0.5, max: 0.9, step: 0.05 },
    cartilage_porosity: { type: 'number', label: 'Cartilage Porosity', min: 0.7, max: 0.95, step: 0.05 },
  },

  [ScaffoldType.ARTICULAR_CARTILAGE]: {
    total_thickness: { type: 'number', label: 'Total Thickness', min: 0.5, max: 5, step: 0.25, unit: 'mm' },
    zone_ratios: {
      type: 'array',
      label: 'Zone Ratios',
      itemCount: 3,
      itemLabels: ['Superficial', 'Middle', 'Deep'],
      min: 0.05,
      max: 0.8,
      step: 0.05,
      description: 'Must sum to 1.0',
    },
    pore_gradient: {
      type: 'array',
      label: 'Pore Gradient (mm)',
      itemCount: 3,
      itemLabels: ['Superficial', 'Middle', 'Deep'],
      min: 0.05,
      max: 0.5,
      step: 0.05,
    },
    diameter: { type: 'number', label: 'Diameter', min: 3, max: 20, step: 1, unit: 'mm' },
  },

  [ScaffoldType.MENISCUS]: {
    inner_radius: { type: 'number', label: 'Inner Radius', min: 5, max: 20, step: 1, unit: 'mm' },
    outer_radius: { type: 'number', label: 'Outer Radius', min: 10, max: 30, step: 1, unit: 'mm' },
    height: { type: 'number', label: 'Height', min: 3, max: 15, step: 1, unit: 'mm' },
    wedge_angle_deg: { type: 'number', label: 'Wedge Angle', min: 10, max: 45, step: 5, unit: 'deg' },
    zone_count: { type: 'number', label: 'Zone Count', min: 2, max: 5, step: 1 },
    fiber_diameter: { type: 'number', label: 'Fiber Diameter', min: 0.05, max: 0.5, step: 0.05, unit: 'mm' },
    arc_degrees: { type: 'number', label: 'Arc Extent', min: 180, max: 360, step: 15, unit: 'deg' },
  },

  [ScaffoldType.TENDON_LIGAMENT]: {
    fiber_diameter: { type: 'number', label: 'Fiber Diameter', min: 0.05, max: 0.3, step: 0.01, unit: 'mm' },
    fiber_spacing: { type: 'number', label: 'Fiber Spacing', min: 0.1, max: 1, step: 0.05, unit: 'mm' },
    crimp_amplitude: { type: 'number', label: 'Crimp Amplitude', min: 0.05, max: 1, step: 0.05, unit: 'mm' },
    crimp_wavelength: { type: 'number', label: 'Crimp Wavelength', min: 0.5, max: 5, step: 0.25, unit: 'mm' },
    bundle_count: { type: 'number', label: 'Bundle Count', min: 1, max: 10, step: 1 },
    length: { type: 'number', label: 'Length', min: 5, max: 100, step: 5, unit: 'mm' },
    width: { type: 'number', label: 'Width', min: 1, max: 20, step: 1, unit: 'mm' },
    thickness: { type: 'number', label: 'Thickness', min: 0.5, max: 10, step: 0.5, unit: 'mm' },
  },

  [ScaffoldType.INTERVERTEBRAL_DISC]: {
    disc_diameter: { type: 'number', label: 'Disc Diameter', min: 20, max: 60, step: 5, unit: 'mm' },
    disc_height: { type: 'number', label: 'Disc Height', min: 3, max: 20, step: 1, unit: 'mm' },
    af_ring_count: { type: 'number', label: 'AF Ring Count', min: 3, max: 10, step: 1 },
    np_diameter: { type: 'number', label: 'NP Diameter', min: 5, max: 25, step: 1, unit: 'mm' },
    af_layer_angle: { type: 'number', label: 'AF Layer Angle', min: 10, max: 45, step: 5, unit: 'deg' },
    fiber_diameter: { type: 'number', label: 'Fiber Diameter', min: 0.05, max: 0.3, step: 0.01, unit: 'mm' },
    np_porosity: { type: 'number', label: 'NP Porosity', min: 0.7, max: 0.95, step: 0.05 },
  },

  [ScaffoldType.HAVERSIAN_BONE]: {
    canal_diameter_um: { type: 'number', label: 'Canal Diameter', min: 30, max: 100, step: 5, unit: 'um' },
    canal_spacing_um: { type: 'number', label: 'Canal Spacing', min: 150, max: 500, step: 25, unit: 'um' },
    cortical_thickness: { type: 'number', label: 'Cortical Thickness', min: 2, max: 10, step: 0.5, unit: 'mm' },
    osteon_pattern: {
      type: 'enum',
      label: 'Osteon Pattern',
      options: [
        { value: 'hexagonal', label: 'Hexagonal' },
        { value: 'random', label: 'Random' },
      ],
    },
    bounding_box: boundingBoxMeta,
  },

  // === Organ Types ===
  [ScaffoldType.HEPATIC_LOBULE]: {
    num_lobules: { type: 'number', label: 'Number of Lobules', min: 1, max: 19, step: 1 },
    lobule_radius: { type: 'number', label: 'Lobule Radius', min: 0.5, max: 3, step: 0.1, unit: 'mm' },
    lobule_height: { type: 'number', label: 'Lobule Height', min: 1, max: 10, step: 0.5, unit: 'mm' },
    wall_thickness: { type: 'number', label: 'Wall Thickness', min: 0.05, max: 0.3, step: 0.025, unit: 'mm' },
    central_vein_radius: { type: 'number', label: 'Central Vein Radius', min: 0.05, max: 0.5, step: 0.025, unit: 'mm' },
    portal_vein_radius: { type: 'number', label: 'Portal Vein Radius', min: 0.05, max: 0.3, step: 0.01, unit: 'mm' },
    show_sinusoids: { type: 'boolean', label: 'Show Sinusoids' },
    sinusoid_radius: { type: 'number', label: 'Sinusoid Radius', min: 0.01, max: 0.1, step: 0.005, unit: 'mm' },
  },

  [ScaffoldType.CARDIAC_PATCH]: {
    fiber_spacing: { type: 'number', label: 'Fiber Spacing', min: 100, max: 500, step: 25, unit: 'um' },
    fiber_diameter: { type: 'number', label: 'Fiber Diameter', min: 50, max: 200, step: 10, unit: 'um' },
    patch_size: {
      type: 'object',
      label: 'Patch Size (mm)',
      properties: {
        x: { type: 'number', label: 'X', min: 1, max: 30, step: 1, unit: 'mm' },
        y: { type: 'number', label: 'Y', min: 1, max: 30, step: 1, unit: 'mm' },
        z: { type: 'number', label: 'Z', min: 0.1, max: 5, step: 0.1, unit: 'mm' },
      },
    },
    layer_count: { type: 'number', label: 'Layer Count', min: 1, max: 5, step: 1 },
    alignment_angle: { type: 'number', label: 'Alignment Angle', min: 0, max: 45, step: 5, unit: 'deg' },
  },

  [ScaffoldType.KIDNEY_TUBULE]: {
    tubule_diameter: { type: 'number', label: 'Tubule Diameter', min: 50, max: 200, step: 10, unit: 'um' },
    wall_thickness: { type: 'number', label: 'Wall Thickness', min: 10, max: 30, step: 2, unit: 'um' },
    convolution_amplitude: { type: 'number', label: 'Convolution Amplitude', min: 200, max: 1000, step: 50, unit: 'um' },
    convolution_frequency: { type: 'number', label: 'Convolution Frequency', min: 1, max: 10, step: 0.5 },
    length: { type: 'number', label: 'Length', min: 3, max: 30, step: 1, unit: 'mm' },
  },

  [ScaffoldType.LUNG_ALVEOLI]: {
    branch_generations: { type: 'number', label: 'Branch Generations', min: 1, max: 5, step: 1 },
    alveoli_diameter: { type: 'number', label: 'Alveoli Diameter', min: 100, max: 300, step: 20, unit: 'um' },
    airway_diameter: { type: 'number', label: 'Airway Diameter', min: 0.5, max: 3, step: 0.1, unit: 'mm' },
    branch_angle: { type: 'number', label: 'Branch Angle', min: 20, max: 60, step: 5, unit: 'deg' },
    bounding_box: boundingBoxMeta,
  },

  [ScaffoldType.PANCREATIC_ISLET]: {
    islet_diameter: { type: 'number', label: 'Islet Diameter', min: 100, max: 300, step: 20, unit: 'um' },
    shell_thickness: { type: 'number', label: 'Shell Thickness', min: 20, max: 100, step: 10, unit: 'um' },
    pore_size: { type: 'number', label: 'Pore Size', min: 10, max: 50, step: 5, unit: 'um' },
    cluster_count: { type: 'number', label: 'Cluster Count', min: 1, max: 20, step: 1 },
    spacing: { type: 'number', label: 'Spacing', min: 150, max: 600, step: 50, unit: 'um' },
  },

  [ScaffoldType.LIVER_SINUSOID]: {
    sinusoid_diameter: { type: 'number', label: 'Sinusoid Diameter', min: 10, max: 30, step: 2, unit: 'um' },
    length: { type: 'number', label: 'Length', min: 2, max: 15, step: 0.5, unit: 'mm' },
    fenestration_size: { type: 'number', label: 'Fenestration Size', min: 0.5, max: 3, step: 0.25, unit: 'um' },
    fenestration_density: { type: 'number', label: 'Fenestration Density', min: 0, max: 1, step: 0.05 },
  },

  // === Soft Tissue Types ===
  [ScaffoldType.MULTILAYER_SKIN]: {
    epidermis_thickness_mm: { type: 'number', label: 'Epidermis Thickness', min: 0.05, max: 0.5, step: 0.05, unit: 'mm' },
    dermis_thickness_mm: { type: 'number', label: 'Dermis Thickness', min: 0.5, max: 5, step: 0.25, unit: 'mm' },
    hypodermis_thickness_mm: { type: 'number', label: 'Hypodermis Thickness', min: 1, max: 10, step: 0.5, unit: 'mm' },
    diameter_mm: { type: 'number', label: 'Diameter', min: 5, max: 30, step: 1, unit: 'mm' },
    pore_gradient: {
      type: 'array',
      label: 'Pore Gradient',
      itemCount: 3,
      itemLabels: ['Epidermis', 'Dermis', 'Hypodermis'],
      min: 0,
      max: 1,
      step: 0.1,
    },
    vascular_channel_diameter_mm: { type: 'number', label: 'Vascular Channel Diameter', min: 0.1, max: 0.5, step: 0.05, unit: 'mm' },
    vascular_channel_count: { type: 'number', label: 'Vascular Channel Count', min: 0, max: 16, step: 1 },
  },

  [ScaffoldType.SKELETAL_MUSCLE]: {
    fiber_diameter_um: { type: 'number', label: 'Fiber Diameter', min: 50, max: 150, step: 5, unit: 'um' },
    fiber_spacing_um: { type: 'number', label: 'Fiber Spacing', min: 75, max: 300, step: 25, unit: 'um' },
    pennation_angle_deg: { type: 'number', label: 'Pennation Angle', min: 0, max: 30, step: 5, unit: 'deg' },
    fascicle_count: { type: 'number', label: 'Fascicle Count', min: 1, max: 10, step: 1 },
    architecture_type: {
      type: 'enum',
      label: 'Architecture Type',
      options: [
        { value: 'parallel', label: 'Parallel' },
        { value: 'unipennate', label: 'Unipennate' },
        { value: 'bipennate', label: 'Bipennate' },
      ],
    },
    length_mm: { type: 'number', label: 'Length', min: 5, max: 50, step: 5, unit: 'mm' },
    width_mm: { type: 'number', label: 'Width', min: 2, max: 20, step: 1, unit: 'mm' },
    height_mm: { type: 'number', label: 'Height', min: 2, max: 20, step: 1, unit: 'mm' },
  },

  [ScaffoldType.CORNEA]: {
    diameter_mm: { type: 'number', label: 'Diameter', min: 8, max: 14, step: 0.5, unit: 'mm' },
    thickness_mm: { type: 'number', label: 'Thickness', min: 0.3, max: 1, step: 0.05, unit: 'mm' },
    radius_of_curvature_mm: { type: 'number', label: 'Radius of Curvature', min: 6, max: 10, step: 0.2, unit: 'mm' },
    lamella_count: { type: 'number', label: 'Lamella Count', min: 2, max: 10, step: 1 },
  },

  [ScaffoldType.ADIPOSE]: {
    cell_size_um: { type: 'number', label: 'Cell Size', min: 100, max: 200, step: 10, unit: 'um' },
    wall_thickness_um: { type: 'number', label: 'Wall Thickness', min: 20, max: 50, step: 5, unit: 'um' },
    vascular_channel_spacing_mm: { type: 'number', label: 'Vascular Spacing', min: 1, max: 5, step: 0.5, unit: 'mm' },
    vascular_channel_diameter_mm: { type: 'number', label: 'Vascular Diameter', min: 0.2, max: 0.6, step: 0.05, unit: 'mm' },
    height_mm: { type: 'number', label: 'Height', min: 2, max: 15, step: 1, unit: 'mm' },
    diameter_mm: { type: 'number', label: 'Diameter', min: 5, max: 30, step: 1, unit: 'mm' },
  },

  // === Tubular Types ===
  [ScaffoldType.BLOOD_VESSEL]: {
    inner_diameter_mm: { type: 'number', label: 'Inner Diameter', min: 2, max: 15, step: 0.5, unit: 'mm' },
    wall_thickness_mm: { type: 'number', label: 'Wall Thickness', min: 0.5, max: 3, step: 0.1, unit: 'mm' },
    layer_ratios: {
      type: 'array',
      label: 'Layer Ratios',
      itemCount: 3,
      itemLabels: ['Intima', 'Media', 'Adventitia'],
      min: 0.05,
      max: 0.8,
      step: 0.05,
      description: 'Must sum to 1.0',
    },
    length_mm: { type: 'number', label: 'Length', min: 10, max: 100, step: 5, unit: 'mm' },
    bifurcation_angle_deg: { type: 'number', label: 'Bifurcation Angle', min: 20, max: 60, step: 5, unit: 'deg' },
  },

  [ScaffoldType.NERVE_CONDUIT]: {
    outer_diameter_mm: { type: 'number', label: 'Outer Diameter', min: 2, max: 8, step: 0.5, unit: 'mm' },
    channel_count: { type: 'number', label: 'Channel Count', min: 1, max: 19, step: 1 },
    channel_diameter_um: { type: 'number', label: 'Channel Diameter', min: 50, max: 500, step: 25, unit: 'um' },
    wall_thickness_mm: { type: 'number', label: 'Wall Thickness', min: 0.3, max: 2, step: 0.1, unit: 'mm' },
    length_mm: { type: 'number', label: 'Length', min: 5, max: 100, step: 5, unit: 'mm' },
  },

  [ScaffoldType.SPINAL_CORD]: {
    cord_diameter_mm: { type: 'number', label: 'Cord Diameter', min: 8, max: 18, step: 1, unit: 'mm' },
    channel_diameter_um: { type: 'number', label: 'Channel Diameter', min: 100, max: 500, step: 50, unit: 'um' },
    channel_count: { type: 'number', label: 'Channel Count', min: 8, max: 48, step: 4 },
    gray_matter_ratio: { type: 'number', label: 'Gray Matter Ratio', min: 0.2, max: 0.6, step: 0.05 },
    length_mm: { type: 'number', label: 'Length', min: 10, max: 100, step: 10, unit: 'mm' },
  },

  [ScaffoldType.BLADDER]: {
    diameter_mm: { type: 'number', label: 'Diameter', min: 40, max: 120, step: 10, unit: 'mm' },
    wall_thickness_mm: { type: 'number', label: 'Wall Thickness', min: 1.5, max: 6, step: 0.5, unit: 'mm' },
    layer_count: { type: 'number', label: 'Layer Count', min: 2, max: 4, step: 1 },
    dome_curvature: { type: 'number', label: 'Dome Curvature', min: 0.3, max: 1, step: 0.1 },
  },

  [ScaffoldType.TRACHEA]: {
    outer_diameter_mm: { type: 'number', label: 'Outer Diameter', min: 12, max: 30, step: 1, unit: 'mm' },
    ring_thickness_mm: { type: 'number', label: 'Ring Thickness', min: 1, max: 5, step: 0.5, unit: 'mm' },
    ring_spacing_mm: { type: 'number', label: 'Ring Spacing', min: 2, max: 7, step: 0.5, unit: 'mm' },
    ring_count: { type: 'number', label: 'Ring Count', min: 3, max: 20, step: 1 },
    posterior_gap_angle_deg: { type: 'number', label: 'Posterior Gap Angle', min: 45, max: 135, step: 15, unit: 'deg' },
  },

  // === Dental Types ===
  [ScaffoldType.DENTIN_PULP]: {
    tooth_height: { type: 'number', label: 'Tooth Height', min: 8, max: 20, step: 1, unit: 'mm' },
    crown_diameter: { type: 'number', label: 'Crown Diameter', min: 6, max: 15, step: 1, unit: 'mm' },
    root_length: { type: 'number', label: 'Root Length', min: 6, max: 20, step: 1, unit: 'mm' },
    root_diameter: { type: 'number', label: 'Root Diameter', min: 2, max: 8, step: 0.5, unit: 'mm' },
    pulp_chamber_size: { type: 'number', label: 'Pulp Chamber Size', min: 0.2, max: 0.7, step: 0.05 },
    dentin_thickness: { type: 'number', label: 'Dentin Thickness', min: 1, max: 5, step: 0.5, unit: 'mm' },
  },

  [ScaffoldType.EAR_AURICLE]: {
    scale_factor: { type: 'number', label: 'Scale Factor', min: 0.5, max: 1.5, step: 0.1 },
    thickness: { type: 'number', label: 'Thickness', min: 1, max: 4, step: 0.5, unit: 'mm' },
    helix_definition: { type: 'number', label: 'Helix Definition', min: 0, max: 1, step: 0.1 },
    antihelix_depth: { type: 'number', label: 'Antihelix Depth', min: 0, max: 1, step: 0.1 },
  },

  [ScaffoldType.NASAL_SEPTUM]: {
    length: { type: 'number', label: 'Length', min: 20, max: 60, step: 5, unit: 'mm' },
    height: { type: 'number', label: 'Height', min: 15, max: 50, step: 5, unit: 'mm' },
    thickness: { type: 'number', label: 'Thickness', min: 1, max: 6, step: 0.5, unit: 'mm' },
    curvature_radius: { type: 'number', label: 'Curvature Radius', min: 30, max: 200, step: 10, unit: 'mm' },
    curve_type: {
      type: 'enum',
      label: 'Curve Type',
      options: [
        { value: 'single', label: 'Single' },
        { value: 's_curve', label: 'S-Curve' },
      ],
    },
  },

  // === Advanced Lattice Types ===
  [ScaffoldType.GYROID]: {
    bounding_box_mm: boundingBoxMeta,
    cell_size_mm: { type: 'number', label: 'Cell Size', min: 0.5, max: 10, step: 0.5, unit: 'mm' },
    wall_thickness_mm: { type: 'number', label: 'Wall Thickness', min: 0.1, max: 2, step: 0.1, unit: 'mm' },
    isovalue: { type: 'number', label: 'Isovalue', min: -1, max: 1, step: 0.1 },
    samples_per_cell: { type: 'number', label: 'Samples per Cell', min: 10, max: 40, step: 5 },
  },

  [ScaffoldType.SCHWARZ_P]: {
    bounding_box_mm: boundingBoxMeta,
    cell_size_mm: { type: 'number', label: 'Cell Size', min: 0.5, max: 10, step: 0.5, unit: 'mm' },
    wall_thickness_mm: { type: 'number', label: 'Wall Thickness', min: 0.1, max: 2, step: 0.1, unit: 'mm' },
    isovalue: { type: 'number', label: 'Isovalue', min: -3, max: 3, step: 0.25 },
    samples_per_cell: { type: 'number', label: 'Samples per Cell', min: 10, max: 40, step: 5 },
  },

  [ScaffoldType.OCTET_TRUSS]: {
    bounding_box_mm: boundingBoxMeta,
    cell_size_mm: { type: 'number', label: 'Cell Size', min: 1, max: 10, step: 0.5, unit: 'mm' },
    strut_diameter_mm: { type: 'number', label: 'Strut Diameter', min: 0.2, max: 2, step: 0.1, unit: 'mm' },
  },

  [ScaffoldType.VORONOI]: {
    bounding_box_mm: boundingBoxMeta,
    cell_count: { type: 'number', label: 'Cell Count', min: 10, max: 100, step: 5 },
    strut_diameter_mm: { type: 'number', label: 'Strut Diameter', min: 0.2, max: 1.5, step: 0.1, unit: 'mm' },
    seed: { type: 'number', label: 'Random Seed', min: 0, max: 9999, step: 1 },
    margin_factor: { type: 'number', label: 'Margin Factor', min: 0.1, max: 0.5, step: 0.05 },
  },

  [ScaffoldType.HONEYCOMB]: {
    bounding_box_mm: boundingBoxMeta,
    cell_size_mm: { type: 'number', label: 'Cell Size', min: 1, max: 10, step: 0.5, unit: 'mm' },
    wall_thickness_mm: { type: 'number', label: 'Wall Thickness', min: 0.2, max: 2, step: 0.1, unit: 'mm' },
  },

  // === Microfluidic Types ===
  [ScaffoldType.ORGAN_ON_CHIP]: {
    channel_width_mm: { type: 'number', label: 'Channel Width', min: 0.1, max: 1, step: 0.05, unit: 'mm' },
    channel_depth_mm: { type: 'number', label: 'Channel Depth', min: 0.05, max: 0.5, step: 0.025, unit: 'mm' },
    chamber_size_mm: {
      type: 'object',
      label: 'Chamber Size (mm)',
      properties: {
        x: { type: 'number', label: 'X', min: 0.5, max: 10, step: 0.5, unit: 'mm' },
        y: { type: 'number', label: 'Y', min: 0.5, max: 10, step: 0.5, unit: 'mm' },
        z: { type: 'number', label: 'Z', min: 0.05, max: 1, step: 0.05, unit: 'mm' },
      },
    },
    chamber_count: { type: 'number', label: 'Chamber Count', min: 1, max: 5, step: 1 },
    inlet_count: { type: 'number', label: 'Inlet Count', min: 1, max: 5, step: 1 },
    chip_size_mm: {
      type: 'object',
      label: 'Chip Size (mm)',
      properties: {
        x: { type: 'number', label: 'X', min: 5, max: 50, step: 5, unit: 'mm' },
        y: { type: 'number', label: 'Y', min: 5, max: 50, step: 5, unit: 'mm' },
        z: { type: 'number', label: 'Z', min: 1, max: 10, step: 0.5, unit: 'mm' },
      },
    },
  },

  [ScaffoldType.GRADIENT_SCAFFOLD]: {
    dimensions_mm: {
      type: 'object',
      label: 'Dimensions (mm)',
      properties: {
        x: { type: 'number', label: 'X', min: 1, max: 50, step: 1, unit: 'mm' },
        y: { type: 'number', label: 'Y', min: 1, max: 50, step: 1, unit: 'mm' },
        z: { type: 'number', label: 'Z', min: 1, max: 50, step: 1, unit: 'mm' },
      },
    },
    gradient_direction: {
      type: 'enum',
      label: 'Gradient Direction',
      options: [
        { value: 'x', label: 'X' },
        { value: 'y', label: 'Y' },
        { value: 'z', label: 'Z' },
      ],
    },
    start_porosity: { type: 'number', label: 'Start Porosity', min: 0, max: 1, step: 0.05 },
    end_porosity: { type: 'number', label: 'End Porosity', min: 0, max: 1, step: 0.05 },
    gradient_type: {
      type: 'enum',
      label: 'Gradient Type',
      options: [
        { value: 'linear', label: 'Linear' },
        { value: 'exponential', label: 'Exponential' },
        { value: 'sigmoid', label: 'Sigmoid' },
      ],
    },
    pore_base_size_mm: { type: 'number', label: 'Pore Base Size', min: 0.2, max: 2, step: 0.1, unit: 'mm' },
    grid_spacing_mm: { type: 'number', label: 'Grid Spacing', min: 0.5, max: 5, step: 0.25, unit: 'mm' },
  },

  [ScaffoldType.PERFUSABLE_NETWORK]: {
    inlet_diameter_mm: { type: 'number', label: 'Inlet Diameter', min: 0.5, max: 5, step: 0.25, unit: 'mm' },
    branch_generations: { type: 'number', label: 'Branch Generations', min: 1, max: 5, step: 1 },
    murray_ratio: { type: 'number', label: "Murray's Ratio", min: 0.6, max: 0.9, step: 0.01 },
    network_type: {
      type: 'enum',
      label: 'Network Type',
      options: [
        { value: 'arterial', label: 'Arterial' },
        { value: 'venous', label: 'Venous' },
        { value: 'capillary', label: 'Capillary' },
      ],
    },
    bounding_box_mm: boundingBoxMeta,
    branching_angle_deg: { type: 'number', label: 'Branching Angle', min: 20, max: 60, step: 5, unit: 'deg' },
  },
};

/**
 * Get human-readable label for a scaffold type
 */
export function getScaffoldTypeLabel(type: ScaffoldType): string {
  const labels: Record<ScaffoldType, string> = {
    [ScaffoldType.VASCULAR_NETWORK]: 'Vascular Network',
    [ScaffoldType.POROUS_DISC]: 'Porous Disc',
    [ScaffoldType.TUBULAR_CONDUIT]: 'Tubular Conduit',
    [ScaffoldType.LATTICE]: 'Lattice',
    [ScaffoldType.PRIMITIVE]: 'Primitive',
    [ScaffoldType.TRABECULAR_BONE]: 'Trabecular Bone',
    [ScaffoldType.OSTEOCHONDRAL]: 'Osteochondral',
    [ScaffoldType.ARTICULAR_CARTILAGE]: 'Articular Cartilage',
    [ScaffoldType.MENISCUS]: 'Meniscus',
    [ScaffoldType.TENDON_LIGAMENT]: 'Tendon/Ligament',
    [ScaffoldType.INTERVERTEBRAL_DISC]: 'Intervertebral Disc',
    [ScaffoldType.HAVERSIAN_BONE]: 'Haversian Bone',
    [ScaffoldType.HEPATIC_LOBULE]: 'Hepatic Lobule',
    [ScaffoldType.CARDIAC_PATCH]: 'Cardiac Patch',
    [ScaffoldType.KIDNEY_TUBULE]: 'Kidney Tubule',
    [ScaffoldType.LUNG_ALVEOLI]: 'Lung Alveoli',
    [ScaffoldType.PANCREATIC_ISLET]: 'Pancreatic Islet',
    [ScaffoldType.LIVER_SINUSOID]: 'Liver Sinusoid',
    [ScaffoldType.MULTILAYER_SKIN]: 'Multilayer Skin',
    [ScaffoldType.SKELETAL_MUSCLE]: 'Skeletal Muscle',
    [ScaffoldType.CORNEA]: 'Cornea',
    [ScaffoldType.ADIPOSE]: 'Adipose',
    [ScaffoldType.BLOOD_VESSEL]: 'Blood Vessel',
    [ScaffoldType.NERVE_CONDUIT]: 'Nerve Conduit',
    [ScaffoldType.SPINAL_CORD]: 'Spinal Cord',
    [ScaffoldType.BLADDER]: 'Bladder',
    [ScaffoldType.TRACHEA]: 'Trachea',
    [ScaffoldType.DENTIN_PULP]: 'Dentin-Pulp',
    [ScaffoldType.EAR_AURICLE]: 'Ear Auricle',
    [ScaffoldType.NASAL_SEPTUM]: 'Nasal Septum',
    [ScaffoldType.GYROID]: 'Gyroid (TPMS)',
    [ScaffoldType.SCHWARZ_P]: 'Schwarz P (TPMS)',
    [ScaffoldType.OCTET_TRUSS]: 'Octet Truss',
    [ScaffoldType.VORONOI]: 'Voronoi',
    [ScaffoldType.HONEYCOMB]: 'Honeycomb',
    [ScaffoldType.ORGAN_ON_CHIP]: 'Organ-on-Chip',
    [ScaffoldType.GRADIENT_SCAFFOLD]: 'Gradient Scaffold',
    [ScaffoldType.PERFUSABLE_NETWORK]: 'Perfusable Network',
  };
  return labels[type] || type;
}
