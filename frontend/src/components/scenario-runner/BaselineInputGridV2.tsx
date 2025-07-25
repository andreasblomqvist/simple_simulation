import React, { useState, forwardRef, useImperativeHandle } from 'react';
import { ColumnDef } from "@tanstack/react-table";
import { Info } from "lucide-react";
import { 
  ROLE_LEVELS, 
  ROLES, 
  DEFAULT_ROLE,
  generateMonthKeys,
} from '../../types/unified-data-structures';
import type {
  LevelType,
  YearMonth,
  BaselineInputData,
  MonthlyValues,
} from '../../types/unified-data-structures';
import { DataTable } from '../ui/data-table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { useToast } from '../ui/use-toast';

// Generate months for 3-year simulation using unified month key generator
const DEFAULT_MONTHS = generateMonthKeys(2025, 1, 2027, 12);

// Utility function to sanitize monthly values
const sanitizeMonthlyValue = (value: any): number => {
  // Convert to number and handle invalid cases
  if (value === null || value === undefined || value === '' || isNaN(value)) {
    return 0;
  }
  const numValue = Number(value);
  return isNaN(numValue) ? 0 : Math.max(0, numValue); // Ensure non-negative
};

// Utility function to sanitize all monthly values in a data structure
const sanitizeMonthlyData = (data: any): any => {
  if (!data || typeof data !== 'object') {
    return {};
  }
  
  const sanitized: any = {};
  
  Object.keys(data).forEach(role => {
    if (data[role] && typeof data[role] === 'object') {
      sanitized[role] = {};
      
      Object.keys(data[role]).forEach(level => {
        if (data[role][level] && typeof data[role][level] === 'object') {
          sanitized[role][level] = {};
          
          Object.keys(data[role][level]).forEach(month => {
            const value = data[role][level][month];
            sanitized[role][level][month] = sanitizeMonthlyValue(value);
          });
        }
      });
    }
  });
  
  return sanitized;
};

// Default values for recruitment and leavers (churn) per role/level/month
const recruitmentDefaults: Record<string, Record<string, Record<string, number | undefined>>> = {
  Consultant: {
    '202501': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202502': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202503': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202504': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202505': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202506': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202507': { A: 5, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202508': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202509': { A: 90, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202510': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202511': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202512': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
  },
  Sales: {},
  Recruitment: {},
};

const leaversDefaults: Record<string, Record<string, Record<string, number | undefined>>> = {
  Consultant: {
    '202501': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 0 },
    '202502': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 0 },
    '202503': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 1 },
    '202504': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 0 },
    '202505': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 0 },
    '202506': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 0 },
    '202507': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 0, PiP: 0 },
    '202508': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 1 },
    '202509': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 2, PiP: 0 },
    '202510': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 1 },
    '202511': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 1, PiP: 1 },
    '202512': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 0 },
  },
  Sales: {},
  Recruitment: {},
};

// Fill Sales and Recruitment with 0s for all months/levels
ROLES.forEach(role => {
  if (role === 'Sales' || role === 'Recruitment') {
    DEFAULT_MONTHS.forEach(month => {
      recruitmentDefaults[role][month] = {};
      leaversDefaults[role][month] = {};
      ROLE_LEVELS[role].forEach(level => {
        recruitmentDefaults[role][month][level] = 0;
        leaversDefaults[role][month][level] = 0;
      });
    });
  }
});

// Extend Consultant defaults to all years (2026, 2027) by copying 2025 values
const extendDefaultsToAllYears = () => {
  // For each year after 2025
  for (let year = 2026; year <= 2027; year++) {
    // For each month in that year
    for (let month = 1; month <= 12; month++) {
      const targetMonth = `${year}${month.toString().padStart(2, '0')}`;
      const sourceMonth = `2025${month.toString().padStart(2, '0')}`;
      
      // Copy recruitment defaults
      if (recruitmentDefaults.Consultant[sourceMonth]) {
        recruitmentDefaults.Consultant[targetMonth] = { ...recruitmentDefaults.Consultant[sourceMonth] };
      }
      
      // Copy churn defaults
      if (leaversDefaults.Consultant[sourceMonth]) {
        leaversDefaults.Consultant[targetMonth] = { ...leaversDefaults.Consultant[sourceMonth] };
      }
    }
  }
};

// Extend defaults to all years
extendDefaultsToAllYears();

