/**
 * Hook for managing AI conversation state and interactions
 * 
 * Manages conversation messages, stakeholder consensus, simulation scenarios,
 * and real-time updates for AI-supported business planning sessions.
 */
import { useState, useEffect, useCallback } from 'react';

// Types
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

// Sample data
const SAMPLE_STAKEHOLDERS: Stakeholder[] = [
  {
    id: 'anna',
    name: 'Anna Eriksson',
    role: 'talent',
    isOnline: true
  },
  {
    id: 'marcus',
    name: 'Marcus Lindqvist',
    role: 'sales',
    isOnline: true
  },
  {
    id: 'sofie',
    name: 'Sofie Andersson',
    role: 'finance',
    isOnline: true
  },
  {
    id: 'erik',
    name: 'Erik Johansson',
    role: 'operations',
    isOnline: false
  }
];

// Sample AI responses for different contexts
const AI_RESPONSES = {
  general: [
    "Thank you for that input. I'm analyzing the implications for our hiring strategy and will update the simulation accordingly.",
    "That's an excellent point. Let me factor that into our analysis and provide updated recommendations.",
    "I understand your concern. Let me run a scenario that addresses this specific issue.",
    "Based on this new information, I'm updating our risk assessment and projected outcomes."
  ],
  talent: [
    "Anna, that market insight is valuable. I'm adjusting our hiring timeline and budget projections based on current market conditions.",
    "Your recruitment pipeline data suggests we should accelerate our talent acquisition strategy. Let me model the impact.",
    "The onboarding capacity constraints you mentioned are important. I'll factor that into our implementation timeline."
  ],
  sales: [
    "Marcus, your pipeline data is crucial for capacity planning. I'm updating our revenue projections accordingly.",
    "The client timeline pressures you mentioned will impact our hiring schedule. Let me optimize for client delivery dates.",
    "Those revenue targets require careful resource allocation. I'm analyzing the optimal hiring strategy to meet them."
  ],
  finance: [
    "Sofie, the budget constraints you've outlined help me optimize our investment strategy. Let me find the most cost-effective approach.",
    "Your ROI requirements are noted. I'm calculating scenarios that maximize return while minimizing financial risk.",
    "The cash flow considerations will influence our hiring timeline. Let me model a phased approach."
  ],
  operations: [
    "Erik, operational feasibility is key to success. I'm ensuring our plans align with your capacity constraints.",
    "The implementation timeline you suggested makes sense from an operations perspective. Updating scenarios accordingly.",
    "Your workspace and resource availability data helps me create more realistic implementation plans."
  ]
};

