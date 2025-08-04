/**
 * Aggregated Business Plan Wrapper
 * 
 * Reuses the existing CleanBusinessPlanTable by creating a virtual aggregated office
 */
import React, { useMemo } from 'react';
import { Building2 } from 'lucide-react';
import { Badge } from '../ui/badge';
import { CleanBusinessPlanTable } from './CleanBusinessPlanTable';
import { useOfficeStore } from '../../stores/officeStore';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import type { OfficeConfig } from '../../types/office';

interface AggregatedBusinessPlanWrapperProps {
  selectedOffices: string[];
  year: number;
  onViewOfficePlan?: (officeId: string, year: number) => void;
}

export const AggregatedBusinessPlanWrapper: React.FC<AggregatedBusinessPlanWrapperProps> = ({
  selectedOffices,
  year,
  onViewOfficePlan
}) => {
  const { offices } = useOfficeStore();
  const { monthlyPlans } = useBusinessPlanStore();

  // Create a virtual "aggregated office" 
  const aggregatedOffice = useMemo(() => {
    const officeNames = selectedOffices.map(id => {
      const office = offices.find(o => o.id === id);
      return office ? office.name : id;
    }).join(', ');

    const virtualOffice: OfficeConfig = {
      id: 'aggregated',
      name: `Aggregated: ${officeNames}`,
      country: 'Multiple',
      city: 'Multiple',
      currency: 'EUR',
      timezone: 'UTC',
      isActive: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      baseline_fte: {}, // Will be populated by aggregation
      salaries: {},
      economic_parameters: {
        monthly_hours: 160,
        working_days_per_month: 20,
        revenue_recognition_delay_months: 0,
        churn_rate_annual: 0.15,
        recruitment_cost_per_hire: 5000,
        onboarding_time_months: 3
      }
    };

    return virtualOffice;
  }, [selectedOffices, offices]);

  // Get office names for display
  const officeNames = useMemo(() => {
    const maxDisplay = Math.min(selectedOffices.length, 5);
    const displayOffices = selectedOffices.slice(0, maxDisplay);
    
    return displayOffices.map(id => {
      const office = offices.find(o => o.id === id);
      return office ? office.name : id;
    }).join(', ') + (selectedOffices.length > maxDisplay ? ` (+${selectedOffices.length - maxDisplay} more)` : '');
  }, [selectedOffices, offices]);

  if (selectedOffices.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-muted-foreground">No offices selected for aggregation</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Aggregated Header */}
      <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border">
        <div>
          <h3 className="font-semibold">
            Aggregated Business Plan - {year}
          </h3>
          <div className="flex items-center gap-2 mt-1">
            <Building2 className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              {Math.min(selectedOffices.length, 5)} offices: {officeNames}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <Badge variant="secondary">
            Aggregated data
          </Badge>
          {selectedOffices.length > 5 && (
            <Badge variant="outline">
              Limited to 5 offices
            </Badge>
          )}
        </div>
      </div>

      {/* Use the existing CleanBusinessPlanTable */}
      <CleanBusinessPlanTable 
        office={aggregatedOffice}
        year={year}
      />
    </div>
  );
};