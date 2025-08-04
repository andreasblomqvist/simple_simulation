/**
 * AI-Supported Conversational Business Planning Interface
 * 
 * Complete replacement for multi-table interface with AI-facilitated conversations,
 * real-time simulation integration, consensus tracking, and stakeholder management.
 * Based on detailed mockups from ai-conversation-interface-mockups.md
 */
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { Progress } from '../ui/progress';
import { Separator } from '../ui/separator';
import {
  Bot,
  Users,
  Clock,
  Send,
  Mic,
  Camera,
  Target,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  MessageCircle,
  BarChart3,
  Lightbulb,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Calendar,
  Building2,
  User,
  Settings,
  Play,
  Pause,
  RefreshCw,
  Save,
  Share,
  FileDown,
  ChevronRight,
  Eye,
  EyeOff
} from 'lucide-react';
// import { useBusinessPlanStore } from '../../stores/businessPlanStore';
// import { useOfficeStore } from '../../stores/officeStore';
import type { OfficeConfig } from '../../types/office';
import { mockStakeholders } from '../../data/mockAIScenarios';

// Types for the conversation interface
interface Stakeholder {
  id: string;
  name: string;
  role: 'talent' | 'sales' | 'finance' | 'operations';
  avatar?: string;
  isOnline: boolean;
}

interface ConversationMessage {
  id: string;
  sender: 'ai_facilitator' | 'stakeholder' | 'system';
  stakeholderId?: string;
  content: string;
  timestamp: Date;
  messageType: 'insight' | 'question' | 'proposal' | 'concern' | 'data' | 'decision';
  attachments?: {
    type: 'simulation' | 'data' | 'chart';
    data: any;
  }[];
}

interface ConsensusState {
  stakeholder: string;
  position: 'supports' | 'neutral' | 'opposes' | 'conditions';
  confidence: number; // 0-100
  conditions: string[];
  concerns: string[];
  lastUpdated: Date;
}

interface SimulationScenario {
  id: string;
  name: string;
  description: string;
  results: {
    workforce: { current: number; projected: number };
    revenue: { current: string; projected: string };
    utilization: { current: string; projected: string };
    investment: string;
    roi: string;
    risk: 'low' | 'medium' | 'high';
    payback: string;
  };
  isActive: boolean;
}

interface PlanningSessionPhase {
  phase: 'discussion' | 'analysis' | 'consensus' | 'decision';
  progress: number;
  timeRemaining?: string;
  nextMilestone?: string;
}

interface Props {
  office: OfficeConfig;
  year: number;
  onYearChange: (year: number) => void;
}


const STAKEHOLDER_COLORS = {
  talent: '#10B981', // Green
  sales: '#3B82F6',  // Blue
  finance: '#F59E0B', // Amber
  operations: '#8B5CF6' // Purple
};

const STAKEHOLDER_AVATARS = {
  talent: '👤',
  sales: '💼',
  finance: '💰',
  operations: '🔧'
};

