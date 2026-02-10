import { create } from 'zustand';
import { TargetShape, TilingMode } from '../types/tiling';

interface TilingState {
  // Panel visibility
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;

  // Target surface
  targetShape: TargetShape;
  setTargetShape: (shape: TargetShape) => void;

  // Mode
  mode: TilingMode;
  setMode: (mode: TilingMode) => void;

  // Sphere / cylinder dimensions
  radius: number;
  setRadius: (r: number) => void;

  // Ellipsoid dimensions
  radiusX: number;
  setRadiusX: (r: number) => void;
  radiusY: number;
  setRadiusY: (r: number) => void;
  radiusZ: number;
  setRadiusZ: (r: number) => void;

  // Torus dimensions
  majorRadius: number;
  setMajorRadius: (r: number) => void;
  minorRadius: number;
  setMinorRadius: (r: number) => void;

  // Cylinder / superellipsoid height
  height: number;
  setHeight: (h: number) => void;

  // Superellipsoid exponents
  exponentN: number;
  setExponentN: (n: number) => void;
  exponentE: number;
  setExponentE: (e: number) => void;

  // Tiling layout
  numTilesU: number;
  setNumTilesU: (n: number) => void;
  numTilesV: number;
  setNumTilesV: (n: number) => void;

  // Volume mode
  numLayers: number;
  setNumLayers: (n: number) => void;
  layerSpacingMm: number;
  setLayerSpacingMm: (s: number) => void;

  // Mesh quality
  refineEdgeLengthMm: number;
  setRefineEdgeLengthMm: (l: number) => void;

  // Tiling execution state
  isTiling: boolean;
  setIsTiling: (tiling: boolean) => void;
  tilingError: string | null;
  setTilingError: (error: string | null) => void;

  // Reset
  resetTiling: () => void;
}

const DEFAULTS = {
  targetShape: 'sphere' as TargetShape,
  mode: 'surface' as TilingMode,
  radius: 10,
  radiusX: 10,
  radiusY: 8,
  radiusZ: 6,
  majorRadius: 15,
  minorRadius: 5,
  height: 20,
  exponentN: 1.0,
  exponentE: 1.0,
  numTilesU: 4,
  numTilesV: 4,
  numLayers: 1,
  layerSpacingMm: 1.0,
  refineEdgeLengthMm: 0.5,
};

export const useTilingStore = create<TilingState>((set) => ({
  isOpen: false,
  setIsOpen: (isOpen) => set({ isOpen }),

  ...DEFAULTS,

  setTargetShape: (targetShape) => set({ targetShape }),
  setMode: (mode) => set({ mode }),
  setRadius: (radius) => set({ radius }),
  setRadiusX: (radiusX) => set({ radiusX }),
  setRadiusY: (radiusY) => set({ radiusY }),
  setRadiusZ: (radiusZ) => set({ radiusZ }),
  setMajorRadius: (majorRadius) => set({ majorRadius }),
  setMinorRadius: (minorRadius) => set({ minorRadius }),
  setHeight: (height) => set({ height }),
  setExponentN: (exponentN) => set({ exponentN }),
  setExponentE: (exponentE) => set({ exponentE }),
  setNumTilesU: (numTilesU) => set({ numTilesU }),
  setNumTilesV: (numTilesV) => set({ numTilesV }),
  setNumLayers: (numLayers) => set({ numLayers }),
  setLayerSpacingMm: (layerSpacingMm) => set({ layerSpacingMm }),
  setRefineEdgeLengthMm: (refineEdgeLengthMm) => set({ refineEdgeLengthMm }),

  isTiling: false,
  setIsTiling: (isTiling) => set({ isTiling }),
  tilingError: null,
  setTilingError: (tilingError) => set({ tilingError }),

  resetTiling: () => set({ ...DEFAULTS, isTiling: false, tilingError: null }),
}));
