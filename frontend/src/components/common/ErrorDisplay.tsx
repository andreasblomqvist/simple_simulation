import React from 'react';
import { Alert, AlertDescription } from '../ui/alert';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { AlertTriangle, RefreshCw, X } from 'lucide-react';
import type { ErrorResponse } from '../../types/unified-data-structures';

interface ErrorDisplayProps {
  error: ErrorResponse | string | any; // Allow any to handle backend validation errors
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
  // Handle different error formats
  const getErrorData = (): { detail: string; correlation_id?: string; context?: any } => {
    if (typeof error === 'string') {
      return { detail: error };
    }
    
    // Handle backend validation error format: {type, loc, msg, input}
    if (error && typeof error === 'object' && 'msg' in error) {
      return { 
        detail: error.msg || 'Validation error',
        context: error.input || error
      };
    }
    
    // Handle expected ErrorResponse format
    if (error && typeof error === 'object' && 'detail' in error) {
      return {
        detail: error.detail,
        correlation_id: error.correlation_id,
        context: error.context
      };
    }
    
    // Fallback for unknown error formats
    return { 
      detail: 'An unexpected error occurred',
      context: error
    };
  };

  const errorData = getErrorData();

  return (
    <Alert variant="destructive" className="mb-4">
      <AlertTriangle className="h-4 w-4" />
      <AlertDescription className="flex-1">
        <div className="space-y-2">
          <p className="font-medium">{errorData.detail}</p>
          
          {errorData.correlation_id && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Reference ID:</span>
              <Badge variant="outline" className="text-xs font-mono">
                {errorData.correlation_id}
              </Badge>
            </div>
          )}
          
          {showDetails && errorData.context && (
            <details className="mt-2">
              <summary className="cursor-pointer text-xs font-medium hover:text-foreground">
                Additional Details
              </summary>
              <pre className="mt-2 max-h-48 overflow-auto rounded-sm bg-muted p-2 text-xs">
                {JSON.stringify(errorData.context, null, 2)}
              </pre>
            </details>
          )}
          
          {(onRetry || onDismiss) && (
            <div className="flex gap-2 pt-2">
              {onRetry && (
                <Button variant="outline" size="sm" onClick={onRetry}>
                  <RefreshCw className="mr-2 h-3 w-3" />
                  Retry
                </Button>
              )}
              {onDismiss && (
                <Button variant="ghost" size="sm" onClick={onDismiss}>
                  <X className="mr-2 h-3 w-3" />
                  Dismiss
                </Button>
              )}
            </div>
          )}
        </div>
      </AlertDescription>
    </Alert>
  );
};

export default ErrorDisplay; 