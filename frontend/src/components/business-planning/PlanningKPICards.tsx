/**
 * Planning KPI Cards Component
 * 
 * Reusable KPI cards for displaying business plan metrics
 * Extracted from multi-table interface for use in expandable planning grid
 */
import React from 'react';
import { Card, CardContent } from '../ui/card';
import { 
  UserPlus,
  UserMinus,
  ArrowUpRight,
  DollarSign,
  TrendingUp,
  Target
} from 'lucide-react';

interface PlanningKPICardsProps {
  kpis?: {
    totalRecruitment: number;
    totalChurn: number;
    netRecruitment: number;
    netRecruitmentPercent: number;
    netRevenue: number;
    avgPriceIncrease: number;
    avgTargetUTR: number;
  };
  className?: string;
}

// Default mock KPI data - in real implementation, calculate from business plan data
const defaultKpis = {
  totalRecruitment: 48,
  totalChurn: 24,
  netRecruitment: 24,
  netRecruitmentPercent: 15.8,
  netRevenue: 2150000,
  avgPriceIncrease: 5.2,
  avgTargetUTR: 78.5
};

export const PlanningKPICards: React.FC<PlanningKPICardsProps> = ({
  kpis = defaultKpis,
  className = ""
}) => {
  return (
    <div className={`grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 ${className}`}>
      {/* Total Recruitment */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <UserPlus className="h-3 w-3 text-green-400" />
              <span className="text-xs font-medium text-gray-400">Total Recruitment</span>
            </div>
            <div className="text-lg font-bold text-white">
              {kpis.totalRecruitment.toLocaleString()}
            </div>
            <div className="text-xs text-gray-400">yearly</div>
          </div>
        </CardContent>
      </Card>

      {/* Total Churn */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <UserMinus className="h-3 w-3 text-red-400" />
              <span className="text-xs font-medium text-gray-400">Total Churn</span>
            </div>
            <div className="text-lg font-bold text-white">
              {kpis.totalChurn.toLocaleString()}
            </div>
            <div className="text-xs text-gray-400">yearly</div>
          </div>
        </CardContent>
      </Card>

      {/* Net Recruitment */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <ArrowUpRight className={`h-3 w-3 ${kpis.netRecruitment >= 0 ? 'text-green-400' : 'text-red-400'}`} />
              <span className="text-xs font-medium text-gray-400">Net Recruitment</span>
            </div>
            <div className={`text-lg font-bold ${kpis.netRecruitment >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {kpis.netRecruitment >= 0 ? '+' : ''}{kpis.netRecruitment.toLocaleString()}
            </div>
            <div className={`text-xs ${kpis.netRecruitmentPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {kpis.netRecruitmentPercent >= 0 ? '+' : ''}{kpis.netRecruitmentPercent.toFixed(1)}% growth
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Net Revenue */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <DollarSign className="h-3 w-3 text-blue-400" />
              <span className="text-xs font-medium text-gray-400">Net Revenue</span>
            </div>
            <div className="text-lg font-bold text-white">
              €{Math.round(kpis.netRevenue / 1000).toLocaleString()}K
            </div>
            <div className="text-xs text-gray-400">yearly</div>
          </div>
        </CardContent>
      </Card>

      {/* Price Increase */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-3 w-3 text-purple-400" />
              <span className="text-xs font-medium text-gray-400">Price Increase</span>
            </div>
            <div className="text-lg font-bold text-white">
              {kpis.avgPriceIncrease >= 0 ? '+' : ''}{kpis.avgPriceIncrease.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-400">vs baseline</div>
          </div>
        </CardContent>
      </Card>

      {/* Target UTR */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <Target className="h-3 w-3 text-yellow-400" />
              <span className="text-xs font-medium text-gray-400">Target UTR</span>
            </div>
            <div className="text-lg font-bold text-white">
              {kpis.avgTargetUTR.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-400">average</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};