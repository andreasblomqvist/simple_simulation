/**
 * Simple AI Planning Interface
 * 
 * Clean conversation interface with supporting data tables.
 * Left: AI conversation flow for recruitment, sales, and financial planning
 * Right: Historical data tables that update based on conversation context
 */
import React, { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import {
  Bot,
  Send,
  User,
  TrendingUp,
  Users,
  DollarSign,
  Calendar,
  BarChart3
} from 'lucide-react';

interface Message {
  id: string;
  sender: 'ai' | 'user';
  content: string;
  timestamp: Date;
  context?: 'recruitment' | 'sales' | 'financial';
}

interface HistoricalData {
  year: number;
  data: Record<string, number>;
}

interface Props {
  office: {
    id: string;
    name: string;
  };
  year: number;
  onYearChange: (year: number) => void;
  onTabChange?: (tab: string) => void;
}

// Mock historical data
const mockRecruitmentData: HistoricalData[] = [
  { year: 2022, data: { graduates: 28, young_professionals: 15, total: 43 } },
  { year: 2023, data: { graduates: 35, young_professionals: 18, total: 53 } },
  { year: 2024, data: { graduates: 32, young_professionals: 22, total: 54 } }
];

const mockRevenueData: HistoricalData[] = [
  { year: 2022, data: { q1: 45, q2: 48, q3: 42, q4: 55, total: 190 } },
  { year: 2023, data: { q1: 52, q2: 55, q3: 48, q4: 62, total: 217 } },
  { year: 2024, data: { q1: 58, q2: 61, q3: 52, q4: 69, total: 240 } }
];

const mockPriceData: HistoricalData[] = [
  { year: 2022, data: { increase: 4.2 } },
  { year: 2023, data: { increase: 5.1 } },
  { year: 2024, data: { increase: 3.8 } }
];

// Conversation flows
const conversationFlows = {
  recruitment: [
    "How many people do you want to recruit this year?",
    "How do you want to distribute that? Graduates (A-AC) vs Young Professionals (C-SrC)?",
    "Spread out evenly or seasonal recruitment?"
  ],
  sales: [
    "How much sales are we targeting this year?",
    "How is that spread out during the year? Even or seasonal?",
    "Any specific months with higher or lower targets?"
  ],
  financial: [
    "How much can we increase prices this year?",
    "Should this be evenly distributed across all services?",
    "Any specific timing for the price increases?"
  ]
};

export const SimpleAIPlanningInterface: React.FC<Props> = ({
  office,
  year,
  onYearChange,
  onTabChange
}) => {
  // Initialize with initial message, check for new plan context
  const [messages, setMessages] = useState<Message[]>(() => {
    // Check if this is a new business plan creation
    const newPlanData = localStorage.getItem('new-business-plan');
    let planName = 'business plan';
    
    if (newPlanData) {
      const planData = JSON.parse(newPlanData);
      if (planData.officeId === office.id && planData.year === year && planData.workflow === 'ai') {
        planName = planData.name;
      }
    }
    
    return [{
      id: '1',
      sender: 'ai',
      content: `Hello! I'm here to help you create "${planName}" for ${office.name} in ${year}. Let's start with recruitment planning. ${conversationFlows.recruitment[0]}`,
      timestamp: new Date(),
      context: 'recruitment'
    }];
  });
  const [currentInput, setCurrentInput] = useState('');
  const [currentContext, setCurrentContext] = useState<'recruitment' | 'sales' | 'financial'>('recruitment');
  const [conversationStep, setConversationStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [planningData, setPlanningData] = useState<{
    recruitment: Record<string, any>;
    sales: Record<string, any>;
    financial: Record<string, any>;
  }>({
    recruitment: {},
    sales: {},
    financial: {}
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (!currentInput.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: currentInput,
      timestamp: new Date(),
      context: currentContext
    };

    setMessages(prev => [...prev, userMessage]);

    // Generate AI response
    setTimeout(() => {
      let aiResponse = '';
      
      // Check if user is making a correction/modification
      const input = currentInput.toLowerCase();
      if (input.includes('instead') || input.includes('change') || input.includes('actually') || 
          input.includes('correction') || input.includes('modify') || input.includes('update')) {
        aiResponse = "Got it! I've updated that information. " + 
          (conversationStep < conversationFlows[currentContext].length - 1 
            ? conversationFlows[currentContext][conversationStep + 1]
            : "Is there anything else you'd like to adjust for " + currentContext + "?");
      } else {
        // Normal flow progression
        const nextStep = conversationStep + 1;

        if (nextStep < conversationFlows[currentContext].length) {
          aiResponse = conversationFlows[currentContext][nextStep];
          setConversationStep(nextStep);
        } else {
          // Move to next context or wrap up
          if (currentContext === 'recruitment') {
            aiResponse = "Great! Now let's discuss sales targets. " + conversationFlows.sales[0];
            setCurrentContext('sales');
            setConversationStep(0);
          } else if (currentContext === 'sales') {
            aiResponse = "Perfect! Finally, let's talk about pricing strategy. " + conversationFlows.financial[0];
            setCurrentContext('financial');
            setConversationStep(0);
          } else {
            aiResponse = "Excellent! I have all the information needed for your business plan. You can now generate the detailed business plan from our conversation.";
            setIsComplete(true);
          }
        }
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: aiResponse,
        timestamp: new Date(),
        context: currentContext
      };

      setMessages(prev => [...prev, aiMessage]);
    }, 1000);

    setCurrentInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const extractPlanningData = () => {
    // Extract planning data from conversation messages
    const data = {
      recruitment: {},
      sales: {},
      financial: {}
    };

    messages.forEach(message => {
      if (message.sender === 'user') {
        const content = message.content.toLowerCase();
        
        // Extract recruitment data
        if (message.context === 'recruitment') {
          if (content.includes('fte') || content.includes('people')) {
            const numbers = content.match(/\d+/g);
            if (numbers) data.recruitment.total = parseInt(numbers[0]);
          }
          if (content.includes('graduate')) {
            const numbers = content.match(/\d+/g);
            if (numbers) data.recruitment.graduates = parseInt(numbers[0]);
          }
          if (content.includes('young professional') || content.includes('yp')) {
            const numbers = content.match(/\d+/g);
            if (numbers) data.recruitment.youngProfessionals = parseInt(numbers[1] || numbers[0]);
          }
        }
        
        // Extract sales data
        if (message.context === 'sales') {
          if (content.includes('m') || content.includes('million')) {
            const numbers = content.match(/\d+/g);
            if (numbers) data.sales.target = parseInt(numbers[0]);
          }
        }
        
        // Extract financial data
        if (message.context === 'financial') {
          if (content.includes('%') || content.includes('percent')) {
            const numbers = content.match(/\d+/g);
            if (numbers) data.financial.priceIncrease = parseInt(numbers[0]);
          }
        }
      }
    });

    return data;
  };

  const handleGenerateBusinessPlan = () => {
    const extractedData = extractPlanningData();
    
    // Store the AI-generated plan data
    localStorage.setItem('ai-generated-plan', JSON.stringify({
      office: office.id,
      year: year,
      data: extractedData,
      timestamp: new Date().toISOString()
    }));
    
    // Navigate to Office Planning tab using React Router (no page reload)
    if (onTabChange) {
      onTabChange('office-planning');
    }
  };

  const renderSupportingData = () => {
    let data: HistoricalData[] = [];
    let title = '';
    let icon = null;

    switch (currentContext) {
      case 'recruitment':
        data = mockRecruitmentData;
        title = 'Historical Recruitment (FTE)';
        icon = <Users className="h-5 w-5 text-blue-400" />;
        break;
      case 'sales':
        data = mockRevenueData;
        title = 'Historical Revenue (M NOK)';
        icon = <TrendingUp className="h-5 w-5 text-green-400" />;
        break;
      case 'financial':
        data = mockPriceData;
        title = 'Historical Price Increases (%)';
        icon = <DollarSign className="h-5 w-5 text-amber-400" />;
        break;
    }

    return (
      <Card className="bg-gray-800 border-gray-600 h-fit">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
            {icon}
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.map(yearData => (
              <div key={yearData.year} className="p-3 bg-gray-700 rounded">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-200">{yearData.year}</span>
                  {yearData.year === year - 1 && (
                    <Badge variant="outline" className="text-xs border-blue-400 text-blue-400">
                      Latest
                    </Badge>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {Object.entries(yearData.data).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-400 capitalize">{key.replace('_', ' ')}:</span>
                      <span className="text-gray-200 font-medium">
                        {currentContext === 'financial' ? `${value}%` : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="simple-ai-planning p-6" style={{ backgroundColor: '#111827' }}>
      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Conversation Panel */}
        <div className="lg:col-span-2">
          <Card className="bg-gray-800 border-gray-600">
            <CardHeader>
              <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
                <Bot className="h-5 w-5 text-blue-400" />
                Planning Conversation
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* Messages */}
              <div className="h-96 overflow-y-auto mb-4 space-y-4">
                {messages.map(message => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.sender === 'ai' ? 'justify-start' : 'justify-end'}`}
                  >
                    {message.sender === 'ai' && (
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                    )}
                    
                    <div
                      className={`max-w-md p-3 rounded-lg ${
                        message.sender === 'ai'
                          ? 'bg-blue-950 text-blue-100'
                          : 'bg-gray-700 text-gray-100'
                      }`}
                    >
                      <div className="text-sm">{message.content}</div>
                      <div className="text-xs opacity-60 mt-1">
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>

                    {message.sender === 'user' && (
                      <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
                        <User className="h-5 w-5 text-white" />
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="space-y-3">
                <div className="flex gap-2">
                  <Textarea
                    value={currentInput}
                    onChange={(e) => setCurrentInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Type your response..."
                    className="flex-1 min-h-[60px] bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400"
                    disabled={isComplete}
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!currentInput.trim() || isComplete}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>

                {/* Generate Business Plan Button */}
                {isComplete && (
                  <div className="flex justify-center">
                    <Button
                      onClick={handleGenerateBusinessPlan}
                      className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 text-lg font-medium"
                    >
                      <BarChart3 className="h-5 w-5 mr-2" />
                      Generate Business Plan
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Supporting Data Panel */}
        <div className="space-y-4">
          {renderSupportingData()}
          
          {/* Context Indicators */}
          <Card className="bg-gray-800 border-gray-600">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-gray-300">Planning Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {['recruitment', 'sales', 'financial'].map(context => (
                  <div
                    key={context}
                    className={`flex items-center gap-2 p-2 rounded ${
                      currentContext === context
                        ? 'bg-blue-900 text-blue-200'
                        : 'bg-gray-700 text-gray-400'
                    }`}
                  >
                    <div className={`w-2 h-2 rounded-full ${
                      currentContext === context ? 'bg-blue-400' : 'bg-gray-500'
                    }`} />
                    <span className="text-sm capitalize">{context}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};