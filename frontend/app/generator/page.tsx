'use client';

import { useCallback, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Viewport } from '@/components/viewer';
import { ParameterPanel } from '@/components/controls';
import { ChatPanel } from '@/components/chat';
import { ExportPanel } from '@/components/export';
import { useScaffoldStore, useChatStore } from '@/lib/store';
import { useAuthStore } from '@/lib/store/authStore';
import { generateScaffold, exportSTL, downloadBlob, sendChatMessage } from '@/lib/api';
import { ScaffoldType } from '@/lib/types/scaffold';
import { NavHeader } from '@/components/NavHeader';

export default function GeneratorPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Scaffold store
  const {
    scaffoldType,
    setScaffoldType,
    params,
    setParams,
    resetParams,
    meshData,
    setMeshData,
    isGenerating,
    setIsGenerating,
    validation,
    setValidation,
    stats,
    setStats,
    scaffoldId,
    setScaffoldId,
  } = useScaffoldStore();

  // Chat store
  const {
    messages,
    addMessage,
    isLoading: chatLoading,
    setIsLoading: setChatLoading,
    suggestions,
    setSuggestions,
    getConversationHistory,
  } = useChatStore();

  // Export state
  const [isExporting, setIsExporting] = useState(false);

  // Handle scaffold generation
  const handleGenerate = useCallback(async () => {
    setIsGenerating(true);
    try {
      const result = await generateScaffold(scaffoldType, params);
      setMeshData(result.mesh);
      setValidation(result.validation);
      setStats(result.stats);
      setScaffoldId(result.scaffold_id);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  }, [scaffoldType, params, setIsGenerating, setMeshData, setValidation, setStats, setScaffoldId]);

  // Handle export
  const handleExport = useCallback(async (format: 'binary' | 'ascii') => {
    if (!scaffoldId) return;
    setIsExporting(true);
    try {
      const blob = await exportSTL(scaffoldId, format);
      const filename = `scaffold_${scaffoldType}_${Date.now()}.stl`;
      downloadBlob(blob, filename);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  }, [scaffoldId, scaffoldType]);

  // Handle chat messages
  const handleSendMessage = useCallback(async (message: string) => {
    addMessage({ role: 'user', content: message });
    setChatLoading(true);

    try {
      const response = await sendChatMessage(
        message,
        getConversationHistory(),
        { type: scaffoldType, ...params }
      );

      addMessage({
        role: 'assistant',
        content: response.message,
        suggestions: response.suggestions,
      });

      setSuggestions(response.suggestions);

      // If action is generate, update params and generate
      if (response.action === 'generate' && response.suggested_params) {
        const { type, ...newParams } = response.suggested_params;
        if (type && type !== scaffoldType) {
          setScaffoldType(type as ScaffoldType);
        }
        setParams({ ...params, ...newParams });
        // Auto-generate after param update
        setTimeout(() => handleGenerate(), 100);
      }
    } catch (error) {
      console.error('Chat failed:', error);
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      });
    } finally {
      setChatLoading(false);
    }
  }, [addMessage, setChatLoading, getConversationHistory, scaffoldType, params,
      setSuggestions, setScaffoldType, setParams, handleGenerate]);

  // Handle scaffold type change
  const handleScaffoldTypeChange = useCallback((type: ScaffoldType) => {
    setScaffoldType(type);
  }, [setScaffoldType]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col bg-black">
      <NavHeader currentPage="generator" />

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left sidebar */}
        <aside className="w-80 border-r border-emerald-500/20 flex flex-col overflow-hidden shrink-0 bg-black/50">
          {/* Parameter Panel */}
          <div className="flex-1 overflow-y-auto">
            <ParameterPanel
              scaffoldType={scaffoldType}
              onScaffoldTypeChange={handleScaffoldTypeChange}
              params={params}
              onParamsChange={setParams}
              onGenerate={handleGenerate}
              onReset={resetParams}
              isGenerating={isGenerating}
            />
          </div>

          {/* Chat Panel */}
          <div className="border-t border-emerald-500/20">
            <ChatPanel
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={chatLoading}
              suggestions={suggestions}
            />
          </div>
        </aside>

        {/* Right content area */}
        <div className="flex-1 flex flex-col overflow-hidden p-4 gap-4 bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950">
          {/* 3D Viewport */}
          <div className="flex-1 min-h-0">
            <Viewport
              meshData={meshData || undefined}
              isLoading={isGenerating}
            />
          </div>

          {/* Export Panel */}
          <div className="h-auto shrink-0">
            <ExportPanel
              scaffoldId={scaffoldId}
              validation={validation}
              stats={stats}
              onExport={handleExport}
              isExporting={isExporting}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
