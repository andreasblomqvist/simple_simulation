import React, { useState, useEffect, useRef } from 'react';
import { Card, Typography, Progress, Button, Space } from 'antd';

const { Title, Paragraph } = Typography;

interface ScenarioExecutionProps {
  onNext: () => void;
  onBack: () => void;
}

const months = [
  '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06',
  '2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12',
];

const ScenarioExecution: React.FC<ScenarioExecutionProps> = ({ onNext, onBack }) => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Ready to run scenario...');
  const [running, setRunning] = useState(false);
  const [cancelled, setCancelled] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (running && progress < 100 && !cancelled) {
      intervalRef.current = setInterval(() => {
        setProgress(prev => {
          const next = Math.min(prev + 100 / months.length, 100);
          setStatus(`Processing month ${months[Math.floor(next / (100 / months.length)) - 1] || months[months.length - 1]}...`);
          return next;
        });
      }, 700);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [running, cancelled]);

  useEffect(() => {
    if (progress >= 100 && running) {
      setStatus('Scenario complete!');
      setRunning(false);
    }
  }, [progress, running]);

  const handleRun = () => {
    setProgress(0);
    setStatus('Starting scenario...');
    setRunning(true);
    setCancelled(false);
  };

  const handleCancel = () => {
    setCancelled(true);
    setRunning(false);
    setStatus('Cancelled');
    setProgress(0);
    if (intervalRef.current) clearInterval(intervalRef.current);
  };

  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Running Scenario</Title>} style={{ maxWidth: 1000, margin: '0 auto' }}>
      <Paragraph>{status}</Paragraph>
      <Progress percent={progress} status={cancelled ? 'exception' : progress === 100 ? 'success' : 'active'} style={{ marginBottom: 24, width: '100%' }} />
      <Space>
        <Button onClick={onBack}>Back</Button>
        <Button onClick={handleRun} disabled={running || progress === 100}>Run Scenario</Button>
        <Button onClick={handleCancel} disabled={!running}>Cancel</Button>
        <Button type="primary" onClick={onNext} disabled={progress < 100}>Next: Results</Button>
      </Space>
    </Card>
  );
};

export default ScenarioExecution; 