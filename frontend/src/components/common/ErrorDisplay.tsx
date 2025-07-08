import React from 'react';
import { Alert, Button, Typography } from 'antd';
import type { ErrorResponse } from '../../types/scenarios';

const { Text } = Typography;

interface ErrorDisplayProps {
  error: ErrorResponse | string;
  onRetry?: () => void;
  onDismiss?: () => void;
  showDetails?: boolean;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ 
  error, 
  onRetry, 
  onDismiss, 
  showDetails = false 
}) => {
  // Handle both string errors and structured ErrorResponse objects
  const errorData: ErrorResponse = typeof error === 'string' 
    ? { detail: error }
    : error;

  return (
    <Alert
      message="Error"
      description={
        <div>
          <p>{errorData.detail}</p>
          {errorData.correlation_id && (
            <p style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
              <Text code>Reference ID: {errorData.correlation_id}</Text>
            </p>
          )}
          {showDetails && errorData.context && (
            <details style={{ marginTop: '8px' }}>
              <summary style={{ cursor: 'pointer', fontSize: '12px' }}>
                Additional Details
              </summary>
              <pre style={{ 
                fontSize: '11px', 
                background: '#f5f5f5', 
                padding: '8px', 
                borderRadius: '4px',
                marginTop: '4px',
                overflow: 'auto',
                maxHeight: '200px'
              }}>
                {JSON.stringify(errorData.context, null, 2)}
              </pre>
            </details>
          )}
        </div>
      }
      type="error"
      showIcon
      action={
        <div style={{ display: 'flex', gap: '8px' }}>
          {onRetry && (
            <Button size="small" onClick={onRetry}>
              Retry
            </Button>
          )}
          {onDismiss && (
            <Button size="small" onClick={onDismiss}>
              Dismiss
            </Button>
          )}
        </div>
      }
      style={{ marginBottom: '16px' }}
    />
  );
};

export default ErrorDisplay; 