/**
 * Scenarios management page - Enhanced with modern UI
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { EnhancedScenarioList } from '../components/scenario-runner/EnhancedScenarioList';
import type { ScenarioListItem, ScenarioId } from '../types/unified-data-structures';

export const Scenarios: React.FC = () => {
  const [scenarios, setScenarios] = useState<ScenarioListItem[]>([]);
  const navigate = useNavigate();

  const handleNext = () => {
    // Navigate to scenario creation
    navigate('/scenario-wizard');
  };

  const handleEdit = (id: ScenarioId) => {
    // Navigate to scenario editor
    navigate(`/scenario-editor/${id}`);
  };

  const handleDelete = (id: ScenarioId) => {
    // Delete logic is handled in EnhancedScenarioList
    console.log('Delete scenario:', id);
  };

  const handleCompare = () => {
    // Navigate to scenario comparison
    navigate('/scenario-comparison');
  };

  const handleExport = () => {
    // Export all scenarios logic
    console.log('Export all scenarios');
  };

  const handleView = (id: ScenarioId) => {
    // Navigate to scenario details
    navigate(`/scenario-runner/${id}`);
  };

  return (
    <EnhancedScenarioList
      onNext={handleNext}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onCompare={handleCompare}
      onExport={handleExport}
      onView={handleView}
      scenarios={scenarios}
      setScenarios={setScenarios}
    />
  );
};