# Frontend Integration Plan - Updated Backend Scenario Service

## Overview

This document outlines the necessary updates to the frontend to work seamlessly with the improved backend scenario service that now includes:
- Enhanced error handling with correlation IDs
- Structured logging
- Improved validation
- New data transformation services
- Better separation of concerns

## Current State Analysis

### ✅ What's Working Well
1. **API Service Structure**: `scenarioApi.ts` is well-organized with proper error handling
2. **Type Safety**: Comprehensive TypeScript types that mostly match backend models
3. **CRUD Operations**: Basic scenario management operations are implemented
4. **Component Architecture**: Good separation between API layer and UI components

### ⚠️ Issues to Address

#### 1. **Type Mismatches**
- **Backend requires `description` field** but frontend makes it optional
- **New backend fields** (`progression_config`, `cat_curves`) not handled in frontend
- **Error response structure** has changed with correlation IDs

#### 2. **API Endpoint Gaps**
- **Validation endpoint** not used by frontend
- **Enhanced error responses** not properly handled
- **Correlation ID tracking** not implemented

#### 3. **User Experience Issues**
- **No loading states** for new structured operations
- **Error messages** not user-friendly
- **No retry mechanisms** for transient failures

## Implementation Plan

### Phase 1: Update Type Definitions ✅

#### 1.1 Update Scenario Types
**File**: `frontend/src/types/scenarios.ts`

**Changes Needed**:
```typescript
// Make description required to match backend
export interface ScenarioDefinition {
  id?: string;
  name: string;
  description: string; // ✅ Change from optional to required
  time_range: TimeRange;
  office_scope: OfficeName[];
  levers: ScenarioLevers;
  economic_params?: EconomicParams;
  // ✅ Add new backend fields
  progression_config?: Record<string, any>;
  cat_curves?: Record<string, any>;
  baseline_input?: any;
  created_at?: string | Date;
  updated_at?: string | Date;
}

// ✅ Add new error response types
export interface ErrorResponse {
  detail: string;
  correlation_id?: string;
  error_type?: string;
  context?: Record<string, any>;
}

// ✅ Add validation response types
export interface ValidationResponse {
  valid: boolean;
  errors: string[];
  warnings?: string[];
  correlation_id?: string;
}
```

#### 1.2 Update API Response Types
**File**: `frontend/src/types/scenarios.ts`

**Changes Needed**:
```typescript
// ✅ Update ScenarioResponse to include correlation ID
export interface ScenarioResponse {
  scenario_id: string;
  scenario_name: string;
  execution_time: number;
  results: SimulationResults;
  status: 'success' | 'error';
  error_message?: string;
  correlation_id?: string; // ✅ Add correlation ID
}

// ✅ Add new API response types
export interface ApiResponse<T> {
  data: T;
  correlation_id?: string;
  metadata?: {
    processing_time?: number;
    warnings?: string[];
  };
}
```

### Phase 2: Enhance API Service ✅

#### 2.1 Update Error Handling
**File**: `frontend/src/services/scenarioApi.ts`

**Changes Needed**:
```typescript
// ✅ Add correlation ID tracking
class ScenarioApiService {
  private correlationId: string | null = null;

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    
    // ✅ Generate correlation ID for each request
    this.correlationId = this.generateCorrelationId();
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-ID': this.correlationId, // ✅ Add correlation ID header
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // ✅ Enhanced error handling with correlation ID
        const error: ErrorResponse = {
          detail: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          correlation_id: errorData.correlation_id || this.correlationId,
          error_type: errorData.error_type,
          context: errorData.context,
        };
        
        throw new Error(JSON.stringify(error));
      }

      const data = await response.json();
      
      // ✅ Log successful requests with correlation ID
      console.log(`API request successful: ${endpoint} [corr: ${this.correlationId}]`);
      
      return data;
    } catch (error) {
      // ✅ Enhanced error logging with correlation ID
      console.error(`API request failed for ${endpoint} [corr: ${this.correlationId}]:`, error);
      throw error;
    }
  }

  private generateCorrelationId(): string {
    return Math.random().toString(36).substring(2, 10);
  }
}
```

#### 2.2 Add Validation Endpoint
**File**: `frontend/src/services/scenarioApi.ts`

