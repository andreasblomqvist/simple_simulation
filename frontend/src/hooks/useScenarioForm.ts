/**
 * Scenario Form Hook
 * 
 * Custom hook for managing scenario creation/editing workflow.
 * Bridges ScenarioService to UI components with state management.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  ScenarioService, 
  type ScenarioWorkflowState, 
  type ScenarioFormData 
} from '../services';
import type { ScenarioDefinition } from '../types/unified-data-structures';
import { showMessage } from '../utils/message';

export interface UseScenarioFormOptions {
  onComplete?: () => void;
  onCancel?: () => void;
  initialScenario?: Partial<ScenarioDefinition>;
  editingId?: string;
}

export interface UseScenarioFormReturn {
  // State
  state: ScenarioWorkflowState;
  
  // Navigation
  current: number;
  steps: Array<{ title: string; description: string }>;
  progressPercentage: number;
  
  // Refs for component communication
  baselineGridRef: React.RefObject<any>;
  leversRef: React.RefObject<any>;
  
  // Actions
  handleDetailsNext: (data: { scenario: ScenarioDefinition }) => void;
  handleBaselineNext: (data: any) => void;
  handleBaselineStepNext: () => void;
  handleBack: () => void;
  handleLeversSave: () => Promise<void>;
  handleRunSimulation: () => Promise<void>;
  
  // Utilities
  isEditing: boolean;
  editingId?: string;
}

const WIZARD_STEPS = [
  { 
    title: 'Scenario Details',
    description: 'Define basic scenario information'
  },
  { 
    title: 'Baseline Input',
    description: 'Configure initial parameters'
  },
  { 
    title: 'Levers',
    description: 'Set scenario adjustments and run simulation'
  },
];

export function useScenarioForm(options: UseScenarioFormOptions = {}): UseScenarioFormReturn {
  const { 
    onComplete, 
    onCancel, 
    initialScenario, 
    editingId: propEditingId 
  } = options;
  
  const { id: urlId } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  
  // Determine editing ID from props or URL
  const editingId = propEditingId || urlId;
  const isEditing = !!editingId;
  
  // Initialize state
  const [state, setState] = useState<ScenarioWorkflowState>(() => 
    ScenarioService.createInitialState(initialScenario)
  );
  
  // Component refs for data extraction
  const baselineGridRef = useRef<any>(null);
  const leversRef = useRef<any>(null);
  
  // Load existing scenario for editing
  const loadScenario = useCallback(async () => {
    if (!editingId) return;
    
    try {
      const { scenario, baselineData } = await ScenarioService.loadScenario(editingId);
      setState(prev => ({
        ...prev,
        scenario,
        baselineData
      }));
    } catch (error) {
      showMessage.error('Failed to load scenario: ' + (error as Error).message);
    }
  }, [editingId]);
  
  // Load scenario on mount if editing
  useEffect(() => {
    loadScenario();
  }, [loadScenario]);
  
  // Navigation handlers
  const handleDetailsNext = useCallback((data: { scenario: ScenarioDefinition }) => {
    setState(prev => ({
      ...prev,
      scenario: data.scenario,
      current: 1,
      baselineData: data.scenario.baseline_input || prev.baselineData
    }));
  }, []);
  
  const handleBaselineNext = useCallback((data: any) => {
    setState(prev => ({
      ...prev,
      baselineData: data,
      current: 2
    }));
  }, []);
  
  const handleBaselineStepNext = useCallback(() => {
    // Extract current data from baseline grid
    const { baselineData } = ScenarioService.extractRefData({ 
      baselineGridRef 
    });
    
    setState(prev => ({
      ...prev,
      baselineData,
      current: 2
    }));
  }, []);
  
  const handleBack = useCallback(() => {
    setState(prev => ({
      ...prev,
      current: Math.max(0, prev.current - 1)
    }));
  }, []);
  
  // Save scenario
  const handleLeversSave = useCallback(async () => {
    if (state.saving) return;
    
    setState(prev => ({ 
      ...prev, 
      saving: true, 
      validationErrors: [] 
    }));
    
    try {
      // Extract current data from component refs
      const { baselineData, leversData } = ScenarioService.extractRefData({
        baselineGridRef,
        leversRef
      });
      
      // Use extracted data or fallback to state
      const formData: ScenarioFormData = {
        scenario: state.scenario,
        baselineData: baselineData || state.baselineData,
        leversData
      };
      
      const result = await ScenarioService.saveScenario(formData, editingId);
      
      if (result.success) {
        setState(prev => ({
          ...prev,
          scenarioId: result.scenarioId || prev.scenarioId
        }));
        
        showMessage.success(
          isEditing ? 'Scenario updated!' : 'Scenario created!'
        );
        
        onComplete?.();
      } else {
        setState(prev => ({
          ...prev,
          validationErrors: [result.error || 'Save failed']
        }));
        showMessage.error('Failed to save scenario: ' + result.error);
      }
    } catch (error) {
      const errorMessage = (error as Error).message;
      setState(prev => ({
        ...prev,
        validationErrors: [errorMessage]
      }));
      showMessage.error('Failed to save scenario: ' + errorMessage);
    } finally {
      setState(prev => ({ ...prev, saving: false }));
    }
  }, [state.scenario, state.baselineData, state.saving, editingId, isEditing, onComplete]);
  
  // Run simulation
  const handleRunSimulation = useCallback(async () => {
    setState(prev => ({
      ...prev,
      simulating: true,
      simulationError: null,
      simulationResult: null
    }));
    
    try {
      // Extract current data from component refs
      const { baselineData, leversData } = ScenarioService.extractRefData({
        baselineGridRef,
        leversRef
      });
      
      // Use extracted data or fallback to state
      const formData: ScenarioFormData = {
        scenario: state.scenario,
        baselineData: baselineData || state.baselineData,
        leversData
      };
      
      const result = await ScenarioService.runSimulation(formData);
      
      if (result.success) {
        setState(prev => ({
          ...prev,
          simulationResult: result.result || null
        }));
      } else {
        setState(prev => ({
          ...prev,
          simulationError: result.error || 'Simulation failed'
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        simulationError: (error as Error).message
      }));
    } finally {
      setState(prev => ({ ...prev, simulating: false }));
    }
  }, [state.scenario, state.baselineData]);
  
  const progressPercentage = ((state.current + 1) / WIZARD_STEPS.length) * 100;
  
  return {
    // State
    state,
    
    // Navigation
    current: state.current,
    steps: WIZARD_STEPS,
    progressPercentage,
    
    // Refs
    baselineGridRef,
    leversRef,
    
    // Actions
    handleDetailsNext,
    handleBaselineNext,
    handleBaselineStepNext,
    handleBack,
    handleLeversSave,
    handleRunSimulation,
    
    // Utilities
    isEditing,
    editingId
  };
}