import React, { useState } from 'react';
import { Typography, Button, Card } from 'antd';
import ScenarioWizard from '../components/scenario-runner/ScenarioWizard';
import ScenarioList from '../components/scenario-runner/ScenarioList';
import ScenarioComparison from '../components/scenario-runner/ScenarioComparison';
import type { ScenarioListItem } from '../types/scenarios';
import { scenarioApi } from '../services/scenarioApi';

const { Title } = Typography;

const ScenarioRunner: React.FC = () => {
  const [creating, setCreating] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  const [editingScenario, setEditingScenario] = useState<ScenarioListItem | null>(null);
  const [scenarios, setScenarios] = useState<ScenarioListItem[]>([]);

  return (
    <Card style={{ margin: 32 }}>
      <Title level={2} style={{ marginBottom: 0 }}>Scenario Runner</Title>
      {creating ? (
        <ScenarioWizard
          scenario={editingScenario}
          onCancel={() => { setCreating(false); setEditingScenario(null); }}
          onComplete={async () => {
            setCreating(false);
            setEditingScenario(null);
            const scenarioList = await scenarioApi.listScenarios();
            setScenarios(scenarioList);
          }}
        />
      ) : showComparison ? (
        <ScenarioComparison onBack={() => setShowComparison(false)} />
      ) : (
        <>
          <ScenarioList
            onNext={() => { setCreating(true); setEditingScenario(null); }}
            onEdit={async id => {
              try {
                if (!id || id === 'undefined' || id === 'null') {
                  throw new Error('Invalid scenario ID');
                }
                const fullScenario = await scenarioApi.getScenario(id);
                if (fullScenario) {
                  // Convert ScenarioDefinition to ScenarioListItem
                  const scenarioListItem: ScenarioListItem = {
                    id: id,
                    name: fullScenario.name,
                    description: fullScenario.description,
                    time_range: fullScenario.time_range,
                    office_scope: fullScenario.office_scope,
                    created_at: fullScenario.created_at as string || new Date().toISOString(),
                    updated_at: fullScenario.updated_at as string || new Date().toISOString(),
                  };
                  setEditingScenario(scenarioListItem);
                  setCreating(true);
                }
              } catch (error) {
                // Optionally show an error message
                // message.error('Failed to load scenario details');
              }
            }}
            onDelete={() => {}}
            onCompare={() => setShowComparison(true)}
            onExport={() => {}}
            onView={() => {}}
            hideHeader
            scenarios={scenarios}
            setScenarios={setScenarios}
          />
        </>
      )}
    </Card>
  );
};

export default ScenarioRunner; 