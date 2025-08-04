/**
 * Mock AI Planning Scenarios Data
 * 
 * Sample data for demonstrating the AI conversational planning interface
 * with realistic Stockholm office Q3 2025 planning scenarios.
 */

interface MockScenario {
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

export const mockAIScenarios: MockScenario[] = [
  {
    id: 'conservative',
    name: 'Conservative Growth',
    description: 'Gradual hiring with mix of 4 Senior + 4 Junior consultants, current salary bands',
    strategy: 'Risk-averse approach focusing on quality over speed',
    approach: 'conservative',
    results: {
      workforce: { current: 42, projected: 50 },
      revenue: { current: '€1.8M', projected: '€1.9M', capacity: '76% of pipeline' },
      utilization: { current: '78%', projected: '82%' },
      investment: '€320K',
      budgetUsage: '43% of budget',
      roi: '3.2x by Q4',
      risk: 'low',
      payback: '5 months',
      timeline: 'Aug-Oct',
      implementation: 'comfortable'
    },
    advantages: [
      'Lower financial risk and comfortable cash flow',
      'Quality control with standard hiring timeline',
      'Current salary structure maintained',
      'Junior consultants provide growth opportunity'
    ],
    risks: [
      'May miss Q4 pipeline opportunities (€200K potential loss)',
      'Junior consultants need 2-3 months training',
      'Utilization improvement delayed until Q4',
      'Competitive disadvantage in talent market'
    ],
    stakeholderFit: {
      anna: 'supports',
      marcus: 'opposes',
      sofie: 'supports',
      erik: 'supports'
    }
  },
  {
    id: 'moderate',
    name: 'Balanced Strategy',
    description: '6 Senior Consultants over July-September with selective market rate adjustments',
    strategy: 'Phased approach balancing growth with risk management',
    approach: 'moderate',
    results: {
      workforce: { current: 42, projected: 48 },
      revenue: { current: '€1.8M', projected: '€2.1M', capacity: '90% of pipeline' },
      utilization: { current: '78%', projected: '84%' },
      investment: '€410K',
      budgetUsage: '55% of budget',
      roi: '4.1x by Q4',
      risk: 'medium',
      payback: '4 months',
      timeline: 'July-Sep',
      implementation: 'manageable'
    },
    advantages: [
      'Captures 90% of Q4 pipeline opportunities',
      'Balanced risk profile with manageable timeline',
      'Maintains financial efficiency and flexibility',
      'Allows for market rate adjustments where needed'
    ],
    risks: [
      'Still requires some hiring acceleration',
      'Partial market rate adjustment may affect retention',
      'May need client timeline negotiation for 10% shortfall'
    ],
    stakeholderFit: {
      anna: 'supports',
      marcus: 'conditions',
      sofie: 'supports',
      erik: 'supports'
    },
    isRecommended: true
  },
  {
    id: 'aggressive',
    name: 'Accelerated Growth',
    description: '8 Senior Consultants by August with full market rate salaries',
    strategy: 'Aggressive hiring to capture full pipeline opportunity',
    approach: 'aggressive',
    results: {
      workforce: { current: 42, projected: 50 },
      revenue: { current: '€1.8M', projected: '€2.3M', capacity: '100% of pipeline' },
      utilization: { current: '78%', projected: '85%' },
      investment: '€490K',
      budgetUsage: '65% of budget',
      roi: '4.3x by Q4',
      risk: 'high',
      payback: '4 months',
      timeline: 'July-Aug',
      implementation: 'aggressive'
    },
    advantages: [
      'Captures full Q4 pipeline opportunity (€2.3M)',
      'Optimal utilization rate achieved quickly',
      'Strong competitive market positioning',
      'Maximum growth potential with high returns'
    ],
    risks: [
      'Aggressive hiring timeline with quality vs speed trade-offs',
      'Significant salary investment sets expensive precedent',
      'Onboarding capacity stretched to limits',
      'Higher execution complexity and coordination needs'
    ],
    stakeholderFit: {
      anna: 'conditions',
      marcus: 'supports',
      sofie: 'conditions',
      erik: 'neutral'
    }
  }
];

export const mockStakeholders = [
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

export const mockDecisionSummary = {
  title: 'Q3 Hiring Strategy: Phased Approach',
  description: 'Phase 1 (July): Hire 4 Senior Consultants in Stockholm. Phase 2 (September): Add 2 more if Volvo contract confirmed. Budget approved: €340K initial, €170K conditional.',
  impact: {
    revenue: '+€2.1M (Q4)',
    utilization: '78% → 85%',
    budget: '€490K total',
    risk: 'medium' as const,
    timeline: '4-month payback'
  },
  stakeholderStatus: [
    {
      name: 'Anna Eriksson',
      role: 'talent',
      status: 'approved' as const
    },
    {
      name: 'Marcus Lindqvist',
      role: 'sales',
      status: 'approved' as const
    },
    {
      name: 'Sofie Andersson',
      role: 'finance',
      status: 'conditions' as const
    },
    {
      name: 'Erik Johansson',
      role: 'operations',
      status: 'approved' as const
    }
  ]
};

export const mockNextActions = [
  {
    assignee: 'Anna (Talent Manager)',
    task: 'Contact top 3 recruitment agencies for Senior Consultant pipeline',
    deadline: 'June 30'
  },
  {
    assignee: 'Marcus (Sales Manager)',
    task: 'Finalize Volvo contract timeline and requirements',
    deadline: 'July 15'
  },
  {
    assignee: 'Sofie (Finance Manager)',
    task: 'Secure board approval for Phase 2 conditional budget',
    deadline: 'June 25'
  },
  {
    assignee: 'Erik (Operations)',
    task: 'Prepare onboarding program for rapid integration',
    deadline: 'July 1'
  }
];

export const mockPlanningSession = {
  sessionId: 'stockholm-q3-2025',
  office: 'Stockholm Office Q3 2025',
  duration: '45 min session',
  participantCount: 4,
  decisionCount: 1,
  consensusLevel: 85
};