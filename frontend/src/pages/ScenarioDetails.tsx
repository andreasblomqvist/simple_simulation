import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Typography, Spin, message, Card } from 'antd';
import { scenarioApi } from '../services/scenarioApi';
import ResultsTable from '../components/scenario-runner/ResultsTable';
import ScenarioLevers, { getCompleteLevers } from '../components/scenario-runner/ScenarioLevers';
import type { ScenarioDefinition } from '../types/scenarios';

const { Title, Text } = Typography;

// Helper to extract baseline values for the levers UI
function extractBaselineValuesFromScenario(scenario: ScenarioDefinition | null): Record<'recruitment' | 'churn' | 'progression', Record<string, number>> {
  const levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
  const levers: Record<'recruitment' | 'churn' | 'progression', Record<string, number>> = {
    recruitment: {}, churn: {}, progression: {}
  };
  if (!scenario || !scenario.baseline_input) return levers;

  // Recruitment
  const recruitment = scenario.baseline_input.global?.recruitment?.Consultant || {};
  for (const level of levels) {
    const values = Object.values(recruitment)
      .map((monthObj: any) => Number(monthObj[level]) || 0)
      .filter(v => !isNaN(v));
    const avg = values.length > 0
      ? values.reduce((sum: number, v) => sum + v, 0) / values.length
      : 0;
    levers.recruitment[level] = avg;
  }

  // Churn
  const churn = scenario.baseline_input.global?.churn?.Consultant || {};
  for (const level of levels) {
    const values = Object.values(churn)
      .map((monthObj: any) => Number(monthObj[level]) || 0)
      .filter(v => !isNaN(v));
    const avg = values.length > 0
      ? values.reduce((sum: number, v) => sum + v, 0) / values.length
      : 0;
    levers.churn[level] = avg;
  }

  // Progression baseline is always 1
  for (const level of levels) {
    levers.progression[level] = 1;
  }
  return levers;
}

const ScenarioDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [scenario, setScenario] = useState<ScenarioDefinition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    const fetchScenario = async () => {
      setLoading(true);
      setError(null);
      try {
        if (!id) {
          throw new Error('No scenario ID provided');
        }
        if (id === 'undefined' || id === 'null') {
          throw new Error('Invalid scenario ID');
        }
        const data = await scenarioApi.getScenario(id);
        console.log('[LEVER DEBUG] Loaded scenario from API:', data);
        if (data.levers) {
          console.log('[LEVER DEBUG] Scenario levers:', data.levers);
        } else {
          console.log('[LEVER DEBUG] Scenario has no levers field.');
        }
        setScenario(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    fetchScenario();
    window.scrollTo(0, 0);
  }, [id]);

  if (loading) return <Spin style={{ margin: 64 }} />;
  if (error) return <div style={{ margin: 64, color: 'red' }}>{error}</div>;
  if (!scenario) return <div style={{ margin: 64 }}>Scenario not found.</div>;

  return (
    <Card style={{ margin: 32 }}>
      <Title level={2} style={{ marginBottom: 0 }}>{scenario.name}</Title>
      <Text type="secondary">{scenario.description}</Text>
      <div style={{ margin: '16px 0' }}>
        <b>Time Range:</b> {scenario.time_range.start_year}-{scenario.time_range.start_month} to {scenario.time_range.end_year}-{scenario.time_range.end_month}<br />
        <b>Office Scope:</b> {scenario.office_scope.join(', ')}
      </div>
      <div style={{ margin: '16px 0' }}>
        <Button type="primary" style={{ marginRight: 8 }} onClick={() => navigate(`/scenario-runner/edit/${id}`)}>Edit</Button>
        <Button style={{ marginRight: 8 }} onClick={() => navigate(`/scenario-runner/duplicate/${id}`)}>Duplicate</Button>
        <Button onClick={() => navigate('/scenario-runner')}>Back to List</Button>
      </div>
      {/* Levers section */}
      <section style={{ marginBottom: 24 }}>
        <h3 style={{ margin: '16px 0 8px 0' }}>Levers</h3>
        <ScenarioLevers
          levers={getCompleteLevers((typeof scenario.levers === 'object' && scenario.levers) ? scenario.levers as any : undefined)}
          baselineValues={extractBaselineValuesFromScenario(scenario)}
        />
        <div style={{ marginTop: 24, textAlign: 'right' }}>
          <Button type="primary" onClick={() => {
            console.log('[LEVER DEBUG] Running simulation for scenario:', scenario);
            setShowResults(true);
          }}>Run Simulation</Button>
        </div>
      </section>
      {showResults && (
        <section>
          <h3 style={{ margin: '16px 0 8px 0' }}>Simulation Results</h3>
          <ResultsTable scenarioId={id!} />
        </section>
      )}
    </Card>
  );
};

export default ScenarioDetails; 