export const AIConversationalPlanningInterface: React.FC<Props> = ({ 
  office, 
  year, 
  onYearChange 
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [sessionPhase, setSessionPhase] = useState<PlanningSessionPhase>({
    phase: 'discussion',
    progress: 35,
    timeRemaining: '25 min remaining',
    nextMilestone: 'Consensus Building (10 min)'
  });
  const [consensus, setConsensus] = useState<ConsensusState[]>([]);
  const [activeScenarios, setActiveScenarios] = useState<SimulationScenario[]>([]);
  const [selectedStakeholder, setSelectedStakeholder] = useState<string | null>('ai_facilitator');
  const [showLiveSimulation, setShowLiveSimulation] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Initialize with sample conversation
  useEffect(() => {
    const initialMessages: ConversationMessage[] = [
      {
        id: '1',
        sender: 'ai_facilitator',
        content: `I've analyzed Q2 performance data for ${office.name}. Revenue grew 15% but consultant utilization dropped to 78%. Based on pipeline data, I recommend focusing on Senior Consultant hiring.\n\n📊 Current state: 42 consultants (18 Senior, 24 Junior)\n🎯 Recommended: +8 Senior Consultants by Q3 end\n💰 Budget impact: +€640K (within allocated budget)\n\nThis would improve utilization to 85% and support the €2.1M Q4 pipeline.`,
        timestamp: new Date(Date.now() - 300000), // 5 minutes ago
        messageType: 'insight'
      },
      {
        id: '2',
        sender: 'stakeholder',
        stakeholderId: 'marcus',
        content: `The pipeline numbers are accurate, but I'm concerned about Q4 capacity. We have three major clients (Nordea, Volvo, H&M) requesting senior resources starting October. Can we accelerate hiring to July instead of August?\n\n📈 Pipeline breakdown:\n• Nordea: €800K (6 Senior Consultants, Oct-Dec)\n• Volvo: €650K (4 Senior + 2 Junior, Nov-Feb)\n• H&M: €650K (5 Senior, Sep-Jan)`,
        timestamp: new Date(Date.now() - 240000), // 4 minutes ago
        messageType: 'concern'
      },
      {
        id: '3',
        sender: 'ai_facilitator',
        content: `🔄 Running accelerated hiring scenario...\n\n✅ Analysis complete! July hiring is feasible with these adjustments:\n\n📅 Revised timeline:\n• July: +4 Senior Consultants (€320K)\n• August: +4 Senior Consultants (€320K)\n• Impact: Meet all Q4 pipeline demands with 2-week buffer\n\n⚠️ Anna: This requires accelerating 3 ongoing recruitment processes\n💰 Sofie: Q3 budget impact increases to €430K (€320K under budget)`,
        timestamp: new Date(Date.now() - 180000), // 3 minutes ago
        messageType: 'proposal',
        attachments: [{
          type: 'simulation',
          data: {
            scenario: 'accelerated_hiring',
            workforce: { current: 42, projected: 50 },
            revenue: { current: '€1.8M', projected: '€2.1M' },
            utilization: { current: '78%', projected: '85%' }
          }
        }]
      }
    ];

    setMessages(initialMessages);

    // Initialize consensus states
    const initialConsensus: ConsensusState[] = [
      {
        stakeholder: 'marcus',
        position: 'supports',
        confidence: 95,
        conditions: [],
        concerns: [],
        lastUpdated: new Date()
      },
      {
        stakeholder: 'anna',
        position: 'conditions',
        confidence: 75,
        conditions: ['Market rate salary adjustment', 'Accelerated recruitment timeline'],
        concerns: ['Quality vs speed trade-off'],
        lastUpdated: new Date()
      },
      {
        stakeholder: 'sofie',
        position: 'conditions',
        confidence: 65,
        conditions: ['ROI validation', 'Board approval process'],
        concerns: ['Salary inflation precedent'],
        lastUpdated: new Date()
      }
    ];

    setConsensus(initialConsensus);

    // Initialize active scenario
    const initialScenario: SimulationScenario = {
      id: 'accelerated_hiring',
      name: 'Accelerated July Hiring',
      description: '8 Senior Consultants by August with market rates',
      results: {
        workforce: { current: 42, projected: 50 },
        revenue: { current: '€1.8M', projected: '€2.1M' },
        utilization: { current: '78%', projected: '85%' },
        investment: '€490K',
        roi: '4.3x by Q4',
        risk: 'medium',
        payback: '4 months'
      },
      isActive: true
    };

    setActiveScenarios([initialScenario]);
  }, [office.id]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!currentInput.trim() || isProcessing) return;

    const userMessage: ConversationMessage = {
      id: Date.now().toString(),
      sender: 'stakeholder',
      stakeholderId: selectedStakeholder || 'user',
      content: currentInput,
      timestamp: new Date(),
      messageType: 'question'
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentInput('');
    setIsProcessing(true);

    // Simulate AI response after a delay
    setTimeout(() => {
      const aiResponse: ConversationMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai_facilitator',
        content: `Thank you for that input. I'm analyzing the implications for our hiring strategy and will update the simulation accordingly. Let me process this information and provide recommendations shortly.`,
        timestamp: new Date(),
        messageType: 'insight'
      };

      setMessages(prev => [...prev, aiResponse]);
      setIsProcessing(false);
    }, 2000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getStakeholderInfo = (stakeholderId: string) => {
    return mockStakeholders.find(s => s.id === stakeholderId);
  };

  // Calculate overall consensus percentage
  const overallConsensus = useMemo(() => {
    if (consensus.length === 0) return 0;
    const supportWeight = consensus.reduce((acc, item) => {
      const weight = item.position === 'supports' ? 1 : 
                   item.position === 'conditions' ? 0.7 : 
                   item.position === 'neutral' ? 0.5 : 0.2;
      return acc + (weight * item.confidence / 100);
    }, 0);
    return Math.round((supportWeight / consensus.length) * 100);
  }, [consensus]);

  const renderMessage = (message: ConversationMessage) => {
    const isAI = message.sender === 'ai_facilitator';
    const isSystem = message.sender === 'system';
    const stakeholder = message.stakeholderId ? getStakeholderInfo(message.stakeholderId) : null;

    return (
      <motion.div
        key={message.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className={`flex gap-3 p-4 rounded-lg mb-4 ${
          isAI ? 'bg-blue-950 border-l-4 border-blue-500' :
          isSystem ? 'bg-gray-800 border-l-4 border-gray-500' :
          'bg-gray-800 border-l-4'
        }`}
        style={{
          borderLeftColor: stakeholder ? STAKEHOLDER_COLORS[stakeholder.role] : undefined
        }}
      >
        <div className="flex-shrink-0">
          {isAI ? (
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
              <Bot className="h-5 w-5 text-white" />
            </div>
          ) : stakeholder ? (
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center text-sm"
              style={{ backgroundColor: STAKEHOLDER_COLORS[stakeholder.role] }}
            >
              {STAKEHOLDER_AVATARS[stakeholder.role]}
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
              <User className="h-5 w-5 text-white" />
            </div>
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-medium text-gray-100">
              {isAI ? 'AI Facilitator' : 
               isSystem ? 'System' :
               stakeholder ? `${stakeholder.name} (${stakeholder.role.charAt(0).toUpperCase() + stakeholder.role.slice(1)})` :
               'Unknown'}
            </span>
            <span className="text-xs text-gray-400">
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
            <Badge 
              variant="outline" 
              className="text-xs"
              style={{ 
                borderColor: isAI ? '#3B82F6' : stakeholder ? STAKEHOLDER_COLORS[stakeholder.role] : '#6B7280',
                color: isAI ? '#3B82F6' : stakeholder ? STAKEHOLDER_COLORS[stakeholder.role] : '#6B7280'
              }}
            >
              {message.messageType}
            </Badge>
          </div>
          
          <div className="text-gray-200 whitespace-pre-wrap leading-relaxed">
            {message.content}
          </div>

          {message.attachments && message.attachments.length > 0 && (
            <div className="mt-3 p-3 bg-gray-700 rounded border">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="h-4 w-4 text-blue-400" />
                <span className="text-sm font-medium text-gray-200">Simulation Update</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-gray-400">Workforce:</span>
                  <span className="text-gray-200 ml-2">
                    {message.attachments[0].data.workforce.current} → {message.attachments[0].data.workforce.projected}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Utilization:</span>
                  <span className="text-gray-200 ml-2">
                    {message.attachments[0].data.utilization.current} → {message.attachments[0].data.utilization.projected}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    );
  };

  const renderLiveSimulation = () => {
    const scenario = activeScenarios[0];
    if (!scenario) return null;

    return (
      <Card className="bg-gray-800 border-gray-600">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-400" />
              Live Simulation Dashboard
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowLiveSimulation(!showLiveSimulation)}
              className="text-gray-400 hover:text-gray-200"
            >
              {showLiveSimulation ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          </div>
          <p className="text-sm text-gray-400">
            Scenario: {scenario.name}
          </p>
        </CardHeader>

        {showLiveSimulation && (
          <CardContent className="space-y-4">
            {/* Current Scenario Results */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="p-3 bg-gray-700 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="h-4 w-4 text-green-400" />
                    <span className="text-sm font-medium text-gray-200">Workforce Impact</span>
                  </div>
                  <div className="text-lg font-bold text-gray-100">
                    {scenario.results.workforce.current} → {scenario.results.workforce.projected}
                  </div>
                  <div className="text-xs text-gray-400">Total consultants</div>
                </div>

                <div className="p-3 bg-gray-700 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign className="h-4 w-4 text-blue-400" />
                    <span className="text-sm font-medium text-gray-200">Revenue Capacity</span>
                  </div>
                  <div className="text-lg font-bold text-gray-100">
                    {scenario.results.revenue.current} → {scenario.results.revenue.projected}
                  </div>
                  <div className="text-xs text-gray-400">Q4 projected</div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="p-3 bg-gray-700 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-amber-400" />
                    <span className="text-sm font-medium text-gray-200">Utilization</span>
                  </div>
                  <div className="text-lg font-bold text-gray-100">
                    {scenario.results.utilization.current} → {scenario.results.utilization.projected}
                  </div>
                  <div className="text-xs text-gray-400">Target: 85%</div>
                </div>

                <div className="p-3 bg-gray-700 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="h-4 w-4 text-purple-400" />
                    <span className="text-sm font-medium text-gray-200">Investment & ROI</span>
                  </div>
                  <div className="text-lg font-bold text-gray-100">
                    {scenario.results.investment}
                  </div>
                  <div className="text-xs text-gray-400">ROI: {scenario.results.roi}</div>
                </div>
              </div>
            </div>

            {/* Risk Assessment */}
            <div className="p-3 bg-gray-700 rounded">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className={`h-4 w-4 ${
                    scenario.results.risk === 'low' ? 'text-green-400' :
                    scenario.results.risk === 'medium' ? 'text-amber-400' :
                    'text-red-400'
                  }`} />
                  <span className="text-sm font-medium text-gray-200">Risk Level</span>
                </div>
                <Badge 
                  variant="outline"
                  className={`${
                    scenario.results.risk === 'low' ? 'border-green-400 text-green-400' :
                    scenario.results.risk === 'medium' ? 'border-amber-400 text-amber-400' :
                    'border-red-400 text-red-400'
                  }`}
                >
                  {scenario.results.risk.toUpperCase()}
                </Badge>
              </div>
              <div className="text-sm text-gray-300">
                Payback period: {scenario.results.payback}
              </div>
            </div>

            {/* Consensus Status */}
            <div className="p-3 bg-gray-700 rounded">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle className="h-4 w-4 text-green-400" />
                <span className="text-sm font-medium text-gray-200">Consensus Status</span>
              </div>
              <div className="space-y-2">
                {consensus.map(item => {
                  const stakeholder = getStakeholderInfo(item.stakeholder);
                  if (!stakeholder) return null;

                  return (
                    <div key={item.stakeholder} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: STAKEHOLDER_COLORS[stakeholder.role] }}
                        />
                        <span className="text-xs text-gray-300">{stakeholder.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${
                            item.position === 'supports' ? 'border-green-400 text-green-400' :
                            item.position === 'conditions' ? 'border-amber-400 text-amber-400' :
                            item.position === 'opposes' ? 'border-red-400 text-red-400' :
                            'border-gray-400 text-gray-400'
                          }`}
                        >
                          {item.position}
                        </Badge>
                        <span className="text-xs text-gray-400">{item.confidence}%</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Update Status */}
            <div className="flex items-center justify-between p-2 bg-blue-900 rounded text-sm">
              <div className="flex items-center gap-2 text-blue-200">
                <RefreshCw className={`h-4 w-4 ${isProcessing ? 'animate-spin' : ''}`} />
                <span>Last updated: {new Date().toLocaleTimeString()}</span>
              </div>
              {isProcessing && (
                <span className="text-blue-300 animate-pulse">Processing input...</span>
              )}
            </div>
          </CardContent>
        )}
      </Card>
    );
  };

  const renderMeetingProgress = () => {
    const phaseLabels = {
      discussion: 'Strategy Development',
      analysis: 'Analysis & Modeling',
      consensus: 'Consensus Building',
      decision: 'Final Decision'
    };

    const phaseIcons = {
      discussion: MessageCircle,
      analysis: BarChart3,
      consensus: Users,
      decision: CheckCircle
    };

    return (
      <Card className="bg-gray-800 border-gray-600">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-100">Meeting Progress</h3>
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Clock className="h-4 w-4" />
              <span>{sessionPhase.timeRemaining}</span>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-300">
                Phase 2/4: {phaseLabels[sessionPhase.phase]}
              </span>
              <span className="text-xs text-gray-500">
                Next: {sessionPhase.nextMilestone}
              </span>
            </div>

            <Progress value={sessionPhase.progress} className="h-2" />

            <div className="grid grid-cols-4 gap-2">
              {Object.entries(phaseLabels).map(([phase, label], index) => {
                const Icon = phaseIcons[phase as keyof typeof phaseIcons];
                const isActive = phase === sessionPhase.phase;
                const isCompleted = index < (sessionPhase.progress / 25);

                return (
                  <div 
                    key={phase}
                    className={`flex flex-col items-center p-2 rounded text-xs ${
                      isActive ? 'bg-blue-900 text-blue-200' :
                      isCompleted ? 'bg-green-900 text-green-200' :
                      'bg-gray-700 text-gray-400'
                    }`}
                  >
                    <Icon className="h-4 w-4 mb-1" />
                    <span>{label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };


  return (
    <div className="ai-conversational-planning space-y-6">
      {/* Session Header */}
      <Card className="bg-gradient-to-r from-blue-900 to-purple-900 border-blue-700">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle className="text-2xl text-white flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                SimpleSim AI Planning
              </CardTitle>
              <p className="text-blue-100">
                🎯 {office.name} Office Q3 {year} Planning Session
              </p>
              <div className="flex items-center gap-4 text-sm text-blue-200">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  <span>
                    {mockStakeholders.filter(s => s.isOnline).map(s => 
                      `${s.name} (${s.role.charAt(0).toUpperCase() + s.role.slice(1)})`
                    ).join(' • ')}
                  </span>
                </div>
                <Separator orientation="vertical" className="h-4 bg-blue-300" />
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  <span>Started: 09:30 AM • Duration: 45 mins</span>
                </div>
                <Separator orientation="vertical" className="h-4 bg-blue-300" />
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  <span>Next milestone: Budget approval (Thu 2pm)</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-sm text-blue-200">Consensus Level</div>
                <div className="text-2xl font-bold text-white">{overallConsensus}%</div>
              </div>
              <Progress value={overallConsensus} className="w-20 h-2" />
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Main Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Conversation Panel */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="bg-gray-800 border-gray-600">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-blue-400" />
                AI-Facilitated Conversation
              </CardTitle>
            </CardHeader>
            
            <CardContent>
              {/* Messages */}
              <div className="h-96 overflow-y-auto mb-4 pr-2">
                <AnimatePresence>
                  {messages.map(renderMessage)}
                </AnimatePresence>
                
                {isProcessing && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex gap-3 p-4 rounded-lg mb-4 bg-blue-950 border-l-4 border-blue-500"
                  >
                    <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium text-gray-100">AI Facilitator</span>
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                      <div className="text-gray-200">Processing your input and analyzing implications...</div>
                    </div>
                  </motion.div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <span>Speaking as:</span>
                  <select
                    value={selectedStakeholder || ''}
                    onChange={(e) => setSelectedStakeholder(e.target.value)}
                    className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-gray-200 text-sm"
                  >
                    <option value="user">Anonymous User</option>
                    {mockStakeholders.map(s => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.role.charAt(0).toUpperCase() + s.role.slice(1)})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex gap-2">
                  <Textarea
                    value={currentInput}
                    onChange={(e) => setCurrentInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Type your input or question..."
                    className="flex-1 min-h-[60px] bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400"
                    disabled={isProcessing}
                  />
                  <div className="flex flex-col gap-2">
                    <Button
                      onClick={handleSendMessage}
                      disabled={!currentInput.trim() || isProcessing}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="icon" className="border-gray-600 text-gray-400">
                      <Mic className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="flex gap-2 flex-wrap">
                  <Button variant="outline" size="sm" className="text-xs border-gray-600 text-gray-300">
                    🎯 Set New Target
                  </Button>
                  <Button variant="outline" size="sm" className="text-xs border-gray-600 text-gray-300">
                    📊 Run Simulation
                  </Button>
                  <Button variant="outline" size="sm" className="text-xs border-gray-600 text-gray-300">
                    💾 Save Progress
                  </Button>
                  <Button variant="outline" size="sm" className="text-xs border-gray-600 text-gray-300">
                    📋 Export Summary
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Meeting Progress */}
          {renderMeetingProgress()}
        </div>

        {/* Live Simulation Panel */}
        <div className="space-y-4">
          {renderLiveSimulation()}

          {/* AI Suggestions */}
          <Card className="bg-gray-800 border-gray-600">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-amber-400" />
                AI Suggestions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-2 text-sm">
                <div className="flex items-start gap-2 p-2 bg-gray-700 rounded">
                  <ChevronRight className="h-4 w-4 text-amber-400 mt-0.5" />
                  <span className="text-gray-200">Consider remote hires to accelerate timeline</span>
                </div>
                <div className="flex items-start gap-2 p-2 bg-gray-700 rounded">
                  <ChevronRight className="h-4 w-4 text-amber-400 mt-0.5" />
                  <span className="text-gray-200">Partner with recruiters for market access</span>
                </div>
                <div className="flex items-start gap-2 p-2 bg-gray-700 rounded">
                  <ChevronRight className="h-4 w-4 text-amber-400 mt-0.5" />
                  <span className="text-gray-200">Implement accelerated onboarding program</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="bg-gray-800 border-gray-600">
            <CardContent className="p-4">
              <div className="grid grid-cols-2 gap-2">
                <Button variant="outline" size="sm" className="border-gray-600 text-gray-300">
                  <Save className="h-4 w-4 mr-1" />
                  Save
                </Button>
                <Button variant="outline" size="sm" className="border-gray-600 text-gray-300">
                  <Share className="h-4 w-4 mr-1" />
                  Share
                </Button>
                <Button variant="outline" size="sm" className="border-gray-600 text-gray-300">
                  <FileDown className="h-4 w-4 mr-1" />
                  Export
                </Button>
                <Button variant="outline" size="sm" className="border-gray-600 text-gray-300">
                  <Play className="h-4 w-4 mr-1" />
                  Scenario
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};