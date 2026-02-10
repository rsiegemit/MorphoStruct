'use client';

import * as React from 'react';
import { ScaffoldType } from '@/lib/types/scaffolds';
import { Label } from '@/components/ui/label';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown, ChevronRight, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ScaffoldItem {
  value: ScaffoldType;
  label: string;
  description: string;
}

// Categories based on audit logic from docs/audit/INDEX.md
// Categories and entries sorted alphabetically
const SCAFFOLD_CATEGORIES: Record<string, ScaffoldItem[]> = {
  'Dental': [
    { value: ScaffoldType.DENTIN_PULP, label: 'Dentin/Pulp', description: 'Tooth dentin and pulp chamber' },
    { value: ScaffoldType.EAR_AURICLE, label: 'Ear Auricle', description: 'External ear cartilage scaffold' },
    { value: ScaffoldType.NASAL_SEPTUM, label: 'Nasal Septum', description: 'Nasal cartilage partition' },
  ],
  'Lattice': [
    { value: ScaffoldType.LATTICE, label: 'Basic Lattice', description: 'Basic 3D lattice structure' },
    { value: ScaffoldType.GYROID, label: 'Gyroid', description: 'Triply periodic minimal surface (TPMS)' },
    { value: ScaffoldType.HONEYCOMB, label: 'Honeycomb', description: 'Hexagonal cell structure' },
    { value: ScaffoldType.OCTET_TRUSS, label: 'Octet Truss', description: 'High-strength lattice framework' },
    { value: ScaffoldType.SCHWARZ_P, label: 'Schwarz P', description: 'Primitive TPMS with cubic symmetry' },
    { value: ScaffoldType.VORONOI, label: 'Voronoi', description: 'Natural tessellation pattern' },
  ],
  'Legacy': [
    { value: ScaffoldType.POROUS_DISC, label: 'Porous Disc', description: 'Flat disc with uniform porosity' },
    { value: ScaffoldType.PRIMITIVE, label: 'Primitive', description: 'Simple geometric shape' },
    { value: ScaffoldType.VASCULAR_NETWORK, label: 'Vascular Network', description: 'Branching vascular channel network' },
  ],
  'Microfluidic': [
    { value: ScaffoldType.GRADIENT_SCAFFOLD, label: 'Gradient Scaffold', description: 'Spatially graded properties' },
    { value: ScaffoldType.ORGAN_ON_CHIP, label: 'Organ-on-Chip', description: 'Microfluidic organ model' },
    { value: ScaffoldType.PERFUSABLE_NETWORK, label: 'Perfusable Network', description: 'Flow-optimized channel system' },
  ],
  'Organ': [
    { value: ScaffoldType.CARDIAC_PATCH, label: 'Cardiac Patch', description: 'Myocardial tissue scaffold' },
    { value: ScaffoldType.HEPATIC_LOBULE, label: 'Hepatic Lobule', description: 'Liver functional unit structure' },
    { value: ScaffoldType.KIDNEY_TUBULE, label: 'Kidney Tubule', description: 'Renal tubular network' },
    { value: ScaffoldType.LIVER_SINUSOID, label: 'Liver Sinusoid', description: 'Hepatic sinusoidal network' },
    { value: ScaffoldType.LUNG_ALVEOLI, label: 'Lung Alveoli', description: 'Alveolar gas exchange structure' },
    { value: ScaffoldType.PANCREATIC_ISLET, label: 'Pancreatic Islet', description: 'Islet of Langerhans scaffold' },
  ],
  'Skeletal': [
    { value: ScaffoldType.ARTICULAR_CARTILAGE, label: 'Articular Cartilage', description: 'Joint surface cartilage structure' },
    { value: ScaffoldType.HAVERSIAN_BONE, label: 'Haversian Bone', description: 'Compact bone with osteon structure' },
    { value: ScaffoldType.INTERVERTEBRAL_DISC, label: 'Intervertebral Disc', description: 'Spinal disc with annulus and nucleus' },
    { value: ScaffoldType.MENISCUS, label: 'Meniscus', description: 'Fibrocartilaginous knee structure' },
    { value: ScaffoldType.OSTEOCHONDRAL, label: 'Osteochondral', description: 'Bone-cartilage interface scaffold' },
    { value: ScaffoldType.TENDON_LIGAMENT, label: 'Tendon/Ligament', description: 'Aligned fibrous tissue scaffold' },
    { value: ScaffoldType.TRABECULAR_BONE, label: 'Trabecular Bone', description: 'Cancellous bone architecture' },
  ],
  'Soft Tissue': [
    { value: ScaffoldType.ADIPOSE, label: 'Adipose', description: 'Fat tissue scaffold' },
    { value: ScaffoldType.CORNEA, label: 'Cornea', description: 'Transparent lamellar eye tissue' },
    { value: ScaffoldType.MULTILAYER_SKIN, label: 'Multilayer Skin', description: 'Epidermis and dermis layers' },
    { value: ScaffoldType.SKELETAL_MUSCLE, label: 'Skeletal Muscle', description: 'Aligned myofiber structure' },
  ],
  'Tubular': [
    { value: ScaffoldType.BLADDER, label: 'Bladder', description: 'Urinary bladder wall scaffold' },
    { value: ScaffoldType.BLOOD_VESSEL, label: 'Blood Vessel', description: 'Vascular graft with wall layers' },
    { value: ScaffoldType.NERVE_CONDUIT, label: 'Nerve Conduit', description: 'Neural guidance channel' },
    { value: ScaffoldType.SPINAL_CORD, label: 'Spinal Cord', description: 'Central nervous tissue scaffold' },
    { value: ScaffoldType.TRACHEA, label: 'Trachea', description: 'Airway cartilage ring structure' },
    { value: ScaffoldType.TUBULAR_CONDUIT, label: 'Tubular Conduit', description: 'Hollow tube for tissue guidance' },
    { value: ScaffoldType.VASCULAR_PERFUSION_DISH, label: 'Vascular Perfusion Dish', description: 'Collision-aware branching vascular network' },
  ],
};