// Helper to initialize recruitment/churn data structure with defaults
const initRoleData = () => {
  const data: Record<string, Record<string, Record<string, number | undefined>>> = {};
  ROLES.forEach(role => {
    data[role] = {};
    ROLE_LEVELS[role].forEach(level => {
      data[role][level] = {};
      DEFAULT_MONTHS.forEach(month => {
        // Use defaults if available, else undefined
        data[role][level][month] =
          (role in recruitmentDefaults && month in recruitmentDefaults[role] && level in recruitmentDefaults[role][month])
            ? recruitmentDefaults[role][month][level]
            : undefined;
      });
    });
  });
  return data;
};

const initLeaverRoleData = () => {
  const data: Record<string, Record<string, Record<string, number | undefined>>> = {};
  ROLES.forEach(role => {
    data[role] = {};
    ROLE_LEVELS[role].forEach(level => {
      data[role][level] = {};
      DEFAULT_MONTHS.forEach(month => {
        // Use defaults if available, else undefined
        data[role][level][month] =
          (role in leaversDefaults && month in leaversDefaults[role] && level in leaversDefaults[role][month])
            ? leaversDefaults[role][month][level]
            : undefined;
      });
    });
  });
  return data;
};

interface BaselineInputGridProps {
  onNext: (data: any) => void;
  initialData?: any;
}

// Function to initialize data from existing baseline input
const initializeFromBaseline = (initialData: any, dataType: 'recruitment' | 'churn') => {
  // Always expect unified nested structure
  if (!initialData?.global?.[dataType]) {
    return initRoleData();
  }
  const sourceData = initialData.global[dataType];
  // sourceData: { Consultant: { levels: { A: { recruitment: { values: { '202501': 10, ... } }, churn: ... }, ... } }, ... }
  const data: any = {};
  ROLES.forEach(role => {
    data[role] = {};
    const roleLevels = sourceData[role]?.levels || {};
    ROLE_LEVELS[role as keyof typeof ROLE_LEVELS]?.forEach(level => {
      // Default to empty object if missing
      const levelData = roleLevels[level] || {};
      // For recruitment: levelData.recruitment?.values; for churn: levelData.churn?.values
      const values = (dataType === 'recruitment')
        ? levelData.recruitment?.values || {}
        : levelData.churn?.values || {};
      data[role][level] = {};
      DEFAULT_MONTHS.forEach(month => {
        data[role][level][month] = values[month] !== undefined ? values[month] : undefined;
      });
    });
  });
  return data;
};

interface MonthRowData {
  month: string;
  [key: string]: any; // For dynamic level columns
}

