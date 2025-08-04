/**
 * Application settings page
 */
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { Settings as SettingsIcon, Save, TrendingUp, Grid3X3 } from 'lucide-react';
import { DataTableMinimal } from '../components/ui/data-table-minimal';
import type { ColumnDef } from '@tanstack/react-table';

interface ProgressionConfigRow {
  level: string;
  progressionRate: string;
  progressionMonths: string;
  nextLevel: string;
  journey: string;
  timeOnLevel: string;
}

interface CATMatrixRow {
  level: string;
  CAT0: string;
  CAT1: string;
  CAT2: string;
  CAT3: string;
  CAT4: string;
  CAT5: string;
  CAT6: string;
}

// Default progression configuration data from backend
const progressionConfigData: ProgressionConfigRow[] = [
  { level: 'A', progressionRate: '15.0%', progressionMonths: 'Jan, Apr, Jul, Oct', nextLevel: 'AC', journey: 'J-1', timeOnLevel: '6 months' },
  { level: 'AC', progressionRate: '12.0%', progressionMonths: 'Jan, Apr, Jul, Oct', nextLevel: 'C', journey: 'J-1', timeOnLevel: '9 months' },
  { level: 'C', progressionRate: '10.0%', progressionMonths: 'Jan, Jul', nextLevel: 'SrC', journey: 'J-1', timeOnLevel: '12 months' },
  { level: 'SrC', progressionRate: '8.0%', progressionMonths: 'Jan, Jul', nextLevel: 'AM', journey: 'J-2', timeOnLevel: '18 months' },
  { level: 'AM', progressionRate: '6.0%', progressionMonths: 'Jan, Jul', nextLevel: 'M', journey: 'J-2', timeOnLevel: '30 months' },
  { level: 'M', progressionRate: '4.0%', progressionMonths: 'Jan', nextLevel: 'SrM', journey: 'J-3', timeOnLevel: '24 months' },
  { level: 'SrM', progressionRate: '3.0%', progressionMonths: 'Jan', nextLevel: 'Pi', journey: 'J-3', timeOnLevel: '120 months' },
  { level: 'Pi', progressionRate: '2.0%', progressionMonths: 'Jan', nextLevel: 'P', journey: 'J-3', timeOnLevel: '12 months' },
  { level: 'P', progressionRate: '1.0%', progressionMonths: 'Jan', nextLevel: 'X', journey: 'J-3', timeOnLevel: '1000 months' },
];

// CAT Matrix data from backend config - progression probability coefficients (0.0 - 1.0)
const catMatrixData: CATMatrixRow[] = [
  { level: 'A', CAT0: '0%', CAT1: '10%', CAT2: '20%', CAT3: '30%', CAT4: '50%', CAT5: '70%', CAT6: '90%' },
  { level: 'AC', CAT0: '0%', CAT1: '15%', CAT2: '25%', CAT3: '40%', CAT4: '60%', CAT5: '80%', CAT6: '95%' },
  { level: 'C', CAT0: '0%', CAT1: '20%', CAT2: '30%', CAT3: '50%', CAT4: '70%', CAT5: '85%', CAT6: '100%' },
  { level: 'SrC', CAT0: '0%', CAT1: '25%', CAT2: '40%', CAT3: '60%', CAT4: '80%', CAT5: '90%', CAT6: '100%' },
  { level: 'AM', CAT0: '0%', CAT1: '30%', CAT2: '50%', CAT3: '70%', CAT4: '85%', CAT5: '95%', CAT6: '100%' },
  { level: 'M', CAT0: '0%', CAT1: '35%', CAT2: '55%', CAT3: '75%', CAT4: '90%', CAT5: '98%', CAT6: '100%' },
  { level: 'SrM', CAT0: '0%', CAT1: '40%', CAT2: '60%', CAT3: '80%', CAT4: '95%', CAT5: '100%', CAT6: '100%' },
  { level: 'PiP', CAT0: '0%', CAT1: '50%', CAT2: '70%', CAT3: '85%', CAT4: '100%', CAT5: '100%', CAT6: '100%' },
];

const progressionColumns: ColumnDef<ProgressionConfigRow>[] = [
  {
    accessorKey: 'level',
    header: 'Level',
  },
  {
    accessorKey: 'progressionRate',
    header: 'Progression Rate',
  },
  {
    accessorKey: 'progressionMonths',
    header: 'Progression Months',
  },
  {
    accessorKey: 'nextLevel',
    header: 'Next Level',
  },
  {
    accessorKey: 'journey',
    header: 'Journey',
  },
  {
    accessorKey: 'timeOnLevel',
    header: 'Time on Level',
  },
];

const catMatrixColumns: ColumnDef<CATMatrixRow>[] = [
  {
    accessorKey: 'level',
    header: 'Level',
  },
  {
    accessorKey: 'CAT0',
    header: 'CAT0',
  },
  {
    accessorKey: 'CAT1',
    header: 'CAT1',
  },
  {
    accessorKey: 'CAT2',
    header: 'CAT2',
  },
  {
    accessorKey: 'CAT3',
    header: 'CAT3',
  },
  {
    accessorKey: 'CAT4',
    header: 'CAT4',
  },
  {
    accessorKey: 'CAT5',
    header: 'CAT5',
  },
  {
    accessorKey: 'CAT6',
    header: 'CAT6',
  },
];

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <SettingsIcon className="h-5 w-5" />
              Settings
            </CardTitle>
            <Button>
              <Save className="mr-2 h-4 w-4" />
              Save Settings
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">General Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="currency">Default Currency</Label>
                  <Select defaultValue="SEK">
                    <SelectTrigger>
                      <SelectValue placeholder="Select currency" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="SEK">Swedish Krona (SEK)</SelectItem>
                      <SelectItem value="EUR">Euro (EUR)</SelectItem>
                      <SelectItem value="USD">US Dollar (USD)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="timezone">Default Timezone</Label>
                  <Select defaultValue="Europe/Stockholm">
                    <SelectTrigger>
                      <SelectValue placeholder="Select timezone" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Europe/Stockholm">Stockholm</SelectItem>
                      <SelectItem value="Europe/Oslo">Oslo</SelectItem>
                      <SelectItem value="Europe/Helsinki">Helsinki</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Simulation Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="auto-save" className="font-medium">Auto-save scenarios</Label>
                  <Checkbox id="auto-save" defaultChecked />
                </div>
                
                <div className="flex items-center justify-between">
                  <Label htmlFor="debug-logging" className="font-medium">Enable debug logging</Label>
                  <Checkbox id="debug-logging" />
                </div>
                
                <div className="flex items-center justify-between">
                  <Label htmlFor="dark-mode" className="font-medium">Dark mode</Label>
                  <Checkbox id="dark-mode" />
                </div>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Grid3X3 className="h-5 w-5" />
            CAT Matrix Configuration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Configure the Career Advancement Timeline (CAT) values for each level and category.
          </p>
          <p className="text-sm text-muted-foreground mb-4">
            CAT values represent progression probability coefficients (0.0 - 1.0) for each level and category.
          </p>
          <DataTableMinimal 
            columns={catMatrixColumns} 
            data={catMatrixData}
            enablePagination={false}
          />
          <p className="text-xs text-muted-foreground mt-4">
            Values must be between 0.0 and 1.0. Higher values indicate higher progression probability.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Progression Configuration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Default progression rates and schedules used when scenarios don't specify custom progression settings.
          </p>
          <DataTableMinimal 
            columns={progressionColumns} 
            data={progressionConfigData} 
          />
        </CardContent>
      </Card>
    </div>
  );
};