// Build a map from value to label for quick lookup
const VALUE_TO_LABEL: Record<ScaffoldType, string> = {} as Record<ScaffoldType, string>;
Object.values(SCAFFOLD_CATEGORIES).forEach(items => {
  items.forEach(item => {
    VALUE_TO_LABEL[item.value] = item.label;
  });
});

interface ScaffoldTypeSelectorProps {
  value: ScaffoldType;
  onChange: (value: ScaffoldType) => void;
}

export function ScaffoldTypeSelector({ value, onChange }: ScaffoldTypeSelectorProps) {
  const [open, setOpen] = React.useState(false);
  const [openCategories, setOpenCategories] = React.useState<Set<string>>(new Set());

  const toggleCategory = (category: string) => {
    setOpenCategories(prev => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  const handleSelect = (scaffoldValue: ScaffoldType) => {
    onChange(scaffoldValue);
    setOpen(false);
  };

  const selectedLabel = VALUE_TO_LABEL[value] || value;

  return (
    <div className="space-y-2">
      <Label>Scaffold Type</Label>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <button
            type="button"
            role="combobox"
            aria-expanded={open}
            className="flex h-10 w-full items-center justify-between rounded-md border border-slate-300 bg-white px-3 py-2 text-sm ring-offset-white focus:outline-none focus:ring-2 focus:ring-slate-950 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:ring-offset-slate-950"
          >
            <span>{selectedLabel}</span>
            <ChevronDown className="h-4 w-4 opacity-50" />
          </button>
        </PopoverTrigger>
        <PopoverContent className="w-80 max-h-96 overflow-y-auto p-1">
          {Object.entries(SCAFFOLD_CATEGORIES).map(([category, items]) => {
            const isOpen = openCategories.has(category);
            return (
              <Collapsible
                key={category}
                open={isOpen}
                onOpenChange={() => toggleCategory(category)}
              >
                <CollapsibleTrigger className="flex w-full items-center justify-between px-2 py-2 text-sm font-semibold hover:bg-slate-100 rounded-sm dark:hover:bg-slate-700">
                  <span className="flex items-center gap-2">
                    <ChevronRight
                      className={cn(
                        "h-4 w-4 transition-transform duration-200",
                        isOpen && "rotate-90"
                      )}
                    />
                    {category}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    ({items.length})
                  </span>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <div className="pl-4">
                    {items.map((item) => {
                      const isSelected = value === item.value;
                      return (
                        <button
                          key={item.value}
                          type="button"
                          onClick={() => handleSelect(item.value)}
                          className={cn(
                            "flex w-full items-start gap-2 px-2 py-1.5 text-sm rounded-sm text-left",
                            "hover:bg-slate-100 dark:hover:bg-slate-700",
                            isSelected && "bg-slate-100 dark:bg-slate-700"
                          )}
                        >
                          <span className="flex h-4 w-4 shrink-0 items-center justify-center mt-0.5">
                            {isSelected && <Check className="h-4 w-4" />}
                          </span>
                          <div className="flex flex-col">
                            <span>{item.label}</span>
                            <span className="text-xs text-slate-500 dark:text-slate-400">
                              {item.description}
                            </span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </CollapsibleContent>
              </Collapsible>
            );
          })}
        </PopoverContent>
      </Popover>
    </div>
  );
}
