import React from 'react';
import { Row, Col, Card, Typography, theme, Divider } from 'antd';

const { Text, Title } = Typography;
const { useToken } = theme;

interface KPIDisplaysProps {
  simulationData: any;
  formatNumber: (value: number) => string;
  selectedYear: string;
  setSelectedYear: (year: string) => void;
}

const KPIDisplays: React.FC<KPIDisplaysProps> = ({ 
  simulationData, 
  formatNumber, 
  selectedYear, 
  setSelectedYear 
}) => {
  const { token } = useToken();

  const getYearData = () => {
    // Get baseline data from aggregated KPIs for comparison
    const aggregatedKpis = simulationData?.kpis || {};
    const baselineFinancial = aggregatedKpis.financial || {};
    
    const baseData = {
      financial: baselineFinancial, // Use aggregated KPIs as source of truth
      growth: aggregatedKpis.growth,
      journeys: aggregatedKpis.journeys
    };

    // Only update non-financial data with year-specific information
    if (simulationData?.years?.[selectedYear]) {
      const yearData = simulationData.years[selectedYear];
      
      // Update growth data with year-specific FTE if available
      if (yearData.total_fte && baseData.growth) {
        baseData.growth = {
          ...baseData.growth,
          current_total_fte: yearData.total_fte,
          total_fte: yearData.total_fte,
          baseline_total_fte: baseData.growth.baseline_total_fte || 0,
          non_debit_ratio: baseData.growth.non_debit_ratio || 0,
          non_debit_ratio_baseline: baseData.growth.non_debit_ratio_baseline || 0
        };
      }

      // Calculate year-specific journey distribution
      const yearJourneys = calculateYearSpecificJourneys(yearData);
      if (yearJourneys) {
        baseData.journeys = yearJourneys;
      }
    }

    // Ensure proper field mapping for growth data
    if (baseData.growth && !baseData.growth.total_fte) {
      baseData.growth = {
        ...baseData.growth,
        total_fte: baseData.growth.current_total_fte || 0,
        baseline_total_fte: baseData.growth.baseline_total_fte || 0,
        non_debit_ratio: baseData.growth.non_debit_ratio || 0,
        non_debit_ratio_baseline: baseData.growth.non_debit_ratio_baseline || 0
      };
    }

    // Debug logging to verify aggregated KPIs are being used
    console.log(`[KPI DEBUG] Year ${selectedYear} using aggregated KPIs:`, {
      net_sales: baseData.financial?.net_sales,
      net_sales_baseline: baseData.financial?.net_sales_baseline,
      ebitda: baseData.financial?.ebitda,
      ebitda_baseline: baseData.financial?.ebitda_baseline,
      margin: baseData.financial?.margin,
      total_fte: baseData.growth?.total_fte,
      source: 'aggregated_kpis'
    });

    return baseData;
  };

  const calculateYearSpecificJourneys = (yearData: any) => {
    if (!yearData?.offices) return simulationData?.kpis?.journeys;

    // Journey level mappings
    const journeyMappings = {
      "Journey 1": ["A", "AC", "C"],
      "Journey 2": ["SrC", "AM"], 
      "Journey 3": ["M", "SrM"],
      "Journey 4": ["PiP"]
    };

    const journeyTotals: { [key: string]: number } = {
      "Journey 1": 0,
      "Journey 2": 0,
      "Journey 3": 0,
      "Journey 4": 0
    };

    // Calculate journey totals from year-specific office data
    Object.values(yearData.offices).forEach((officeData: any) => {
      const levels = officeData.levels || {};
      
      // Process consultant, sales, recruitment levels
      ['Consultant', 'Sales', 'Recruitment'].forEach(role => {
        const roleData = levels[role] || {};
        Object.entries(roleData).forEach(([level, levelResults]: [string, any]) => {
          if (Array.isArray(levelResults) && levelResults.length > 0) {
            // Get latest month data
            const latestData = levelResults[levelResults.length - 1];
            const fteCount = latestData?.total || 0;
            
            // Map to journey
            Object.entries(journeyMappings).forEach(([journeyName, journeyLevels]) => {
              if (journeyLevels.includes(level)) {
                journeyTotals[journeyName] += fteCount;
              }
            });
          }
        });
      });
    });

    const totalFte = Object.values(journeyTotals).reduce((sum: number, value: number) => sum + value, 0);
    const journeyPercentages: { [key: string]: number } = {};
    
    Object.entries(journeyTotals).forEach(([journey, count]) => {
      journeyPercentages[journey] = totalFte > 0 ? (count / totalFte * 100) : 0;
    });

    return {
      journey_totals: journeyTotals,
      journey_percentages: journeyPercentages,
      journey_totals_baseline: simulationData?.kpis?.journeys?.journey_totals_baseline || {},
      journey_percentages_baseline: simulationData?.kpis?.journeys?.journey_percentages_baseline || {}
    };
  };

  const renderFinancialKPIs = () => {
    const data = getYearData();
    if (!data.financial) return null;

    const financial = data.financial;
    
    return (
      <Card 
        title="💰 Financial Performance" 
        style={{ marginBottom: 24 }}
        extra={<Text type="secondary" style={{ fontSize: '12px' }}>Year {selectedYear}</Text>}
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Text type="secondary">Revenue</Text>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                {formatNumber(financial.net_sales)}
              </div>
              <Text type="secondary" style={{ 
                color: (financial.net_sales - financial.net_sales_baseline) > 0 ? token.colorSuccess : 
                       (financial.net_sales - financial.net_sales_baseline) < 0 ? token.colorError : token.colorTextSecondary 
              }}>
                vs Baseline: {formatNumber(financial.net_sales - financial.net_sales_baseline)}
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Text type="secondary">EBITDA</Text>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                {formatNumber(financial.ebitda)}
              </div>
              <Text type="secondary" style={{ 
                color: (financial.ebitda - financial.ebitda_baseline) > 0 ? token.colorSuccess : 
                       (financial.ebitda - financial.ebitda_baseline) < 0 ? token.colorError : token.colorTextSecondary 
              }}>
                vs Baseline: {formatNumber(financial.ebitda - financial.ebitda_baseline)}
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Text type="secondary">Margin</Text>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                {(financial.margin * 100).toFixed(1)}%
              </div>
              <Text type="secondary" style={{ 
                color: (financial.margin - financial.margin_baseline) > 0 ? token.colorSuccess : 
                       (financial.margin - financial.margin_baseline) < 0 ? token.colorError : token.colorTextSecondary 
              }}>
                vs Baseline: {((financial.margin - financial.margin_baseline) * 100).toFixed(1)}pp
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Text type="secondary">Avg Rate</Text>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                {financial.avg_hourly_rate.toFixed(0)} SEK
              </div>
              <Text type="secondary" style={{ 
                color: (financial.avg_hourly_rate - financial.avg_hourly_rate_baseline) > 0 ? token.colorSuccess : 
                       (financial.avg_hourly_rate - financial.avg_hourly_rate_baseline) < 0 ? token.colorError : token.colorTextSecondary 
              }}>
                vs Baseline: {(financial.avg_hourly_rate - financial.avg_hourly_rate_baseline).toFixed(0)} SEK
              </Text>
            </Card>
          </Col>
        </Row>
      </Card>
    );
  };

  const renderWorkforceInsights = () => {
    const data = getYearData();
    if (!data.growth) return null;

    const growth = data.growth;
    const totalGrowthAbs = growth.total_fte - growth.baseline_total_fte;
    const totalGrowthPct = growth.baseline_total_fte > 0 ? 
      ((growth.total_fte - growth.baseline_total_fte) / growth.baseline_total_fte * 100) : 0;
    
    return (
      <Card title="👥 Workforce Dynamics" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Card size="small">
              <Text type="secondary">Total Growth</Text>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                {totalGrowthPct.toFixed(1)}%
              </div>
              <Text type="secondary">
                {totalGrowthAbs > 0 ? '+' : ''}{totalGrowthAbs} FTE
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card size="small">
              <Text type="secondary">Current FTE</Text>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                {growth.total_fte}
              </div>
              <Text type="secondary">
                Baseline: {growth.baseline_total_fte}
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card size="small">
              <Text type="secondary">Non-debit Ratio</Text>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                {growth.non_debit_ratio.toFixed(1)}%
              </div>
              <Text type="secondary">
                Baseline: {growth.non_debit_ratio_baseline.toFixed(1)}%
              </Text>
            </Card>
          </Col>
        </Row>
      </Card>
    );
  };

  const renderSeniorityDistribution = () => {
    const data = getYearData();
    if (!data.journeys) return null;

    const journeys = data.journeys;
    
    return (
      <Card title="📊 Seniority Distribution" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          {Object.entries(journeys.journey_totals).map(([journey, total]) => {
            const current = total as number;
            const baseline = journeys.journey_totals_baseline[journey] || 0;
            const change = current - baseline;
            const currentPct = journeys.journey_percentages[journey] || 0;
            
            return (
              <Col xs={24} sm={12} md={6} key={journey}>
                <Card size="small">
                  <Text type="secondary">{journey}</Text>
                  <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                    {current} FTE ({currentPct.toFixed(1)}%)
                  </div>
                  <Text type="secondary" style={{ 
                    color: change > 0 ? token.colorSuccess : change < 0 ? token.colorError : token.colorTextSecondary 
                  }}>
                    {change > 0 ? '+' : ''}{change} vs baseline
                  </Text>
                </Card>
              </Col>
            );
          })}
        </Row>
      </Card>
    );
  };

  const renderYearOverYearComparison = () => {
    if (!simulationData?.years) return null;

    const years = Object.keys(simulationData.years).sort();
    if (years.length <= 1) return null;

    return (
      <Card title="📈 Year-over-Year Progression" style={{ marginBottom: 24 }}>
        <Row gutter={[8, 8]} style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: 8 }}>
          <Col span={3}><Text strong>Year</Text></Col>
          <Col span={4}><Text strong>Revenue</Text></Col>
          <Col span={3}><Text strong>FTE</Text></Col>
          <Col span={4}><Text strong>EBITDA</Text></Col>
          <Col span={3}><Text strong>Margin</Text></Col>
          <Col span={4}><Text strong>Change</Text></Col>
        </Row>
        {years.map((year, index) => {
          const yearData = simulationData.years[year];
          const prevYear = index > 0 ? simulationData.years[years[index - 1]] : null;
          const revenueChange = prevYear ? 
            ((yearData.total_revenue - prevYear.total_revenue) / prevYear.total_revenue * 100).toFixed(1) + '%' : 
            'Baseline';
          
          return (
            <Row key={year} gutter={[8, 8]} style={{ 
              fontSize: '11px', 
              marginBottom: 4,
              backgroundColor: year === selectedYear ? token.colorPrimaryBg : 'transparent',
              padding: '4px 0',
              borderRadius: year === selectedYear ? '4px' : '0px'
            }}>
              <Col span={3}><Text strong>{year}</Text></Col>
              <Col span={4}><Text>{formatNumber(yearData.total_revenue || 0)}</Text></Col>
              <Col span={3}><Text>{yearData.total_fte || 0}</Text></Col>
              <Col span={4}><Text>{formatNumber(yearData.ebitda || 0)}</Text></Col>
              <Col span={3}><Text>{((yearData.margin || 0) * 100).toFixed(1)}%</Text></Col>
              <Col span={4}>
                <Text style={{ 
                  color: revenueChange !== 'Baseline' && parseFloat(revenueChange) > 0 ? 
                    token.colorSuccess : 
                    revenueChange !== 'Baseline' && parseFloat(revenueChange) < 0 ? 
                      token.colorError : 
                      token.colorTextSecondary 
                }}>
                  {revenueChange}
                </Text>
              </Col>
            </Row>
          );
        })}
      </Card>
    );
  };

  return (
    <>
      {renderFinancialKPIs()}
      {renderWorkforceInsights()}
      {renderSeniorityDistribution()}
      {renderYearOverYearComparison()}
    </>
  );
};

export default KPIDisplays; 