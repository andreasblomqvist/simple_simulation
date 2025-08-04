/**
 * Consensus Tracker Component
 * 
 * Real-time consensus tracking and decision point analysis for AI-supported business planning.
 * Shows stakeholder positions, confidence levels, and resolution paths.
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Separator } from '../ui/separator';
import {
  CheckCircle,
  AlertTriangle,
  Users,
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  Clock,
  Target,
  ChevronRight,
  Lightbulb,
  BarChart3,
  TrendingUp
} from 'lucide-react';

interface Stakeholder {
  id: string;
  name: string;
  role: 'talent' | 'sales' | 'finance' | 'operations';
  avatar?: string;
  isOnline: boolean;
}

interface ConsensusState {
  stakeholder: string;
  position: 'supports' | 'neutral' | 'opposes' | 'conditions';
  confidence: number; // 0-100
  conditions: string[];
  concerns: string[];
  lastUpdated: Date;
}

interface DecisionPoint {
  id: string;
  title: string;
  description: string;
  urgency: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
  deadline?: Date;
}

interface Props {
  consensus: ConsensusState[];
  stakeholders: Stakeholder[];
  currentDecision?: DecisionPoint;
  onPositionUpdate?: (stakeholderId: string, position: ConsensusState['position'], confidence: number) => void;
  onRequestResolution?: (decisionId: string) => void;
}

const STAKEHOLDER_COLORS = {
  talent: '#10B981',
  sales: '#3B82F6',
  finance: '#F59E0B',
  operations: '#8B5CF6'
};

const STAKEHOLDER_AVATARS = {
  talent: '👤',
  sales: '💼',
  finance: '💰',
  operations: '🔧'
};

export const ConsensusTracker: React.FC<Props> = ({
  consensus,
  stakeholders,
  currentDecision,
  onPositionUpdate,
  onRequestResolution
}) => {
  const [showDetails, setShowDetails] = useState(false);

  const getStakeholderInfo = (stakeholderId: string) => {
    return stakeholders.find(s => s.id === stakeholderId);
  };

  const calculateOverallConsensus = () => {
    if (consensus.length === 0) return 0;
    const supportWeight = consensus.reduce((acc, item) => {
      const weight = item.position === 'supports' ? 1 : 
                   item.position === 'conditions' ? 0.7 : 
                   item.position === 'neutral' ? 0.5 : 0.2;
      return acc + (weight * item.confidence / 100);
    }, 0);
    return Math.round((supportWeight / consensus.length) * 100);
  };

  const getConsensusLevel = (percentage: number) => {
    if (percentage >= 80) return { level: 'strong', color: 'text-green-400', bgColor: 'bg-green-900' };
    if (percentage >= 60) return { level: 'moderate', color: 'text-amber-400', bgColor: 'bg-amber-900' };
    return { level: 'weak', color: 'text-red-400', bgColor: 'bg-red-900' };
  };

  const getPositionIcon = (position: ConsensusState['position']) => {
    switch (position) {
      case 'supports': return <ThumbsUp className="h-4 w-4 text-green-400" />;
      case 'opposes': return <ThumbsDown className="h-4 w-4 text-red-400" />;
      case 'neutral': return <MessageCircle className="h-4 w-4 text-gray-400" />;
      case 'conditions': return <AlertTriangle className="h-4 w-4 text-amber-400" />;
    }
  };

  const getPositionColor = (position: ConsensusState['position']) => {
    switch (position) {
      case 'supports': return 'border-green-400 text-green-400';
      case 'opposes': return 'border-red-400 text-red-400';
      case 'neutral': return 'border-gray-400 text-gray-400';
      case 'conditions': return 'border-amber-400 text-amber-400';
    }
  };

  const overallConsensus = calculateOverallConsensus();
  const consensusInfo = getConsensusLevel(overallConsensus);

  return (
    <div className="consensus-tracker space-y-4">
      {/* Current Decision Point */}
      {currentDecision && (
        <Card className="bg-gray-800 border-gray-600">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
                  <Target className="h-5 w-5 text-blue-400" />
                  Decision Point
                </CardTitle>
                <h3 className="text-xl font-bold text-gray-100">{currentDecision.title}</h3>
                <p className="text-gray-300">{currentDecision.description}</p>
              </div>
              
              <div className="flex items-center gap-2">
                <Badge 
                  variant="outline" 
                  className={`${
                    currentDecision.urgency === 'high' ? 'border-red-400 text-red-400' :
                    currentDecision.urgency === 'medium' ? 'border-amber-400 text-amber-400' :
                    'border-green-400 text-green-400'
                  }`}
                >
                  {currentDecision.urgency.toUpperCase()} URGENCY
                </Badge>
                
                {currentDecision.deadline && (
                  <div className="flex items-center gap-1 text-sm text-gray-400">
                    <Clock className="h-4 w-4" />
                    <span>{currentDecision.deadline.toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </div>
          </CardHeader>
        </Card>
      )}

      {/* Overall Consensus Status */}
      <Card className="bg-gray-800 border-gray-600">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
            <Users className="h-5 w-5 text-blue-400" />
            Consensus Dashboard
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Overall Consensus Level */}
          <div className={`p-4 rounded-lg ${consensusInfo.bgColor}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <BarChart3 className={`h-5 w-5 ${consensusInfo.color}`} />
                <span className="font-medium text-gray-100">Overall Consensus</span>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-100">{overallConsensus}%</div>
                <div className={`text-sm ${consensusInfo.color}`}>{consensusInfo.level.toUpperCase()}</div>
              </div>
            </div>
            <Progress value={overallConsensus} className="h-2" />
          </div>

          {/* Stakeholder Positions */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-200">Stakeholder Positions</h4>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="text-gray-400 hover:text-gray-200"
              >
                {showDetails ? 'Hide Details' : 'Show Details'}
              </Button>
            </div>

            <div className="grid gap-3">
              {consensus.map(item => {
                const stakeholder = getStakeholderInfo(item.stakeholder);
                if (!stakeholder) return null;

                return (
                  <motion.div
                    key={item.stakeholder}
                    layout
                    className="p-3 bg-gray-700 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div 
                          className="w-8 h-8 rounded-full flex items-center justify-center text-sm"
                          style={{ backgroundColor: STAKEHOLDER_COLORS[stakeholder.role] }}
                        >
                          {STAKEHOLDER_AVATARS[stakeholder.role]}
                        </div>
                        <div>
                          <div className="font-medium text-gray-200">{stakeholder.name}</div>
                          <div className="text-xs text-gray-400 capitalize">{stakeholder.role}</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                          {getPositionIcon(item.position)}
                          <Badge variant="outline" className={getPositionColor(item.position)}>
                            {item.position.toUpperCase()}
                          </Badge>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-200">{item.confidence}%</div>
                          <div className="text-xs text-gray-400">confidence</div>
                        </div>
                      </div>
                    </div>

                    <AnimatePresence>
                      {showDetails && (item.conditions.length > 0 || item.concerns.length > 0) && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="mt-3 pt-3 border-t border-gray-600 space-y-2"
                        >
                          {item.conditions.length > 0 && (
                            <div>
                              <div className="text-xs font-medium text-amber-400 mb-1">Conditions:</div>
                              <ul className="space-y-1">
                                {item.conditions.map((condition, index) => (
                                  <li key={index} className="text-xs text-gray-300 flex items-start gap-2">
                                    <ChevronRight className="h-3 w-3 text-amber-400 mt-0.5 flex-shrink-0" />
                                    {condition}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {item.concerns.length > 0 && (
                            <div>
                              <div className="text-xs font-medium text-red-400 mb-1">Concerns:</div>
                              <ul className="space-y-1">
                                {item.concerns.map((concern, index) => (
                                  <li key={index} className="text-xs text-gray-300 flex items-start gap-2">
                                    <AlertTriangle className="h-3 w-3 text-red-400 mt-0.5 flex-shrink-0" />
                                    {concern}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* Consensus Analysis */}
          <div className="p-3 bg-gray-700 rounded border border-blue-600">
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="h-4 w-4 text-blue-400" />
              <span className="text-sm font-medium text-gray-200">AI Consensus Analysis</span>
            </div>
            
            <div className="text-sm text-gray-300 space-y-2">
              {overallConsensus >= 80 && (
                <p>Strong consensus achieved! The team is aligned and ready to proceed with implementation.</p>
              )}
              
              {overallConsensus >= 60 && overallConsensus < 80 && (
                <p>Moderate consensus detected. Address remaining conditions and concerns to strengthen alignment.</p>
              )}
              
              {overallConsensus < 60 && (
                <p>Consensus building needed. Key stakeholders have concerns that require resolution before proceeding.</p>
              )}

              {/* Specific recommendations based on positions */}
              {consensus.some(c => c.position === 'conditions') && (
                <div className="mt-2 p-2 bg-amber-900 rounded text-amber-200">
                  <div className="font-medium text-xs mb-1">🎯 Next Steps:</div>
                  <div className="text-xs">Address stakeholder conditions to improve consensus level</div>
                </div>
              )}

              {consensus.some(c => c.position === 'opposes') && (
                <div className="mt-2 p-2 bg-red-900 rounded text-red-200">
                  <div className="font-medium text-xs mb-1">⚠️ Critical Issue:</div>
                  <div className="text-xs">Strong opposition detected - requires immediate attention</div>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          {currentDecision && (
            <div className="flex gap-2 pt-3 border-t border-gray-600">
              <Button
                variant="outline"
                size="sm"
                className="flex-1 border-gray-600 text-gray-300"
                onClick={() => onRequestResolution?.(currentDecision.id)}
              >
                <Target className="h-4 w-4 mr-2" />
                Request AI Resolution
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                className="border-gray-600 text-gray-300"
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                Facilitate Discussion
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};