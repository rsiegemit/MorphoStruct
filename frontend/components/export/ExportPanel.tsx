'use client';

import { useState } from 'react';
import { Download, FileType, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ValidationSummary } from './ValidationSummary';

interface ExportPanelProps {
  scaffoldId: string | null;
  validation: {
    is_valid: boolean;
    is_printable: boolean;
    warnings: string[];
    errors: string[];
  } | null;
  stats: {
    triangle_count: number;
    volume_mm3: number;
    generation_time_ms: number;
  } | null;
  onExport: (format: 'binary' | 'ascii') => void;
  onSave?: (name: string) => void;
  isExporting?: boolean;
  isSaving?: boolean;
}

export function ExportPanel({
  scaffoldId,
  validation,
  stats,
  onExport,
  onSave,
  isExporting = false,
  isSaving = false,
}: ExportPanelProps) {
  const canExport = !!scaffoldId;
  const [saveName, setSaveName] = useState('');
  const [showSaveInput, setShowSaveInput] = useState(false);

  const handleSave = () => {
    if (!saveName.trim() || !onSave) return;
    onSave(saveName.trim());
    setSaveName('');
    setShowSaveInput(false);
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-4 space-y-4">
      <h3 className="font-semibold flex items-center gap-2">
        <FileType className="w-5 h-5 text-blue-500" />
        Export Scaffold
      </h3>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="bg-slate-50 dark:bg-slate-700/50 p-2 rounded">
            <div className="text-slate-500 dark:text-slate-400">Triangles</div>
            <div className="font-medium">{stats.triangle_count.toLocaleString()}</div>
          </div>
          <div className="bg-slate-50 dark:bg-slate-700/50 p-2 rounded">
            <div className="text-slate-500 dark:text-slate-400">Volume</div>
            <div className="font-medium">{stats.volume_mm3.toFixed(2)} mm³</div>
          </div>
          <div className="bg-slate-50 dark:bg-slate-700/50 p-2 rounded col-span-2">
            <div className="text-slate-500 dark:text-slate-400">Generation Time</div>
            <div className="font-medium">{(stats.generation_time_ms / 1000).toFixed(2)}s</div>
          </div>
        </div>
      )}

      {/* Validation Summary */}
      {validation && (
        <ValidationSummary validation={validation} />
      )}

      {/* Export Buttons */}
      <div className="flex gap-2">
        <Button
          onClick={() => onExport('binary')}
          disabled={!canExport || isExporting}
          className="flex-1"
        >
          <Download className="w-4 h-4 mr-2" />
          {isExporting ? 'Exporting...' : 'STL (Binary)'}
        </Button>
        <Button
          onClick={() => onExport('ascii')}
          disabled={!canExport || isExporting}
          variant="outline"
          className="flex-1"
        >
          <Download className="w-4 h-4 mr-2" />
          STL (ASCII)
        </Button>
      </div>

      {/* Save to Library */}
      {onSave && canExport && (
        <>
          {showSaveInput ? (
            <div className="flex gap-2">
              <input
                type="text"
                value={saveName}
                onChange={(e) => setSaveName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSave()}
                placeholder="Scaffold name..."
                className="flex-1 px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
              <Button
                onClick={handleSave}
                disabled={!saveName.trim() || isSaving}
                size="sm"
              >
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
              <Button
                onClick={() => { setShowSaveInput(false); setSaveName(''); }}
                variant="outline"
                size="sm"
              >
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              onClick={() => setShowSaveInput(true)}
              variant="outline"
              className="w-full"
              disabled={isSaving}
            >
              <Save className="w-4 h-4 mr-2" />
              Save to Library
            </Button>
          )}
        </>
      )}

      {!scaffoldId && (
        <p className="text-sm text-slate-500 text-center">
          Generate a scaffold to enable export
        </p>
      )}
    </div>
  );
}
