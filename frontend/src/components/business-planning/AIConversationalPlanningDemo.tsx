/**
 * AI Conversational Planning Demo
 * 
 * Comprehensive demonstration of all AI planning features:
 * - Main conversational interface
 * - Consensus tracking
 * - Scenario comparison
 * - Mobile planning view
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import {
  Bot,
  MessageSquare,
  Users,
  BarChart3,
  Smartphone,
  Monitor,
  Target,
  Lightbulb
} from 'lucide-react';

import { AIConversationalPlanningInterface } from './AIConversationalPlanningInterface';
import { ConsensusTracker } from './ConsensusTracker';
import { ScenarioComparison } from './ScenarioComparison';
import { MobilePlanningView } from './MobilePlanningView';

import { 
  mockAIScenarios, 
  mockStakeholders, 
  mockDecisionSummary, 
  mockNextActions, 
  mockPlanningSession 
} from '../../data/mockAIScenarios';

interface Props {
  office: {
    id: string;
    name: string;
  };
  year: number;
  onYearChange: (year: number) => void;
}

export const AIConversationalPlanningDemo: React.FC<Props> = ({
  office,
  year,
  onYearChange
}) => {
  const [activeView, setActiveView] = useState<'desktop' | 'mobile'>('desktop');
  const [currentDecision] = useState({
    id: 'q3-hiring-strategy',
    title: 'Should we proceed with accelerated July hiring at market rates?',
    description: 'The team needs to decide on the hiring strategy for Q3 to support the €2.1M Q4 pipeline.',
    urgency: 'medium' as const,
    impact: 'high' as const,
    deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 1 week from now
  });

  // Sample consensus data
  const [consensus] = useState([
    {
      stakeholder: 'marcus',
      position: 'supports' as const,
      confidence: 95,
      conditions: [],
      concerns: [],
      lastUpdated: new Date()
    },
    {
      stakeholder: 'anna',
      position: 'conditions' as const,
      confidence: 75,
      conditions: ['Market rate salary adjustment', 'Accelerated recruitment timeline'],
      concerns: ['Quality vs speed trade-off'],
      lastUpdated: new Date()
    },
    {
      stakeholder: 'sofie',
      position: 'conditions' as const,
      confidence: 65,
      conditions: ['ROI validation', 'Board approval process'],
      concerns: ['Salary inflation precedent'],
      lastUpdated: new Date()
    },
    {
      stakeholder: 'erik',
      position: 'supports' as const,
      confidence: 85,
      conditions: [],
      concerns: ['Onboarding capacity'],
      lastUpdated: new Date()
    }
  ]);

  const handlePositionUpdate = (stakeholderId: string, position: any, confidence: number) => {
    console.log('Position update:', { stakeholderId, position, confidence });
  };

  const handleRequestResolution = (decisionId: string) => {
    console.log('Request resolution for:', decisionId);
  };

  const handleSelectScenario = (scenarioId: string) => {
    console.log('Selected scenario:', scenarioId);
  };

  const handleModifyScenario = (scenarioId: string) => {
    console.log('Modify scenario:', scenarioId);
  };

  const handleCreateNewScenario = () => {
    console.log('Create new scenario');
  };

  const handleCreateScenario = () => {
    console.log('Create scenario from planning session');
  };

  const handleEmailSummary = () => {
    console.log('Email summary');
  };

  const handleScheduleFollowup = () => {
    console.log('Schedule follow-up');
  };

  const handleSendMessage = (message: string) => {
    console.log('Send message:', message);
  };

  return (
    <div className="ai-planning-demo space-y-6">
      {/* Demo Header */}
      <Card className="bg-gradient-to-r from-indigo-900 to-purple-900 border-indigo-700">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle className="text-2xl text-white flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                AI Conversational Planning Demo
              </CardTitle>
              <p className="text-indigo-100 max-w-3xl">
                Experience the future of business planning with AI-facilitated conversations, 
                real-time simulation integration, and intelligent consensus tracking.
              </p>
              <div className="flex items-center gap-4 text-sm text-indigo-200">
                <Badge variant="outline" className="border-indigo-400 text-indigo-300">
                  <Lightbulb className="h-3 w-3 mr-1" />
                  AI-Powered
                </Badge>
                <Badge variant="outline" className="border-indigo-400 text-indigo-300">
                  <Target className="h-3 w-3 mr-1" />
                  Real-time Simulation
                </Badge>
                <Badge variant="outline" className="border-indigo-400 text-indigo-300">
                  <Users className="h-3 w-3 mr-1" />
                  Consensus Tracking
                </Badge>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant={activeView === 'desktop' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveView('desktop')}
                className={activeView === 'desktop' 
                  ? 'bg-indigo-600 hover:bg-indigo-700' 
                  : 'border-indigo-400 text-indigo-300'
                }
              >
                <Monitor className="h-4 w-4 mr-2" />
                Desktop View
              </Button>
              <Button
                variant={activeView === 'mobile' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveView('mobile')}
                className={activeView === 'mobile' 
                  ? 'bg-indigo-600 hover:bg-indigo-700' 
                  : 'border-indigo-400 text-indigo-300'
                }
              >
                <Smartphone className="h-4 w-4 mr-2" />
                Mobile View
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Desktop View */}
      {activeView === 'desktop' && (
        <Tabs defaultValue="conversation" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 h-12 p-1 rounded-xl bg-gray-800">
            <TabsTrigger value="conversation" className="flex items-center gap-2 text-gray-300">
              <MessageSquare className="h-4 w-4" />
              <span className="hidden sm:inline">AI Conversation</span>
            </TabsTrigger>
            <TabsTrigger value="consensus" className="flex items-center gap-2 text-gray-300">
              <Users className="h-4 w-4" />
              <span className="hidden sm:inline">Consensus Tracker</span>
            </TabsTrigger>
            <TabsTrigger value="scenarios" className="flex items-center gap-2 text-gray-300">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Scenario Comparison</span>
            </TabsTrigger>
            <TabsTrigger value="mobile-preview" className="flex items-center gap-2 text-gray-300">
              <Smartphone className="h-4 w-4" />
              <span className="hidden sm:inline">Mobile Preview</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="conversation">
            <AIConversationalPlanningInterface
              office={office}
              year={year}
              onYearChange={onYearChange}
            />
          </TabsContent>

          <TabsContent value="consensus">
            <div className="space-y-6">
              <Card className="bg-gray-800 border-gray-600">
                <CardHeader>
                  <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
                    <Users className="h-5 w-5 text-blue-400" />
                    Consensus Tracking Demo
                  </CardTitle>
                  <p className="text-gray-300 text-sm">
                    Real-time consensus tracking and decision point analysis for AI-supported business planning.
                  </p>
                </CardHeader>
              </Card>

              <ConsensusTracker
                consensus={consensus}
                stakeholders={mockStakeholders.map(s => ({
                  ...s,
                  isOnline: true
                }))}
                currentDecision={currentDecision}
                onPositionUpdate={handlePositionUpdate}
                onRequestResolution={handleRequestResolution}
              />
            </div>
          </TabsContent>

          <TabsContent value="scenarios">
            <div className="space-y-6">
              <Card className="bg-gray-800 border-gray-600">
                <CardHeader>
                  <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-blue-400" />
                    Scenario Comparison Demo
                  </CardTitle>
                  <p className="text-gray-300 text-sm">
                    Side-by-side analysis of strategic options with AI recommendations and stakeholder fit assessment.
                  </p>
                </CardHeader>
              </Card>

              <ScenarioComparison
                scenarios={mockAIScenarios}
                stakeholders={mockStakeholders}
                onSelectScenario={handleSelectScenario}
                onModifyScenario={handleModifyScenario}
                onCreateNewScenario={handleCreateNewScenario}
              />
            </div>
          </TabsContent>

          <TabsContent value="mobile-preview">
            <div className="space-y-6">
              <Card className="bg-gray-800 border-gray-600">
                <CardHeader>
                  <CardTitle className="text-lg text-gray-100 flex items-center gap-2">
                    <Smartphone className="h-5 w-5 text-blue-400" />
                    Mobile Planning View Demo
                  </CardTitle>
                  <p className="text-gray-300 text-sm">
                    Mobile/tablet optimized view for meeting room tablets with executive summary and quick actions.
                  </p>
                </CardHeader>
              </Card>

              <div className="max-w-md mx-auto">
                <MobilePlanningView
                  session={mockPlanningSession}
                  decision={mockDecisionSummary}
                  nextActions={mockNextActions}
                  onCreateScenario={handleCreateScenario}
                  onEmailSummary={handleEmailSummary}
                  onScheduleFollowup={handleScheduleFollowup}
                  onSendMessage={handleSendMessage}
                />
              </div>
            </div>
          </TabsContent>
        </Tabs>
      )}

      {/* Mobile View */}
      {activeView === 'mobile' && (
        <div className="max-w-md mx-auto">
          <MobilePlanningView
            session={mockPlanningSession}
            decision={mockDecisionSummary}
            nextActions={mockNextActions}
            onCreateScenario={handleCreateScenario}
            onEmailSummary={handleEmailSummary}
            onScheduleFollowup={handleScheduleFollowup}
            onSendMessage={handleSendMessage}
          />
        </div>
      )}
    </div>
  );
};