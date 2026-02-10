'use client';

import { useCallback } from 'react';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { ChevronDown, Layers } from 'lucide-react';
import { useTilingStore } from '@/lib/store/tilingStore';
import { tileScaffold } from '@/lib/api/tiling';
import type { TargetShape, TilingMode, TileRequest } from '@/lib/types/tiling';

interface TilingPanelProps {
  scaffoldId: string | null;
  onTilingComplete: (result: {
    mesh: { vertices: number[]; indices: number[]; normals: number[] };
    stlBase64: string;
    scaffoldId: string;
    stats: { triangle_count: number; volume_mm3: number; generation_time_ms: number };
  }) => void;
}

const SHAPE_LABELS: Record<TargetShape, string> = {
  sphere: 'Sphere',
  ellipsoid: 'Ellipsoid',
  torus: 'Torus',
  cylinder: 'Cylinder',
  superellipsoid: 'Superellipsoid',
};

export function TilingPanel({ scaffoldId, onTilingComplete }: TilingPanelProps) {
  const {
    isOpen, setIsOpen,
    targetShape, setTargetShape,
    mode, setMode,
    radius, setRadius,
    radiusX, setRadiusX,
    radiusY, setRadiusY,
    radiusZ, setRadiusZ,
    majorRadius, setMajorRadius,
    minorRadius, setMinorRadius,
    height, setHeight,
    exponentN, setExponentN,
    exponentE, setExponentE,
    numTilesU, setNumTilesU,
    numTilesV, setNumTilesV,
    numLayers, setNumLayers,
    layerSpacingMm, setLayerSpacingMm,
    refineEdgeLengthMm, setRefineEdgeLengthMm,
    isTiling, setIsTiling,
    tilingError, setTilingError,
  } = useTilingStore();

  const handleTile = useCallback(async () => {
    if (!scaffoldId) return;

    setIsTiling(true);
    setTilingError(null);

    try {
      const request: TileRequest = {
        scaffold_id: scaffoldId,
        target_shape: targetShape,
        mode,
        num_tiles_u: numTilesU,
        num_tiles_v: numTilesV,
        refine_edge_length_mm: refineEdgeLengthMm,
      };

      // Add shape-specific dimensions
      if (targetShape === 'sphere') {
        request.radius = radius;
      } else if (targetShape === 'ellipsoid') {
        request.radius_x = radiusX;
        request.radius_y = radiusY;
        request.radius_z = radiusZ;
      } else if (targetShape === 'torus') {
        request.major_radius = majorRadius;
        request.minor_radius = minorRadius;
      } else if (targetShape === 'cylinder') {
        request.radius = radius;
        request.height = height;
      } else if (targetShape === 'superellipsoid') {
        request.radius_x = radiusX;
        request.radius_y = radiusY;
        request.radius_z = radiusZ;
        request.exponent_n = exponentN;
        request.exponent_e = exponentE;
      }

      // Volume mode params
      if (mode === 'volume') {
        request.num_layers = numLayers;
        request.layer_spacing_mm = layerSpacingMm;
      }

      const result = await tileScaffold(request);

      onTilingComplete({
        mesh: result.mesh,
        stlBase64: result.stl_base64,
        scaffoldId: result.scaffold_id,
        stats: {
          triangle_count: result.stats.triangle_count,
          volume_mm3: result.stats.volume_mm3,
          generation_time_ms: result.stats.generation_time_ms,
        },
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Tiling failed';
      setTilingError(message);
    } finally {
      setIsTiling(false);
    }
  }, [
    scaffoldId, targetShape, mode, radius, radiusX, radiusY, radiusZ,
    majorRadius, minorRadius, height, exponentN, exponentE,
    numTilesU, numTilesV, numLayers, layerSpacingMm, refineEdgeLengthMm,
    setIsTiling, setTilingError, onTilingComplete,
  ]);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger className="flex items-center justify-between w-full p-4 border-t border-emerald-500/20 hover:bg-emerald-500/5 transition-colors">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <span className="font-semibold text-sm text-slate-200">Tile onto Surface</span>
        </div>
        <ChevronDown
          className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </CollapsibleTrigger>

      <CollapsibleContent>
        <div className="p-4 space-y-4 border-t border-emerald-500/10">
          {!scaffoldId && (
            <p className="text-xs text-amber-400">
              Generate a scaffold first, then tile it onto a surface.
            </p>
          )}

          {/* Target Shape */}
          <div className="space-y-2">
            <Label className="text-slate-300">Target Shape</Label>
            <Select value={targetShape} onValueChange={(v) => setTargetShape(v as TargetShape)}>
              <SelectTrigger className="bg-slate-900 border-slate-700 text-slate-200">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(SHAPE_LABELS).map(([value, label]) => (
                  <SelectItem key={value} value={value}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Shape-specific dimensions */}
          {targetShape === 'sphere' && (
            <SliderControl
              label="Radius (mm)"
              value={radius}
              onChange={setRadius}
              min={1}
              max={100}
              step={0.5}
            />
          )}

          {targetShape === 'ellipsoid' && (
            <>
              <SliderControl label="X Radius (mm)" value={radiusX} onChange={setRadiusX} min={1} max={100} step={0.5} />
              <SliderControl label="Y Radius (mm)" value={radiusY} onChange={setRadiusY} min={1} max={100} step={0.5} />
              <SliderControl label="Z Radius (mm)" value={radiusZ} onChange={setRadiusZ} min={1} max={100} step={0.5} />
            </>
          )}

          {targetShape === 'torus' && (
            <>
              <SliderControl label="Major Radius (mm)" value={majorRadius} onChange={setMajorRadius} min={5} max={100} step={0.5} />
              <SliderControl label="Minor Radius (mm)" value={minorRadius} onChange={setMinorRadius} min={1} max={50} step={0.5} />
            </>
          )}

          {targetShape === 'cylinder' && (
            <>
              <SliderControl label="Radius (mm)" value={radius} onChange={setRadius} min={1} max={100} step={0.5} />
              <SliderControl label="Height (mm)" value={height} onChange={setHeight} min={1} max={200} step={1} />
            </>
          )}

          {targetShape === 'superellipsoid' && (
            <>
              <SliderControl label="X Radius (mm)" value={radiusX} onChange={setRadiusX} min={1} max={100} step={0.5} />
              <SliderControl label="Y Radius (mm)" value={radiusY} onChange={setRadiusY} min={1} max={100} step={0.5} />
              <SliderControl label="Z Radius (mm)" value={radiusZ} onChange={setRadiusZ} min={1} max={100} step={0.5} />
              <SliderControl label="Exponent N (roundness)" value={exponentN} onChange={setExponentN} min={0.1} max={4.0} step={0.1} />
              <SliderControl label="Exponent E (squareness)" value={exponentE} onChange={setExponentE} min={0.1} max={4.0} step={0.1} />
            </>
          )}

          {/* Tile counts */}
          <SliderControl label="Tiles U" value={numTilesU} onChange={setNumTilesU} min={1} max={20} step={1} />
          <SliderControl label="Tiles V" value={numTilesV} onChange={setNumTilesV} min={1} max={20} step={1} />

          {/* Mode toggle */}
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <Label className="text-slate-300">Volume Fill</Label>
              <span className="text-xs text-slate-500">Multiple radial layers</span>
            </div>
            <Switch
              checked={mode === 'volume'}
              onCheckedChange={(v) => setMode(v ? 'volume' : 'surface')}
              className="data-[state=checked]:bg-emerald-500"
            />
          </div>

          {/* Volume mode controls */}
          {mode === 'volume' && (
            <>
              <SliderControl label="Layers" value={numLayers} onChange={setNumLayers} min={1} max={10} step={1} />
              <SliderControl label="Layer Spacing (mm)" value={layerSpacingMm} onChange={setLayerSpacingMm} min={0.1} max={10} step={0.1} />
            </>
          )}

          {/* Mesh quality */}
          <SliderControl
            label="Edge Length (mm)"
            value={refineEdgeLengthMm}
            onChange={setRefineEdgeLengthMm}
            min={0.1}
            max={5.0}
            step={0.1}
          />

          {/* Error */}
          {tilingError && (
            <p className="text-xs text-red-400 bg-red-500/10 rounded p-2">{tilingError}</p>
          )}

          {/* Tile button */}
          <Button
            onClick={handleTile}
            disabled={!scaffoldId || isTiling}
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white"
          >
            <Layers className="w-4 h-4 mr-2" />
            {isTiling ? 'Tiling...' : 'Tile onto Surface'}
          </Button>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}

/** Reusable slider row with label and current value display. */
function SliderControl({
  label,
  value,
  onChange,
  min,
  max,
  step,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number;
  max: number;
  step: number;
}) {
  const display = step >= 1 ? value : value.toFixed(1);

  return (
    <div className="space-y-2">
      <div className="flex justify-between">
        <Label className="text-slate-300">{label}</Label>
        <span className="text-sm text-slate-500">{display}</span>
      </div>
      <Slider
        value={[value]}
        onValueChange={([v]) => onChange(v)}
        min={min}
        max={max}
        step={step}
      />
    </div>
  );
}
