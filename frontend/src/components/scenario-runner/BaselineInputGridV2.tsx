import React, { forwardRef, useImperativeHandle } from 'react';
import { ColumnDef } from "@tanstack/react-table";
import { Info } from "lucide-react";
import { ROLE_LEVELS, DEFAULT_ROLE } from '../../types/unified-data-structures';
import type { StandardRole } from '../../types/office';
import { DataTable } from '../ui/data-table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { useBaselineData } from '../../hooks';


interface BaselineInputGridProps {
  onNext: (data: any) => void;
  initialData?: any;
}

interface MonthRowData {
  month: string;
  [key: string]: any; // For dynamic level columns
}

const BaselineInputGridV2 = forwardRef<any, BaselineInputGridProps>(({ onNext, initialData }, ref) => {
  // Use the baseline data hook
  const {
    selectedRole,
    activeTab,
    tableData,
    setSelectedRole,
    setActiveTab,
    handleCellChange,
    handleApplyForAllYears,
    handleNext,
    getCurrentData,
    defaultMonths,
    availableRoles,
    availableLevels
  } = useBaselineData({
    initialData,
    onNext
  });

  // Expose getCurrentData through imperative handle
  useImperativeHandle(ref, () => ({
    getCurrentData
  }));


  // Build DataTable columns
  const columns: ColumnDef<MonthRowData>[] = [
    {
      accessorKey: "month",
      header: "Month",
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("month")}</div>
      ),
    },
    ...availableLevels.map(level => ({
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
                    {availableRoles.map(role => (
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
                    {availableRoles.map(role => (
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