const BaselineInputGridV2 = forwardRef<any, BaselineInputGridProps>(({ onNext, initialData }, ref) => {
  const [activeTab, setActiveTab] = useState('recruitment');
  const [selectedRole, setSelectedRole] = useState(DEFAULT_ROLE);
  const [recruitmentData, setRecruitmentData] = useState(() => initializeFromBaseline(initialData, 'recruitment'));
  const [leaversData, setLeaversData] = useState(() => initializeFromBaseline(initialData, 'churn'));
  const { toast } = useToast();

  useImperativeHandle(ref, () => ({
    getCurrentData: () => {
      // Build unified nested structure for baseline_input
      return {
        global: {
          recruitment: recruitmentData,
          churn: leaversData,
        }
      };
    }
  }));

  const handleCellChange = (month: string, level: string, value: number | null) => {
    // Sanitize the input value
    const sanitizedValue = sanitizeMonthlyValue(value);
    
    if (activeTab === 'recruitment') {
      setRecruitmentData(prev => ({
        ...prev,
        [selectedRole]: {
          ...prev[selectedRole],
          [level]: {
            ...prev[selectedRole][level],
            [month]: sanitizedValue
          }
        }
      }));
    } else {
      setLeaversData(prev => ({
        ...prev,
        [selectedRole]: {
          ...prev[selectedRole],
          [level]: {
            ...prev[selectedRole][level],
            [month]: sanitizedValue
          }
        }
      }));
    }
  };

  // Function to apply 2025 values to all years
  const handleApplyForAllYears = () => {
    const currentData = activeTab === 'recruitment' ? recruitmentData : leaversData;
    const setData = activeTab === 'recruitment' ? setRecruitmentData : setLeaversData;
    
    // Get 2025 values for the selected role
    const year2025Values: Record<string, Record<string, number | undefined>> = {};
    ROLE_LEVELS[selectedRole].forEach(level => {
      year2025Values[level] = {};
      // Get all 2025 months (202501-202512)
      for (let month = 1; month <= 12; month++) {
        const monthKey = `2025${month.toString().padStart(2, '0')}`;
        year2025Values[level][monthKey] = currentData[selectedRole]?.[level]?.[monthKey];
      }
    });

    // Apply 2025 values to all subsequent years (2026, 2027, etc.)
    setData(prev => {
      const newData = { ...prev };
      
      // For each year after 2025
      for (let year = 2026; year <= 2027; year++) {
        // For each month in that year
        for (let month = 1; month <= 12; month++) {
          const targetMonth = `${year}${month.toString().padStart(2, '0')}`;
          const sourceMonth = `2025${month.toString().padStart(2, '0')}`;
          
          // Copy values for each level
          ROLE_LEVELS[selectedRole].forEach(level => {
            if (!newData[selectedRole]) newData[selectedRole] = {};
            if (!newData[selectedRole][level]) newData[selectedRole][level] = {};
            
            newData[selectedRole][level][targetMonth] = sanitizeMonthlyValue(year2025Values[level][sourceMonth]);
          });
        }
      }
      
      return newData;
    });

    toast({
      title: "Values Applied",
      description: `Applied 2025 ${activeTab} values to all years for ${selectedRole}`,
    });
  };

  const handleNext = () => {
    // Sanitize all data before sending to parent
    const sanitizedRecruitmentData = sanitizeMonthlyData(recruitmentData);
    const sanitizedLeaversData = sanitizeMonthlyData(leaversData);
    
    const baselineInput = {
      global: {
        recruitment: sanitizedRecruitmentData,
        churn: sanitizedLeaversData,
      }
    };
    onNext(baselineInput);
  };

  // Build DataTable columns
  const levels = ROLE_LEVELS[selectedRole];
  const columns: ColumnDef<MonthRowData>[] = [
    {
      accessorKey: "month",
      header: "Month",
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("month")}</div>
      ),
    },
    ...levels.map(level => ({
      accessorKey: level,
      header: level,
      cell: ({ row }: { row: any }) => {
        const value = row.getValue(level) as number | undefined;
        return (
          <Input
            type="number"
            min="0"
            value={value || ''}
            onChange={(e) => {
              const newValue = e.target.value === '' ? null : Number(e.target.value);
              handleCellChange(row.getValue("month"), level, newValue);
            }}
            className="w-20 h-8"
          />
        );
      },
    })),
  ];

  // Prepare table data
  const tableData: MonthRowData[] = DEFAULT_MONTHS.map(month => ({
    month,
    ...levels.reduce((acc, level) => {
      acc[level] = activeTab === 'recruitment' 
        ? recruitmentData[selectedRole]?.[level]?.[month]
        : leaversData[selectedRole]?.[level]?.[month];
      return acc;
    }, {} as Record<string, number | undefined>),
  }));

  return (
    <div className="space-y-6 p-6">
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">
            Baseline Input Configuration
          </h2>
          <p className="text-muted-foreground">
            Configure monthly recruitment and churn values for each role and level
          </p>
        </div>
        
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Apply for All Years</AlertTitle>
          <AlertDescription className="space-y-2">
            <p>Click the button below to copy all 2025 values to subsequent years (2026, 2027, etc.). This ensures the simulation has complete data for all years.</p>
            <Button 
              onClick={handleApplyForAllYears}
              size="sm"
              className="mt-2"
            >
              Apply 2025 Values to All Years
            </Button>
          </AlertDescription>
        </Alert>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="recruitment">Recruitment</TabsTrigger>
          <TabsTrigger value="churn">Churn (Leavers)</TabsTrigger>
        </TabsList>
        
        <TabsContent value="recruitment" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recruitment Planning</CardTitle>
              <CardDescription>
                Configure monthly recruitment targets for each role and level
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium">Role:</label>
                <Select value={selectedRole} onValueChange={setSelectedRole}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ROLES.map(role => (
                      <SelectItem key={role} value={role}>{role}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <DataTable
                columns={columns}
                data={tableData}
                enablePagination={false}
                enableColumnToggle={false}
                enableSelection={false}
              />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="churn" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Churn (Leavers) Planning</CardTitle>
              <CardDescription>
                Configure monthly turnover expectations for each role and level
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium">Role:</label>
                <Select value={selectedRole} onValueChange={setSelectedRole}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ROLES.map(role => (
                      <SelectItem key={role} value={role}>{role}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <DataTable
                columns={columns}
                data={tableData}
                enablePagination={false}
                enableColumnToggle={false}
                enableSelection={false}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex justify-end">
        <Button onClick={handleNext} size="lg">
          Next
        </Button>
      </div>
    </div>
  );
});

BaselineInputGridV2.displayName = 'BaselineInputGridV2';

export default BaselineInputGridV2;