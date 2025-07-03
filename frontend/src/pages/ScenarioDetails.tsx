import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Typography, Spin, message, Card } from 'antd';
import { scenarioApi } from '../services/scenarioApi';
import ResultsTable from '../components/scenario-runner/ResultsTable';
import ScenarioLevers, { getCompleteLevers } from '../components/scenario-runner/ScenarioLevers';
import type { ScenarioDefinition } from '../types/scenarios';

const { Title, Text } = Typography;

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
        if (!id) throw new Error('No scenario ID provided');
        const data = await scenarioApi.getScenario(id);
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
        <ScenarioLevers levers={getCompleteLevers(scenario.levers)} />
        <div style={{ marginTop: 24, textAlign: 'right' }}>
          <Button type="primary" onClick={() => setShowResults(true)}>Run Simulation</Button>
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