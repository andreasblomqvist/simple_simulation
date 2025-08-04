/**
 * Mobile Planning View Component
 * 
 * Mobile/tablet optimized view for AI-supported business planning sessions.
 * Designed for meeting room tablets with executive summary and quick actions.
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Separator } from '../ui/separator';
import {
  Bot,
  Users,
  Clock,
  Target,
  TrendingUp,
  DollarSign,
  CheckCircle,
  AlertTriangle,
  MessageCircle,
  Calendar,
  Building2,
  Send,
  Mic,
  Camera,
  FileDown,
  Share,
  Save,
  Play,
  ChevronDown,
  ChevronUp,
  BarChart3,
  Lightbulb
} from 'lucide-react';

interface MobilePlanningSession {
  sessionId: string;
  office: string;
  duration: string;
  participantCount: number;
  decisionCount: number;
  consensusLevel: number;
}

interface DecisionSummary {
  title: string;
  description: string;
  impact: {
    revenue: string;
    utilization: string;
    budget: string;
    risk: 'low' | 'medium' | 'high';
    timeline: string;
  };
  stakeholderStatus: Array<{
    name: string;
    role: string;
    status: 'approved' | 'conditions' | 'cautious' | 'opposed';
  }>;
}

interface NextAction {
  assignee: string;
  task: string;
  deadline: string;
}

interface Props {
  session: MobilePlanningSession;
  decision: DecisionSummary;
  nextActions: NextAction[];
  onCreateScenario?: () => void;
  onEmailSummary?: () => void;
  onScheduleFollowup?: () => void;
  onSendMessage?: (message: string) => void;
}

const STAKEHOLDER_COLORS = {
  talent: '#10B981',
  sales: '#3B82F6',
  finance: '#F59E0B',
  operations: '#8B5CF6'
};

const STATUS_COLORS = {
  approved: 'border-green-400 text-green-400',
  conditions: 'border-amber-400 text-amber-400',
  cautious: 'border-orange-400 text-orange-400',
  opposed: 'border-red-400 text-red-400'
};

const STATUS_ICONS = {
  approved: '✅',
  conditions: '🟡',
  cautious: '⚠️',
  opposed: '❌'
};

export const MobilePlanningView: React.FC<Props> = ({
  session,
  decision,
  nextActions,
  onCreateScenario,
  onEmailSummary,
  onScheduleFollowup,
  onSendMessage
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [quickInput, setQuickInput] = useState('');
  const [activeSection, setActiveSection] = useState<'summary' | 'impact' | 'actions'>('summary');

  const handleSendQuickMessage = () => {
    if (quickInput.trim() && onSendMessage) {
      onSendMessage(quickInput);
      setQuickInput('');
    }
  };

  const renderSessionHeader = () => (
    <Card className="bg-gradient-to-r from-blue-900 to-purple-900 border-blue-700">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="text-white font-medium">SimpleSim AI Planning</div>
              <div className="text-blue-200 text-sm">{session.office} • {new Date().toLocaleTimeString()}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-white text-lg font-bold">{session.consensusLevel}%</div>
            <div className="text-blue-200 text-xs">Consensus</div>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-3 text-center">
          <div className="text-blue-100">
            <div className="text-lg font-bold">{session.duration}</div>
            <div className="text-xs text-blue-200">Duration</div>
          </div>
          <div className="text-blue-100">
            <div className="text-lg font-bold">{session.participantCount}</div>
            <div className="text-xs text-blue-200">Participants</div>
          </div>
          <div className="text-blue-100">
            <div className="text-lg font-bold">{session.decisionCount}</div>
            <div className="text-xs text-blue-200">Decisions</div>
          </div>
          <div className="text-blue-100">
            <div className="text-lg font-bold">{session.consensusLevel}%</div>
            <div className="text-xs text-blue-200">Agreement</div>
          </div>
        </div>

        <Progress value={session.consensusLevel} className="mt-3 h-2" />
      </CardContent>
    </Card>
  );

  const renderDecisionMade = () => (
    <Card className="bg-gray-800 border-gray-600">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-400" />
            Decision Made
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDetails(!showDetails)}
            className="text-gray-400"
          >
            {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div>
          <h3 className="text-xl font-bold text-gray-100 mb-2">{decision.title}</h3>
          <p className="text-gray-300 text-sm leading-relaxed">{decision.description}</p>
        </div>

        <AnimatePresence>
          {showDetails && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4"
            >
              {/* Impact Summary */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-gray-700 rounded">
                  <div className="flex items-center gap-2 mb-1">
                    <DollarSign className="h-4 w-4 text-green-400" />
                    <span className="text-sm font-medium text-gray-200">Revenue Impact</span>
                  </div>
                  <div className="text-lg font-bold text-gray-100">{decision.impact.revenue}</div>
                  <div className="text-xs text-gray-400">Q4 projected</div>
                </div>

                <div className="p-3 bg-gray-700 rounded">
                  <div className="flex items-center gap-2 mb-1">
                    <TrendingUp className="h-4 w-4 text-blue-400" />
                    <span className="text-sm font-medium text-gray-200">Utilization</span>
                  </div>
                  <div className="text-lg font-bold text-gray-100">{decision.impact.utilization}</div>
                  <div className="text-xs text-gray-400">Target achieved</div>
                </div>

                <div className="p-3 bg-gray-700 rounded">
                  <div className="flex items-center gap-2 mb-1">
                    <Target className="h-4 w-4 text-purple-400" />
                    <span className="text-sm font-medium text-gray-200">Investment</span>
                  </div>
                  <div className="text-lg font-bold text-gray-100">{decision.impact.budget}</div>
                  <div className="text-xs text-gray-400">Q3 budget</div>
                </div>

                <div className="p-3 bg-gray-700 rounded">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className={`h-4 w-4 ${
                      decision.impact.risk === 'low' ? 'text-green-400' :
                      decision.impact.risk === 'medium' ? 'text-amber-400' :
                      'text-red-400'
                    }`} />
                    <span className="text-sm font-medium text-gray-200">Risk Level</span>
                  </div>
                  <div className="text-lg font-bold text-gray-100 capitalize">{decision.impact.risk}</div>
                  <div className="text-xs text-gray-400">{decision.impact.timeline}</div>
                </div>
              </div>

              {/* Stakeholder Status */}
              <div>
                <h4 className="text-sm font-medium text-gray-200 mb-3">Stakeholder Status</h4>
                <div className="space-y-2">
                  {decision.stakeholderStatus.map(stakeholder => (
                    <div key={stakeholder.name} className="flex items-center justify-between p-2 bg-gray-700 rounded">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: STAKEHOLDER_COLORS[stakeholder.role as keyof typeof STAKEHOLDER_COLORS] || '#6B7280' }}
                        />
                        <span className="text-sm text-gray-200">{stakeholder.name}</span>
                        <span className="text-xs text-gray-400 capitalize">({stakeholder.role})</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm">{STATUS_ICONS[stakeholder.status]}</span>
                        <Badge variant="outline" className={STATUS_COLORS[stakeholder.status]} size="sm">
                          {stakeholder.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );

  const renderNextActions = () => (
    <Card className="bg-gray-800 border-gray-600">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-blue-400" />
          Next Actions
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-3">
          {nextActions.map((action, index) => (
            <div key={index} className="p-3 bg-gray-700 rounded">
              <div className="flex items-start justify-between mb-2">
                <div className="font-medium text-gray-200">{action.assignee}</div>
                <div className="text-xs text-gray-400">{action.deadline}</div>
              </div>
              <div className="text-sm text-gray-300">{action.task}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  const renderQuickActions = () => (
    <Card className="bg-gray-800 border-gray-600">
      <CardContent className="p-4">
        <div className="grid grid-cols-2 gap-3 mb-4">
          <Button
            onClick={onCreateScenario}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Play className="h-4 w-4 mr-2" />
            Create Scenario
          </Button>
          <Button
            onClick={onEmailSummary}
            variant="outline"
            className="border-gray-600 text-gray-300"
          >
            <Share className="h-4 w-4 mr-2" />
            Email Summary
          </Button>
          <Button
            onClick={onScheduleFollowup}
            variant="outline"
            className="border-gray-600 text-gray-300"
          >
            <Calendar className="h-4 w-4 mr-2" />
            Schedule Follow-up
          </Button>
          <Button
            variant="outline"
            className="border-gray-600 text-gray-300"
          >
            <Save className="h-4 w-4 mr-2" />
            Save Progress
          </Button>
        </div>

        {/* Quick Input */}
        <div className="space-y-3">
          <Separator className="bg-gray-600" />
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Bot className="h-4 w-4 text-blue-400" />
              <span className="text-sm text-gray-300">Quick input...</span>
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={quickInput}
                onChange={(e) => setQuickInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-gray-100 placeholder-gray-400 text-sm"
                onKeyDown={(e) => e.key === 'Enter' && handleSendQuickMessage()}
              />
              <Button
                size="sm"
                onClick={handleSendQuickMessage}
                disabled={!quickInput.trim()}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Send className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="border-gray-600 text-gray-300"
              >
                <Mic className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderAIInsight = () => (
    <Card className="bg-blue-950 border-blue-600">
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div className="space-y-2">
            <div className="text-blue-100 font-medium">AI Facilitator</div>
            <div className="text-blue-200 text-sm leading-relaxed">
              "Excellent progress! Your team has achieved strong consensus on the phased hiring approach. 
              Ready to create a simulation scenario from the agreed plan?"
            </div>
            <div className="flex gap-2 mt-3">
              <Button
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-xs"
                onClick={onCreateScenario}
              >
                Yes, Create Scenario
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="border-blue-400 text-blue-300 text-xs"
              >
                Continue Discussion
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="mobile-planning-view space-y-4 max-w-md mx-auto p-4">
      {renderSessionHeader()}
      {renderDecisionMade()}
      {renderNextActions()}
      {renderAIInsight()}
      {renderQuickActions()}
    </div>
  );
};