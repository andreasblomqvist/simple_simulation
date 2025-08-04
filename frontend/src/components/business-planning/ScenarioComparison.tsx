/**
 * Scenario Comparison Component
 * 
 * Side-by-side analysis of different strategic options with AI recommendations.
 * Shows detailed comparison matrix, risk analysis, and stakeholder fit assessment.
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Separator } from '../ui/separator';
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  Users,
  AlertTriangle,
  CheckCircle,
  Target,
  Clock,
  Lightbulb,
  ChevronRight,
  ThumbsUp,
  ThumbsDown,
  Minus,
  Zap,
  Shield,
  Scale,
  Eye,
  Settings,
  Play
} from 'lucide-react';

interface SimulationScenario {
  id: string;
  name: string;
  description: string;
  strategy: string;
  approach: 'conservative' | 'moderate' | 'aggressive';
  results: {
    workforce: { current: number; projected: number };
    revenue: { current: string; projected: string; capacity: string };
    utilization: { current: string; projected: string };
    investment: string;
    budgetUsage: string;
    roi: string;
    risk: 'low' | 'medium' | 'high';
    payback: string;
    timeline: string;
    implementation: 'comfortable' | 'manageable' | 'aggressive';
  };
  advantages: string[];
  risks: string[];
  stakeholderFit: Record<string, 'supports' | 'neutral' | 'opposes' | 'conditions'>;
  isRecommended?: boolean;
}

interface Props {
  scenarios: SimulationScenario[];
  stakeholders: Array<{
    id: string;
    name: string;
    role: string;
  }>;
  onSelectScenario?: (scenarioId: string) => void;
  onModifyScenario?: (scenarioId: string) => void;
  onCreateNewScenario?: () => void;
}

const STAKEHOLDER_COLORS = {
  talent: '#10B981',
  sales: '#3B82F6',
  finance: '#F59E0B',
  operations: '#8B5CF6'
};

const APPROACH_COLORS = {
  conservative: '#10B981',
  moderate: '#F59E0B',
  aggressive: '#EF4444'
};

const APPROACH_ICONS = {
  conservative: Shield,
  moderate: Scale,
  aggressive: Zap
};

export const ScenarioComparison: React.FC<Props> = ({
  scenarios,
  stakeholders,
  onSelectScenario,
  onModifyScenario,
  onCreateNewScenario
}) => {
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>(
    scenarios.slice(0, 3).map(s => s.id)
  );
  const [showDetailedAnalysis, setShowDetailedAnalysis] = useState(false);

  const toggleScenarioSelection = (scenarioId: string) => {
    setSelectedScenarios(prev => {
      if (prev.includes(scenarioId)) {
        return prev.filter(id => id !== scenarioId);
      } else if (prev.length < 3) {
        return [...prev, scenarioId];
      } else {
        // Replace the first scenario if already at limit
        return [scenarioId, ...prev.slice(1)];
      }
    });
  };

  const getDisplayScenarios = () => {
    return scenarios.filter(s => selectedScenarios.includes(s.id));
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-400 border-green-400';
      case 'medium': return 'text-amber-400 border-amber-400';
      case 'high': return 'text-red-400 border-red-400';
      default: return 'text-gray-400 border-gray-400';
    }
  };

  const getImplementationColor = (implementation: string) => {
    switch (implementation) {
      case 'comfortable': return 'text-green-400';
      case 'manageable': return 'text-amber-400';
      case 'aggressive': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStakeholderIcon = (position: string) => {
    switch (position) {
      case 'supports': return <ThumbsUp className="h-3 w-3 text-green-400" />;
      case 'opposes': return <ThumbsDown className="h-3 w-3 text-red-400" />;
      case 'neutral': return <Minus className="h-3 w-3 text-gray-400" />;
      case 'conditions': return <AlertTriangle className="h-3 w-3 text-amber-400" />;
    }
  };

  const renderComparisonMatrix = () => {
    const displayScenarios = getDisplayScenarios();
    if (displayScenarios.length === 0) return null;

    return (
      <Card className="bg-gray-800 border-gray-600">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-400" />
            Scenario Comparison Matrix
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-600">
                  <th className="text-left py-3 px-4 text-gray-300 font-medium">Metric</th>
                  {displayScenarios.map(scenario => {
                    const ApproachIcon = APPROACH_ICONS[scenario.approach];
                    return (
                      <th key={scenario.id} className="text-center py-3 px-4 min-w-[200px]">
                        <div className="space-y-2">
                          <div className="flex items-center justify-center gap-2">
                            <ApproachIcon 
                              className="h-4 w-4" 
                              style={{ color: APPROACH_COLORS[scenario.approach] }}
                            />
                            <span className="font-medium text-gray-100">{scenario.name}</span>
                            {scenario.isRecommended && (
                              <Badge variant="outline" className="border-blue-400 text-blue-400 text-xs">
                                AI RECOMMENDED
                              </Badge>
                            )}
                          </div>
                          <div className="text-xs text-gray-400">{scenario.approach.toUpperCase()}</div>
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              
              <tbody className="divide-y divide-gray-700">
                {/* Workforce */}
                <tr>
                  <td className="py-3 px-4 text-gray-300 font-medium">👥 New Hires</td>
                  {displayScenarios.map(scenario => (
                    <td key={scenario.id} className="py-3 px-4 text-center text-gray-200">
                      {scenario.results.workforce.projected - scenario.results.workforce.current} Senior
                      <div className="text-xs text-gray-400">{scenario.results.timeline}</div>
                    </td>
                  ))}
                </tr>

                {/* Budget Impact */}
                <tr>
                  <td className="py-3 px-4 text-gray-300 font-medium">💰 Q3 Budget Impact</td>
                  {displayScenarios.map(scenario => (
                    <td key={scenario.id} className="py-3 px-4 text-center text-gray-200">
                      {scenario.results.investment}
                      <div className="text-xs text-gray-400">{scenario.results.budgetUsage}</div>
                    </td>
                  ))}
                </tr>

                {/* Revenue Capacity */}
                <tr>
                  <td className="py-3 px-4 text-gray-300 font-medium">📈 Q4 Revenue Capacity</td>
                  {displayScenarios.map(scenario => (
                    <td key={scenario.id} className="py-3 px-4 text-center text-gray-200">
                      {scenario.results.revenue.projected}
                      <div className="text-xs text-gray-400">{scenario.results.revenue.capacity}</div>
                    </td>
                  ))}
                </tr>

                {/* Utilization */}
                <tr>
                  <td className="py-3 px-4 text-gray-300 font-medium">⚡ Utilization Target</td>
                  {displayScenarios.map(scenario => (
                    <td key={scenario.id} className="py-3 px-4 text-center text-gray-200">
                      {scenario.results.utilization.projected}
                      <div className="text-xs text-green-400">✅ Target achieved</div>
                    </td>
                  ))}
                </tr>

                {/* Risk Level */}
                <tr>
                  <td className="py-3 px-4 text-gray-300 font-medium">🚨 Risk Level</td>
                  {displayScenarios.map(scenario => (
                    <td key={scenario.id} className="py-3 px-4 text-center">
                      <Badge variant="outline" className={getRiskColor(scenario.results.risk)}>
                        {scenario.results.risk.toUpperCase()}
                      </Badge>
                      <div className="text-xs text-gray-400 mt-1">{scenario.results.payback} payback</div>
                    </td>
                  ))}
                </tr>

                {/* Implementation */}
                <tr>
                  <td className="py-3 px-4 text-gray-300 font-medium">⏰ Implementation</td>
                  {displayScenarios.map(scenario => (
                    <td key={scenario.id} className="py-3 px-4 text-center">
                      <span className={getImplementationColor(scenario.results.implementation)}>
                        {scenario.results.implementation.toUpperCase()}
                      </span>
                      <div className="text-xs text-gray-400 mt-1">{scenario.results.timeline}</div>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderDetailedAnalysis = () => {
    const displayScenarios = getDisplayScenarios();
    
    return (
      <div className="grid gap-6">
        {displayScenarios.map(scenario => {
          const ApproachIcon = APPROACH_ICONS[scenario.approach];
          
          return (
            <Card key={scenario.id} className="bg-gray-800 border-gray-600">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <ApproachIcon 
                        className="h-5 w-5" 
                        style={{ color: APPROACH_COLORS[scenario.approach] }}
                      />
                      <CardTitle className="text-lg text-gray-100">{scenario.name}</CardTitle>
                      {scenario.isRecommended && (
                        <Badge variant="outline" className="border-blue-400 text-blue-400">
                          AI RECOMMENDED
                        </Badge>
                      )}
                    </div>
                    <p className="text-gray-300">{scenario.description}</p>
                    <div className="text-sm text-gray-400">
                      🎯 Strategy: {scenario.strategy}
                    </div>
                  </div>
                  
                  <Button
                    onClick={() => onSelectScenario?.(scenario.id)}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Target className="h-4 w-4 mr-2" />
                    Select Scenario
                  </Button>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Advantages */}
                  <div className="space-y-3">
                    <h4 className="font-medium text-green-400 flex items-center gap-2">
                      <CheckCircle className="h-4 w-4" />
                      Advantages
                    </h4>
                    <ul className="space-y-2">
                      {scenario.advantages.map((advantage, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-gray-300">
                          <ChevronRight className="h-3 w-3 text-green-400 mt-1 flex-shrink-0" />
                          {advantage}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Risks & Challenges */}
                  <div className="space-y-3">
                    <h4 className="font-medium text-red-400 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      Risks & Challenges
                    </h4>
                    <ul className="space-y-2">
                      {scenario.risks.map((risk, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-gray-300">
                          <AlertTriangle className="h-3 w-3 text-red-400 mt-1 flex-shrink-0" />
                          {risk}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Stakeholder Fit */}
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-200 flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Stakeholder Fit Assessment
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {stakeholders.map(stakeholder => {
                      const position = scenario.stakeholderFit[stakeholder.id];
                      const positionColors = {
                        supports: 'bg-green-900 border-green-400 text-green-200',
                        conditions: 'bg-amber-900 border-amber-400 text-amber-200',
                        neutral: 'bg-gray-700 border-gray-400 text-gray-200',
                        opposes: 'bg-red-900 border-red-400 text-red-200'
                      };
                      
                      return (
                        <div 
                          key={stakeholder.id}
                          className={`p-2 rounded border ${positionColors[position] || positionColors.neutral}`}
                        >
                          <div className="flex items-center gap-2 mb-1">
                            {getStakeholderIcon(position)}
                            <span className="text-xs font-medium">{stakeholder.name}</span>
                          </div>
                          <div className="text-xs capitalize">{position}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 pt-3 border-t border-gray-600">
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-gray-600 text-gray-300"
                    onClick={() => onModifyScenario?.(scenario.id)}
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    Modify
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-gray-600 text-gray-300"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Deep Dive
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-gray-600 text-gray-300"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Run Simulation
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    );
  };

  const renderAIRecommendation = () => {
    const recommendedScenario = scenarios.find(s => s.isRecommended);
    if (!recommendedScenario) return null;

    return (
      <Card className="bg-blue-950 border-blue-600">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg text-blue-100 flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-blue-400" />
            AI Recommendation
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-3">
          <div className="text-blue-100">
            <p className="mb-3">
              Based on stakeholder analysis and risk assessment, I recommend <strong>{recommendedScenario.name}</strong>:
            </p>
            
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <ChevronRight className="h-3 w-3 text-blue-400 mt-1 flex-shrink-0" />
                Achieves 90% of revenue goals with 60% less risk than aggressive approach
              </li>
              <li className="flex items-start gap-2">
                <ChevronRight className="h-3 w-3 text-blue-400 mt-1 flex-shrink-0" />
                Addresses financial concerns while supporting growth objectives
              </li>
              <li className="flex items-start gap-2">
                <ChevronRight className="h-3 w-3 text-blue-400 mt-1 flex-shrink-0" />
                Provides manageable timeline for quality hiring and onboarding
              </li>
              <li className="flex items-start gap-2">
                <ChevronRight className="h-3 w-3 text-blue-400 mt-1 flex-shrink-0" />
                Maintains operational feasibility across all departments
              </li>
            </ul>

            <div className="mt-4 p-3 bg-blue-900 rounded">
              <div className="text-sm text-blue-200">
                <div className="font-medium mb-1">Expected Outcomes:</div>
                <div>Success probability: 85% • ROI efficiency: 4.1x • Implementation risk: Low-Medium</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="scenario-comparison space-y-6">
      {/* Header */}
      <Card className="bg-gray-800 border-gray-600">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle className="text-xl text-gray-100 flex items-center gap-2">
                <Scale className="h-6 w-6 text-blue-400" />
                Strategic Scenario Analysis
              </CardTitle>
              <p className="text-gray-300">
                Compare alternative approaches to your Q3 hiring challenge with AI-powered analysis
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDetailedAnalysis(!showDetailedAnalysis)}
                className="border-gray-600 text-gray-300"
              >
                {showDetailedAnalysis ? 'Show Matrix' : 'Detailed View'}
              </Button>
              <Button
                onClick={onCreateNewScenario}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Target className="h-4 w-4 mr-2" />
                Generate New Option
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {/* Scenario Selection */}
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm text-gray-300">Compare scenarios:</span>
            <div className="flex gap-2 flex-wrap">
              {scenarios.map(scenario => (
                <Button
                  key={scenario.id}
                  variant={selectedScenarios.includes(scenario.id) ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleScenarioSelection(scenario.id)}
                  className={selectedScenarios.includes(scenario.id) 
                    ? "bg-blue-600 hover:bg-blue-700" 
                    : "border-gray-600 text-gray-300"
                  }
                >
                  {scenario.name}
                </Button>
              ))}
            </div>
          </div>
          
          <div className="text-xs text-gray-400">
            Select up to 3 scenarios for comparison • {selectedScenarios.length}/3 selected
          </div>
        </CardContent>
      </Card>

      {/* AI Recommendation */}
      {renderAIRecommendation()}

      {/* Comparison Content */}
      {showDetailedAnalysis ? renderDetailedAnalysis() : renderComparisonMatrix()}

      {/* Action Buttons */}
      <Card className="bg-gray-800 border-gray-600">
        <CardContent className="p-4">
          <div className="flex gap-3 justify-center">
            <Button variant="outline" className="border-gray-600 text-gray-300">
              <Settings className="h-4 w-4 mr-2" />
              Modify Options
            </Button>
            <Button variant="outline" className="border-gray-600 text-gray-300">
              <Eye className="h-4 w-4 mr-2" />
              Deep Dive Analysis
            </Button>
            <Button variant="outline" className="border-gray-600 text-gray-300">
              <Users className="h-4 w-4 mr-2" />
              Discuss with Team
            </Button>
            <Button className="bg-green-600 hover:bg-green-700">
              <CheckCircle className="h-4 w-4 mr-2" />
              Make Decision
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};