**Changes Needed**:
```typescript
// ✅ Add validation method
async validateScenario(scenario: ScenarioDefinition): Promise<ValidationResponse> {
  return this.request<ValidationResponse>('/validate', {
    method: 'POST',
    body: JSON.stringify(scenario),
  });
}

// ✅ Add validation before save/run
async createScenario(scenario: ScenarioDefinition): Promise<ScenarioId> {
  // ✅ Validate before creating
  const validation = await this.validateScenario(scenario);
  if (!validation.valid) {
    throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
  }

  const response = await this.request<{scenario_id: string}>('/create', {
    method: 'POST',
    body: JSON.stringify(scenario),
  });
  return response.scenario_id;
}
```

#### 2.3 Add Retry Logic
**File**: `frontend/src/services/scenarioApi.ts`

**Changes Needed**:
```typescript
// ✅ Add retry mechanism for transient failures
private async requestWithRetry<T>(
  endpoint: string,
  options: RequestInit = {},
  maxRetries: number = 3
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await this.request<T>(endpoint, options);
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
      
      // ✅ Only retry on specific error types
      const errorStr = error.toString();
      if (errorStr.includes('500') || errorStr.includes('502') || errorStr.includes('503')) {
        console.log(`Retrying request (attempt ${attempt}/${maxRetries}) [corr: ${this.correlationId}]`);
        await this.delay(1000 * attempt); // Exponential backoff
        continue;
      }
      
      throw error;
    }
  }
  
  throw new Error('Max retries exceeded');
}

private delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### Phase 3: Update UI Components ✅

#### 3.1 Update Scenario Creation Form
**File**: `frontend/src/components/scenario-runner/ScenarioCreationForm.tsx`

**Changes Needed**:
```typescript
// ✅ Make description required
const [formData, setFormData] = useState({
  name: scenario?.name || '',
  description: scenario?.description || '', // ✅ Required field
  time_range: scenario?.time_range || defaultTimeRange,
  office_scope: scenario?.office_scope || [],
});

// ✅ Add validation
const validateForm = (): string[] => {
  const errors: string[] = [];
  
  if (!formData.name.trim()) {
    errors.push('Scenario name is required');
  }
  
  if (!formData.description.trim()) { // ✅ Validate description
    errors.push('Scenario description is required');
  }
  
  if (formData.office_scope.length === 0) {
    errors.push('At least one office must be selected');
  }
  
  return errors;
};
```

#### 3.2 Add Loading States and Error Handling
**File**: `frontend/src/components/scenario-runner/ScenarioWizard.tsx`

**Changes Needed**:
```typescript
// ✅ Add enhanced loading states
const [validationLoading, setValidationLoading] = useState(false);
const [validationErrors, setValidationErrors] = useState<string[]>([]);

// ✅ Add validation step
const handleValidateScenario = async (scenarioData: ScenarioDefinition) => {
  setValidationLoading(true);
  setValidationErrors([]);
  
  try {
    const validation = await scenarioApi.validateScenario(scenarioData);
    if (!validation.valid) {
      setValidationErrors(validation.errors);
      return false;
    }
    return true;
  } catch (error) {
    setValidationErrors([`Validation failed: ${error.message}`]);
    return false;
  } finally {
    setValidationLoading(false);
  }
};

// ✅ Update save logic with validation
const handleLeversSave = async () => {
  if (saving) return;
  setSaving(true);
  
  try {
    const scenarioWithData = {
      ...scenario,
      baseline_input: baselineInput,
      levers: leversData,
      description: scenario.description || 'No description provided', // ✅ Ensure description
    } as ScenarioDefinition;
    
    // ✅ Validate before saving
    const isValid = await handleValidateScenario(scenarioWithData);
    if (!isValid) {
      return;
    }
    
    if (id) {
      await scenarioApi.updateScenario(id, scenarioWithData);
      message.success('Scenario updated!');
    } else {
      const newScenarioId = await scenarioApi.createScenario(scenarioWithData);
      setScenarioId(newScenarioId);
      message.success('Scenario created!');
    }
    
    navigate('/scenario-runner');
  } catch (error) {
    // ✅ Enhanced error display with correlation ID
    const errorData = JSON.parse(error.message);
    message.error(`Failed to save scenario: ${errorData.detail}`);
    console.error(`Save failed [corr: ${errorData.correlation_id}]:`, error);
  } finally {
    setSaving(false);
  }
};
```

#### 3.3 Add Error Display Component
**File**: `frontend/src/components/common/ErrorDisplay.tsx` (new file)

**Changes Needed**:
```typescript
import React from 'react';
import { Alert, Button } from 'antd';
import type { ErrorResponse } from '../../types/scenarios';

