/**
 * CAT Matrix Editor Component
 * Allows editing of office-specific CAT progression probabilities
 */
import React, { useState, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  RotateCcw, 
  Save, 
  AlertTriangle,
  TrendingUp,
  Users,
  Calculator,
  Info
} from 'lucide-react';
import type { CATMatrix } from '../../types/office';

interface CATMatrixEditorProps {
  catMatrix: CATMatrix;
  officeName: string;
  onSave: (matrix: CATMatrix) => void;
  onReset: () => void;
  isLoading?: boolean;
}

// Standard CAT levels and stages
const CAT_LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P', 'X'];
const CAT_STAGES = ['CAT0', 'CAT6', 'CAT12', 'CAT18', 'CAT24', 'CAT30', 'CAT36', 'CAT42', 'CAT48', 'CAT54', 'CAT60'];

// Journey groupings for better organization
const JOURNEY_GROUPS = {
  'Junior (J-1)': ['A', 'AC', 'C'],
  'Mid-Level (J-2)': ['SrC', 'AM'],
  'Senior (J-3)': ['M', 'SrM', 'Pi', 'P', 'X']
};

export const CATMatrixEditor: React.FC<CATMatrixEditorProps> = ({
  catMatrix,
  officeName,
  onSave,
  onReset,
  isLoading = false
}) => {
  const [editMatrix, setEditMatrix] = useState<CATMatrix>(catMatrix);
  const [hasChanges, setHasChanges] = useState(false);
  const [activeLevel, setActiveLevel] = useState<string>('A');

  // Update probability for a specific level and CAT stage
  const updateProbability = useCallback((level: string, catStage: string, value: number) => {
    const clampedValue = Math.max(0, Math.min(1, value));
    
    setEditMatrix(prev => ({
      ...prev,
      [level]: {
        ...prev[level],
        [catStage]: clampedValue
      }
    }));
    setHasChanges(true);
  }, []);

  // Calculate aggregate statistics for the matrix
  const matrixStats = useMemo(() => {
    const stats = {
      totalProbabilities: 0,
      avgProbability: 0,
      highestProbability: 0,
      levelsWithData: 0
    };

    let totalProbs = 0;
    let probCount = 0;
    let levelsWithData = 0;

    Object.entries(editMatrix).forEach(([level, stages]) => {
      let levelHasData = false;
      Object.values(stages).forEach(prob => {
        if (prob > 0) {
          totalProbs += prob;
          probCount++;
          levelHasData = true;
          stats.highestProbability = Math.max(stats.highestProbability, prob);
        }
      });
      if (levelHasData) levelsWithData++;
    });

    stats.totalProbabilities = totalProbs;
    stats.avgProbability = probCount > 0 ? totalProbs / probCount : 0;
    stats.levelsWithData = levelsWithData;

    return stats;
  }, [editMatrix]);

  // Handle save
  const handleSave = () => {
    onSave(editMatrix);
    setHasChanges(false);
  };

  // Handle reset
  const handleReset = () => {
    onReset();
    setHasChanges(false);
  };

  // Render a level's CAT progression table
  const renderLevelMatrix = (level: string) => {
    const levelData = editMatrix[level] || {};
    const relevantStages = CAT_STAGES.filter(stage => 
      levelData.hasOwnProperty(stage) || stage === 'CAT0'
    );

    return (
      <div className="space-y-4">
        {/* Level Info Header */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold" style={{ color: '#f3f4f6' }}>
              Level {level} CAT Progression
            </h3>
            <p className="text-sm" style={{ color: '#9ca3af' }}>
              Adjust progression probabilities for each CAT stage
            </p>
          </div>
          <Badge variant="outline" style={{
            backgroundColor: '#1f2937',
            borderColor: '#3b82f6',
            color: '#93c5fd'
          }}>
            {relevantStages.length} stages
          </Badge>
        </div>

        {/* CAT Stages Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {relevantStages.map(stage => {
            const probability = levelData[stage] || 0;
            return (
              <div 
                key={stage}
                className="p-3 rounded-lg border"
                style={{ 
                  backgroundColor: '#111827',
                  borderColor: '#374151'
                }}
              >
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium" style={{ color: '#d1d5db' }}>
                    {stage}
                  </label>
                  <span 
                    className="text-xs px-2 py-1 rounded-full"
                    style={{
                      backgroundColor: probability > 0.5 ? '#10b981' : probability > 0.2 ? '#f59e0b' : '#6b7280',
                      color: '#ffffff'
                    }}
                  >
                    {(probability * 100).toFixed(1)}%
                  </span>
                </div>
                
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.001"
                  value={probability}
                  onChange={(e) => updateProbability(level, stage, parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                />
                
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.001"
                  value={probability.toFixed(3)}
                  onChange={(e) => updateProbability(level, stage, parseFloat(e.target.value) || 0)}
                  className="w-full mt-2 px-2 py-1 text-xs rounded border"
                  style={{
                    backgroundColor: '#374151',
                    borderColor: '#4b5563',
                    color: '#f3f4f6'
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
      <CardHeader className="p-6" style={{ 
        borderBottom: '1px solid #374151',
        background: 'linear-gradient(to right, #1e3a8a, #312e81)',
      }}>
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                <TrendingUp className="h-5 w-5" style={{ color: '#ffffff' }} />
              </div>
              CAT Progression Matrix
            </CardTitle>
            <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
              Configure {officeName}'s CAT progression probabilities by level and tenure stage
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            {hasChanges && (
              <Badge variant="outline" style={{
                backgroundColor: '#f59e0b',
                borderColor: '#f59e0b',
                color: '#ffffff'
              }}>
                Unsaved Changes
              </Badge>
            )}
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              disabled={isLoading}
              style={{
                borderColor: '#6b7280',
                color: '#9ca3af'
              }}
              className="hover:bg-gray-700"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset to Default
            </Button>
            
            <Button
              size="sm"
              onClick={handleSave}
              disabled={!hasChanges || isLoading}
              style={{
                backgroundColor: hasChanges ? '#10b981' : '#374151',
                color: '#ffffff'
              }}
              className="hover:bg-green-600 disabled:hover:bg-gray-600"
            >
              <Save className="h-4 w-4 mr-2" />
              Save Matrix
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6">
        {/* Matrix Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
            <div className="flex items-center gap-2 mb-2">
              <Users className="h-4 w-4" style={{ color: '#3b82f6' }} />
              <span className="text-sm font-medium" style={{ color: '#9ca3af' }}>Levels</span>
            </div>
            <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
              {matrixStats.levelsWithData}/{CAT_LEVELS.length}
            </div>
          </div>

          <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
            <div className="flex items-center gap-2 mb-2">
              <Calculator className="h-4 w-4" style={{ color: '#10b981' }} />
              <span className="text-sm font-medium" style={{ color: '#9ca3af' }}>Avg Probability</span>
            </div>
            <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
              {(matrixStats.avgProbability * 100).toFixed(1)}%
            </div>
          </div>

          <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4" style={{ color: '#f59e0b' }} />
              <span className="text-sm font-medium" style={{ color: '#9ca3af' }}>Highest Prob</span>
            </div>
            <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
              {(matrixStats.highestProbability * 100).toFixed(1)}%
            </div>
          </div>

          <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
            <div className="flex items-center gap-2 mb-2">
              <Info className="h-4 w-4" style={{ color: '#8b5cf6' }} />
              <span className="text-sm font-medium" style={{ color: '#9ca3af' }}>Total Weight</span>
            </div>
            <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
              {matrixStats.totalProbabilities.toFixed(2)}
            </div>
          </div>
        </div>

        {/* Level Tabs */}
        <Tabs value={activeLevel} onValueChange={setActiveLevel} className="space-y-6">
          <TabsList 
            className="grid grid-cols-5 lg:grid-cols-10 h-12 p-1.5 rounded-xl border-0 shadow-sm"
            style={{ backgroundColor: '#374151' }}
          >
            {CAT_LEVELS.map(level => {
              const hasData = editMatrix[level] && Object.values(editMatrix[level]).some(p => p > 0);
              return (
                <TabsTrigger 
                  key={level} 
                  value={level}
                  className="flex flex-col items-center gap-1 h-9 px-2 rounded-lg transition-all duration-200 font-medium text-xs"
                  style={{
                    backgroundColor: activeLevel === level ? '#1f2937' : 'transparent',
                    color: activeLevel === level ? '#f3f4f6' : '#9ca3af',
                    boxShadow: activeLevel === level ? '0 1px 3px rgba(0, 0, 0, 0.1)' : 'none'
                  }}
                >
                  <span>{level}</span>
                  {hasData && (
                    <div 
                      className="w-1 h-1 rounded-full"
                      style={{ backgroundColor: '#10b981' }}
                    />
                  )}
                </TabsTrigger>
              );
            })}
          </TabsList>

          {/* Level Content */}
          {CAT_LEVELS.map(level => (
            <TabsContent key={level} value={level} className="space-y-6">
              {renderLevelMatrix(level)}
            </TabsContent>
          ))}
        </Tabs>

        {/* Help Text */}
        <div 
          className="mt-6 p-4 rounded-lg flex items-start gap-3"
          style={{ backgroundColor: '#111827', borderLeft: '4px solid #3b82f6' }}
        >
          <Info className="h-5 w-5 mt-0.5" style={{ color: '#3b82f6' }} />
          <div>
            <h4 className="font-medium mb-1" style={{ color: '#f3f4f6' }}>
              About CAT Matrix
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: '#9ca3af' }}>
              The CAT matrix defines progression probabilities for each consultant level at different tenure stages. 
              Higher probabilities indicate more positive progression environments. Adjust values between 0.0 (never progress) 
              and 1.0 (always progress) to reflect your office's unique progression culture.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};