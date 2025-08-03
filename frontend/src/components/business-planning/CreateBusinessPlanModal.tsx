/**
 * Create Business Plan Modal
 * 
 * Modal dialog for creating new business plans with office selection,
 * naming, and workflow choice (AI conversation vs manual entry)
 */
import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter
} from '../ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { Badge } from '../ui/badge';
import { 
  Building2, 
  Bot, 
  Edit, 
  Calendar,
  Sparkles,
  Calculator
} from 'lucide-react';
import type { OfficeConfig } from '../../types/office';

interface Props {
  open: boolean;
  onClose: () => void;
  offices: OfficeConfig[];
  onCreatePlan: (data: {
    name: string;
    officeId: string;
    year: number;
    workflow: 'ai' | 'manual';
  }) => void;
}

export const CreateBusinessPlanModal: React.FC<Props> = ({
  open,
  onClose,
  offices,
  onCreatePlan
}) => {
  const [planName, setPlanName] = useState('');
  const [selectedOfficeId, setSelectedOfficeId] = useState('');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedWorkflow, setSelectedWorkflow] = useState<'ai' | 'manual'>('ai');

  const availableYears = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() + i);
  const selectedOffice = offices.find(office => office.id === selectedOfficeId);

  const handleCreate = () => {
    if (!planName.trim() || !selectedOfficeId) return;

    onCreatePlan({
      name: planName.trim(),
      officeId: selectedOfficeId,
      year: selectedYear,
      workflow: selectedWorkflow
    });

    // Reset form
    setPlanName('');
    setSelectedOfficeId('');
    setSelectedYear(new Date().getFullYear());
    setSelectedWorkflow('ai');
    onClose();
  };

  const handleCancel = () => {
    // Reset form
    setPlanName('');
    setSelectedOfficeId('');
    setSelectedYear(new Date().getFullYear());
    setSelectedWorkflow('ai');
    onClose();
  };

  // Auto-generate plan name when office/year changes
  React.useEffect(() => {
    if (selectedOffice && !planName) {
      setPlanName(`${selectedOffice.name} ${selectedYear} Business Plan`);
    }
  }, [selectedOffice, selectedYear, planName]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-gray-800 border-gray-600 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold text-white flex items-center gap-2">
            <Building2 className="h-5 w-5 text-blue-400" />
            Create Business Plan
          </DialogTitle>
          <DialogDescription className="text-gray-300">
            Create a new business plan for strategic workforce planning. Choose your preferred workflow to get started.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Office Selection */}
          <div className="space-y-2">
            <Label htmlFor="office" className="text-sm font-medium text-gray-200">
              Office
            </Label>
            <Select value={selectedOfficeId} onValueChange={setSelectedOfficeId}>
              <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                <SelectValue placeholder="Select an office" />
              </SelectTrigger>
              <SelectContent className="bg-gray-700 border-gray-600">
                {offices.map(office => (
                  <SelectItem 
                    key={office.id} 
                    value={office.id}
                    className="text-white hover:bg-gray-600"
                  >
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-gray-400" />
                      {office.name}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Year Selection */}
          <div className="space-y-2">
            <Label htmlFor="year" className="text-sm font-medium text-gray-200">
              Year
            </Label>
            <Select value={selectedYear.toString()} onValueChange={(value) => setSelectedYear(parseInt(value))}>
              <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-gray-700 border-gray-600">
                {availableYears.map(year => (
                  <SelectItem 
                    key={year} 
                    value={year.toString()}
                    className="text-white hover:bg-gray-600"
                  >
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      {year}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Plan Name */}
          <div className="space-y-2">
            <Label htmlFor="name" className="text-sm font-medium text-gray-200">
              Plan Name
            </Label>
            <Input
              id="name"
              value={planName}
              onChange={(e) => setPlanName(e.target.value)}
              placeholder="Enter business plan name"
              className="bg-gray-700 border-gray-600 text-white placeholder-gray-400"
            />
          </div>

          {/* Workflow Selection */}
          <div className="space-y-3">
            <Label className="text-sm font-medium text-gray-200">
              Planning Workflow
            </Label>
            <div className="grid grid-cols-1 gap-3">
              {/* AI Conversation Option */}
              <div
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  selectedWorkflow === 'ai'
                    ? 'border-blue-500 bg-blue-950/30'
                    : 'border-gray-600 bg-gray-700/50 hover:bg-gray-700'
                }`}
                onClick={() => setSelectedWorkflow('ai')}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-4 h-4 rounded-full border-2 mt-0.5 ${
                    selectedWorkflow === 'ai'
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-400'
                  }`} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Bot className="h-4 w-4 text-blue-400" />
                      <span className="font-medium text-white">AI-Guided Conversation</span>
                      <Badge variant="outline" className="text-xs border-blue-400 text-blue-400">
                        <Sparkles className="h-3 w-3 mr-1" />
                        Recommended
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-300">
                      Interactive conversation to gather recruitment, sales, and financial targets with contextual guidance.
                    </p>
                  </div>
                </div>
              </div>

              {/* Manual Entry Option */}
              <div
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  selectedWorkflow === 'manual'
                    ? 'border-blue-500 bg-blue-950/30'
                    : 'border-gray-600 bg-gray-700/50 hover:bg-gray-700'
                }`}
                onClick={() => setSelectedWorkflow('manual')}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-4 h-4 rounded-full border-2 mt-0.5 ${
                    selectedWorkflow === 'manual'
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-400'
                  }`} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Calculator className="h-4 w-4 text-green-400" />
                      <span className="font-medium text-white">Manual Entry</span>
                    </div>
                    <p className="text-sm text-gray-300">
                      Direct access to detailed planning tables for precise monthly data entry across all metrics.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            onClick={handleCancel}
            className="border-gray-600 text-gray-300 hover:bg-gray-700"
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreate}
            disabled={!planName.trim() || !selectedOfficeId}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {selectedWorkflow === 'ai' ? (
              <>
                <Bot className="h-4 w-4 mr-2" />
                Start AI Planning
              </>
            ) : (
              <>
                <Edit className="h-4 w-4 mr-2" />
                Start Manual Entry
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};