export const useAIConversation = (officeId: string, year: number) => {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [consensus, setConsensus] = useState<ConsensusState[]>([]);
  const [scenarios, setScenarios] = useState<SimulationScenario[]>([]);
  const [sessionPhase, setSessionPhase] = useState<PlanningSessionPhase>({
    phase: 'discussion',
    progress: 35,
    timeRemaining: '25 min remaining',
    nextMilestone: 'Consensus Building (10 min)'
  });
  const [isProcessing, setIsProcessing] = useState(false);

  // Initialize conversation with sample data
  useEffect(() => {
    const initialMessages: ConversationMessage[] = [
      {
        id: '1',
        sender: 'ai_facilitator',
        content: `I've analyzed Q2 performance data for this office. Revenue grew 15% but consultant utilization dropped to 78%. Based on pipeline data, I recommend focusing on Senior Consultant hiring.\n\n📊 Current state: 42 consultants (18 Senior, 24 Junior)\n🎯 Recommended: +8 Senior Consultants by Q3 end\n💰 Budget impact: +€640K (within allocated budget)\n\nThis would improve utilization to 85% and support the €2.1M Q4 pipeline.`,
        timestamp: new Date(Date.now() - 300000), // 5 minutes ago
        messageType: 'insight'
      },
      {
        id: '2',
        sender: 'stakeholder',
        stakeholderId: 'marcus',
        content: `The pipeline numbers are accurate, but I'm concerned about Q4 capacity. We have three major clients requesting senior resources starting October. Can we accelerate hiring to July instead of August?\n\n📈 Pipeline breakdown:\n• Client A: €800K (6 Senior Consultants, Oct-Dec)\n• Client B: €650K (4 Senior + 2 Junior, Nov-Feb)\n• Client C: €650K (5 Senior, Sep-Jan)`,
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

    // Initialize consensus
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

    // Initialize scenario
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

    setScenarios([initialScenario]);
  }, [officeId, year]);

  // Send message function
  const sendMessage = useCallback(async (content: string, stakeholderId?: string) => {
    if (!content.trim() || isProcessing) return;

    const userMessage: ConversationMessage = {
      id: Date.now().toString(),
      sender: 'stakeholder',
      stakeholderId: stakeholderId || 'user',
      content,
      timestamp: new Date(),
      messageType: 'question'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);

    // Simulate AI response after a delay
    setTimeout(() => {
      const stakeholder = SAMPLE_STAKEHOLDERS.find(s => s.id === stakeholderId);
      const responseContext = stakeholder ? stakeholder.role : 'general';
      const responses = AI_RESPONSES[responseContext as keyof typeof AI_RESPONSES] || AI_RESPONSES.general;
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];

      const aiResponse: ConversationMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai_facilitator',
        content: randomResponse,
        timestamp: new Date(),
        messageType: 'insight'
      };

      setMessages(prev => [...prev, aiResponse]);
      setIsProcessing(false);

      // Update session phase progress occasionally
      if (Math.random() > 0.7) {
        setSessionPhase(prev => ({
          ...prev,
          progress: Math.min(prev.progress + 5, 100)
        }));
      }
    }, 1500 + Math.random() * 1000); // 1.5-2.5 second delay
  }, [isProcessing]);

  // Update consensus
  const updateConsensus = useCallback((stakeholderId: string, position: ConsensusState['position'], confidence: number) => {
    setConsensus(prev => {
      const existing = prev.find(c => c.stakeholder === stakeholderId);
      if (existing) {
        return prev.map(c => 
          c.stakeholder === stakeholderId 
            ? { ...c, position, confidence, lastUpdated: new Date() }
            : c
        );
      } else {
        return [...prev, {
          stakeholder: stakeholderId,
          position,
          confidence,
          conditions: [],
          concerns: [],
          lastUpdated: new Date()
        }];
      }
    });
  }, []);

  // Calculate overall consensus
  const calculateOverallConsensus = useCallback(() => {
    if (consensus.length === 0) return 0;
    const supportWeight = consensus.reduce((acc, item) => {
      const weight = item.position === 'supports' ? 1 : 
                   item.position === 'conditions' ? 0.7 : 
                   item.position === 'neutral' ? 0.5 : 0.2;
      return acc + (weight * item.confidence / 100);
    }, 0);
    return Math.round((supportWeight / consensus.length) * 100);
  }, [consensus]);

  // Create new scenario
  const createScenario = useCallback((name: string, description: string) => {
    const newScenario: SimulationScenario = {
      id: Date.now().toString(),
      name,
      description,
      results: {
        workforce: { current: 42, projected: 46 + Math.floor(Math.random() * 8) },
        revenue: { current: '€1.8M', projected: `€${(1.9 + Math.random() * 0.4).toFixed(1)}M` },
        utilization: { current: '78%', projected: `${80 + Math.floor(Math.random() * 10)}%` },
        investment: `€${(400 + Math.random() * 200).toFixed(0)}K`,
        roi: `${(3.5 + Math.random() * 1.5).toFixed(1)}x by Q4`,
        risk: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
        payback: `${3 + Math.floor(Math.random() * 3)} months`
      },
      isActive: false
    };

    setScenarios(prev => [...prev, newScenario]);
    return newScenario;
  }, []);

  return {
    // State
    messages,
    consensus,
    scenarios,
    sessionPhase,
    isProcessing,
    stakeholders: SAMPLE_STAKEHOLDERS,
    
    // Actions
    sendMessage,
    updateConsensus,
    createScenario,
    
    // Computed
    overallConsensus: calculateOverallConsensus()
  };
};