interface ErrorDisplayProps {
  error: ErrorResponse;
  onRetry?: () => void;
  onDismiss?: () => void;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry, onDismiss }) => {
  return (
    <Alert
      message="Error"
      description={
        <div>
          <p>{error.detail}</p>
          {error.correlation_id && (
            <p style={{ fontSize: '12px', color: '#666' }}>
              Reference ID: {error.correlation_id}
            </p>
          )}
          {error.context && (
            <details style={{ marginTop: '8px' }}>
              <summary>Additional Details</summary>
              <pre style={{ fontSize: '12px' }}>
                {JSON.stringify(error.context, null, 2)}
              </pre>
            </details>
          )}
        </div>
      }
      type="error"
      showIcon
      action={
        <div>
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
    />
  );
};

export default ErrorDisplay;
```

### Phase 4: Add New Features ✅

#### 4.1 Progression Configuration UI
**File**: `frontend/src/components/scenario-runner/ProgressionConfig.tsx` (new file)

**Changes Needed**:
```typescript
import React, { useState } from 'react';
import { Card, Form, InputNumber, Select, Button } from 'antd';

interface ProgressionConfigProps {
  value?: Record<string, any>;
  onChange?: (value: Record<string, any>) => void;
}

const ProgressionConfig: React.FC<ProgressionConfigProps> = ({ value, onChange }) => {
  const [config, setConfig] = useState(value || {});

  const handleChange = (newConfig: Record<string, any>) => {
    setConfig(newConfig);
    onChange?.(newConfig);
  };

  return (
    <Card title="Progression Configuration" size="small">
      <Form layout="vertical">
        <Form.Item label="Evaluation Months">
          <Select
            mode="multiple"
            placeholder="Select evaluation months"
            value={config.evaluation_months || []}
            onChange={(months) => handleChange({ ...config, evaluation_months: months })}
            options={[
              { label: 'January', value: 1 },
              { label: 'February', value: 2 },
              // ... all months
            ]}
          />
        </Form.Item>
        
        <Form.Item label="Default Progression Rate (%)">
          <InputNumber
            min={0}
            max={100}
            value={config.default_rate || 10}
            onChange={(rate) => handleChange({ ...config, default_rate: rate })}
          />
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ProgressionConfig;
```

#### 4.2 CAT Curves Configuration UI
**File**: `frontend/src/components/scenario-runner/CATCurvesConfig.tsx` (new file)

**Changes Needed**:
```typescript
import React, { useState } from 'react';
import { Card, Form, InputNumber, Select, Button } from 'antd';

interface CATCurvesConfigProps {
  value?: Record<string, any>;
  onChange?: (value: Record<string, any>) => void;
}

const CATCurvesConfig: React.FC<CATCurvesConfigProps> = ({ value, onChange }) => {
  const [curves, setCurves] = useState(value || {});

  const levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];

  const handleChange = (newCurves: Record<string, any>) => {
    setCurves(newCurves);
    onChange?.(newCurves);
  };

  return (
    <Card title="CAT Curves Configuration" size="small">
      <Form layout="vertical">
        {levels.map(level => (
          <div key={level} style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <span style={{ width: '60px', fontWeight: 'bold' }}>{level}:</span>
            <InputNumber
              placeholder="Progression %"
              min={0}
              max={100}
              value={curves[`${level}_progression`] || 0}
              onChange={(value) => handleChange({
                ...curves,
                [`${level}_progression`]: value
              })}
              style={{ width: '120px' }}
            />
            <InputNumber
              placeholder="Retention %"
              min={0}
              max={100}
              value={curves[`${level}_retention`] || 0}
              onChange={(value) => handleChange({
                ...curves,
                [`${level}_retention`]: value
              })}
              style={{ width: '120px' }}
            />
          </div>
        ))}
      </Form>
    </Card>
  );
};

export default CATCurvesConfig;
```

### Phase 5: Testing and Validation ✅

#### 5.1 Update Unit Tests
**Files**: 
- `frontend/src/services/__tests__/scenarioApi.test.ts`
- `frontend/src/components/__tests__/ScenarioWizard.test.tsx`

**Changes Needed**:
```typescript
// ✅ Test new validation functionality
describe('validateScenario', () => {
  it('should validate scenario successfully', async () => {
    const mockScenario = {
      name: 'Test Scenario',
      description: 'Test Description', // ✅ Required field
      time_range: { start_year: 2025, start_month: 1, end_year: 2027, end_month: 12 },
      office_scope: ['Stockholm'],
      levers: {},
    };

    const mockResponse = { valid: true, errors: [] };
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await scenarioApi.validateScenario(mockScenario);
    expect(result.valid).toBe(true);
  });

  it('should handle validation errors', async () => {
    const mockResponse = { 
      valid: false, 
      errors: ['Description is required'],
      correlation_id: 'abc123'
    };
    
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await scenarioApi.validateScenario({} as any);
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Description is required');
  });
});
```

#### 5.2 Integration Tests
**File**: `frontend/src/__tests__/integration/scenarioFlow.test.tsx`

**Changes Needed**:
```typescript
// ✅ Test complete scenario creation flow
describe('Scenario Creation Flow', () => {
  it('should create scenario with validation', async () => {
    // Test the complete flow from form to API
    // Including validation, error handling, and correlation IDs
  });

  it('should handle API errors gracefully', async () => {
    // Test error scenarios with correlation ID tracking
  });
});
```

## Implementation Checklist

### Phase 1: Type Updates
- [ ] Update `ScenarioDefinition` interface to make description required
- [ ] Add new backend fields (`progression_config`, `cat_curves`)
- [ ] Add error response types with correlation IDs
- [ ] Add validation response types

### Phase 2: API Service Updates
- [ ] Add correlation ID tracking to all API requests
- [ ] Implement enhanced error handling with structured responses
- [ ] Add validation endpoint integration
- [ ] Add retry logic for transient failures
- [ ] Update all CRUD operations to use validation

### Phase 3: UI Component Updates
- [ ] Update scenario creation form to require description
- [ ] Add loading states for validation operations
- [ ] Implement enhanced error display with correlation IDs
- [ ] Add retry mechanisms in UI
- [ ] Create reusable error display component

### Phase 4: New Features
- [ ] Create progression configuration UI component
- [ ] Create CAT curves configuration UI component
- [ ] Integrate new components into scenario wizard
- [ ] Add form validation for new fields

### Phase 5: Testing
- [ ] Update unit tests for new functionality
- [ ] Add integration tests for complete flows
- [ ] Test error scenarios and correlation ID tracking
- [ ] Validate all API endpoints work correctly

## Benefits of These Updates

### 1. **Better Error Handling**
- Users get clear, actionable error messages
- Correlation IDs help with debugging
- Retry mechanisms improve reliability

### 2. **Enhanced Validation**
- Client-side validation prevents invalid data submission
- Server-side validation provides additional safety
- Users get immediate feedback on form errors

### 3. **Improved User Experience**
- Loading states provide better feedback
- Error messages are user-friendly
- Retry mechanisms handle transient failures

### 4. **Better Debugging**
- Correlation IDs track requests through the system
- Structured error responses provide context
- Enhanced logging helps with troubleshooting

### 5. **Future-Proof Architecture**
- New backend fields are properly supported
- API service is extensible for new features
- Type safety prevents runtime errors

## Migration Strategy

### 1. **Backward Compatibility**
- Keep existing API endpoints working
- Gradually migrate to new validation
- Maintain existing UI until new components are ready

### 2. **Phased Rollout**
- Phase 1: Update types and basic error handling
- Phase 2: Add validation and retry logic
- Phase 3: Update UI components
- Phase 4: Add new features
- Phase 5: Comprehensive testing

### 3. **Testing Strategy**
- Unit tests for all new functionality
- Integration tests for complete flows
- Manual testing of all user scenarios
- Performance testing for new features

This plan ensures a smooth transition to the improved backend while maintaining a great user experience and adding valuable new features. 