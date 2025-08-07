/**
 * Enhanced Workforce Management Tab Component
 * Displays workforce KPIs and snapshot population with improved UI
 */
import React, { useState, useEffect } from 'react';
import { 
  OfficeConfig, 
  WorkforceDistribution, 
  WorkforceEntry, 
  STANDARD_ROLES, 
  STANDARD_LEVELS,
  StandardRole,
  StandardLevel
} from '../../types/office';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { KPICard } from './KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Users, UserCheck, Briefcase, Settings } from 'lucide-react';

interface WorkforceTabProps {
  office: OfficeConfig;
}

export const WorkforceTab: React.FC<WorkforceTabProps> = ({ office }) => {
  const [workforceData, setWorkforceData] = useState<WorkforceEntry[]>([]);
  const [originalData, setOriginalData] = useState<WorkforceEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { loadWorkforceDistribution, currentWorkforce } = useBusinessPlanStore();

  // Load workforce data
  useEffect(() => {
    const loadData = async () => {
      if (!office?.id) return;
      
      setLoading(true);
      setError(null);
      
      try {
        await loadWorkforceDistribution(office.id);
      } catch (err) {
        setError('Failed to load workforce data');
        console.error('Error loading workforce:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [office?.id, loadWorkforceDistribution]);

  // Initialize workforce data from store
  useEffect(() => {
    if (currentWorkforce?.workforce) {
      setWorkforceData([...currentWorkforce.workforce]);
      setOriginalData([...currentWorkforce.workforce]);
      setIsDirty(false);
    } else {
      // Initialize with empty data for all role/level combinations
      const emptyWorkforce: WorkforceEntry[] = [];
      STANDARD_ROLES.forEach(role => {
        STANDARD_LEVELS.forEach(level => {
          emptyWorkforce.push({
            role,
            level,
            fte: 0,
            notes: ''
          });
        });
      });
      setWorkforceData(emptyWorkforce);
      setOriginalData(emptyWorkforce);
      setIsDirty(false);
    }
  }, [currentWorkforce]);

  // Check if data has changed
  useEffect(() => {
    const hasChanges = workforceData.some((entry, index) => {
      const original = originalData[index];
      if (!original) return true;
      return entry.fte !== original.fte || entry.notes !== original.notes;
    });
    setIsDirty(hasChanges);
  }, [workforceData, originalData]);

  const handleFteChange = (role: StandardRole, level: StandardLevel, fte: number) => {
    setWorkforceData(prev => prev.map(entry => 
      entry.role === role && entry.level === level 
        ? { ...entry, fte: Math.max(0, fte) }
        : entry
    ));
  };

  const handleNotesChange = (role: StandardRole, level: StandardLevel, notes: string) => {
    setWorkforceData(prev => prev.map(entry => 
      entry.role === role && entry.level === level 
        ? { ...entry, notes }
        : entry
    ));
  };

  const handleSave = async () => {
    if (!office?.id || !isDirty) return;
    
    setSaving(true);
    setError(null);
    
    try {
      // Filter out entries with 0 FTE to keep data clean
      const filteredWorkforce = workforceData.filter(entry => entry.fte > 0);
      
      const workforceDistribution: Omit<WorkforceDistribution, 'id' | 'created_at' | 'updated_at'> = {
        office_id: office.id,
        start_date: new Date().toISOString().split('T')[0], // Today's date
        workforce: filteredWorkforce
      };

      // TODO: Implement actual API call when backend endpoint is available
      // For now, simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('Saving workforce distribution:', workforceDistribution);
      
      setOriginalData([...workforceData]);
      setIsDirty(false);
      
      // Reload data to ensure consistency
      await loadWorkforceDistribution(office.id);
      
    } catch (err) {
      setError('Failed to save workforce data');
      console.error('Error saving workforce:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    setWorkforceData([...originalData]);
    setIsDirty(false);
  };

  const handleQuickFill = (role: StandardRole, totalFte: number) => {
    const roleLevels = STANDARD_LEVELS;
    const ftePerLevel = Math.floor(totalFte / roleLevels.length);
    const remainder = totalFte % roleLevels.length;
    
    setWorkforceData(prev => prev.map(entry => {
      if (entry.role === role) {
        const levelIndex = roleLevels.indexOf(entry.level as StandardLevel);
        const fte = ftePerLevel + (levelIndex < remainder ? 1 : 0);
        return { ...entry, fte };
      }
      return entry;
    }));
  };

  const getTotalFte = () => workforceData.reduce((sum, entry) => sum + entry.fte, 0);
  const getRoleFte = (role: StandardRole) => 
    workforceData.filter(entry => entry.role === role).reduce((sum, entry) => sum + entry.fte, 0);
  const getLevelFte = (level: StandardLevel) => 
    workforceData.filter(entry => entry.level === level).reduce((sum, entry) => sum + entry.fte, 0);

  // Get workforce breakdown for KPI cards
  const getWorkforceKPIs = () => {
    return {
      consultants: getRoleFte('Consultant'),
      sales: getRoleFte('Sales'),
      recruiters: getRoleFte('Recruitment'),
      operations: getRoleFte('Operations')
    };
  };

  // Get snapshot population data for table
  const getSnapshotData = () => {
    const snapshot: Array<{ role: string; level: string; fte: number }> = [];
    
    STANDARD_ROLES.forEach(role => {
      STANDARD_LEVELS.forEach(level => {
        const entry = workforceData.find(e => e.role === role && e.level === level);
        if (entry && entry.fte > 0) {
          snapshot.push({
            role: entry.role,
            level: entry.level,
            fte: entry.fte
          });
        }
      });
    });
    
    return snapshot.sort((a, b) => {
      // Sort by role first, then by level
      if (a.role !== b.role) {
        return STANDARD_ROLES.indexOf(a.role as StandardRole) - STANDARD_ROLES.indexOf(b.role as StandardRole);
      }
      return STANDARD_LEVELS.indexOf(a.level as StandardLevel) - STANDARD_LEVELS.indexOf(b.level as StandardLevel);
    });
  };

  const workforceKPIs = getWorkforceKPIs();
  const snapshotData = getSnapshotData();

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <KPICard key={i} title="Loading..." value={0} loading={true} />
          ))}
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Loading workforce data...</CardTitle>
          </CardHeader>
          <CardContent>
            <LoadingSpinner size="large" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Consultants"
          value={Math.round(workforceKPIs.consultants)}
          unit="FTE"
          subtitle="Billable consultants"
          variant={workforceKPIs.consultants > 0 ? 'success' : 'default'}
        />
        <KPICard
          title="Sales"
          value={Math.round(workforceKPIs.sales)}
          unit="FTE"
          subtitle="Business development"
          variant={workforceKPIs.sales > 0 ? 'success' : 'default'}
        />
        <KPICard
          title="Recruiters"
          value={Math.round(workforceKPIs.recruiters)}
          unit="FTE"
          subtitle="Talent acquisition"
          variant={workforceKPIs.recruiters > 0 ? 'success' : 'default'}
        />
        <KPICard
          title="Operations"
          value={Math.round(workforceKPIs.operations)}
          unit="FTE"
          subtitle="Support functions"
          variant={workforceKPIs.operations > 0 ? 'success' : 'default'}
        />
      </div>

      {/* Snapshot Population Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Snapshot Population
          </CardTitle>
        </CardHeader>
        <CardContent>
          {snapshotData.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Role</TableHead>
                  <TableHead>Level</TableHead>
                  <TableHead className="text-right">FTE</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {snapshotData.map((item, index) => (
                  <TableRow key={`${item.role}-${item.level}`}>
                    <TableCell className="font-medium">{item.role}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{item.level}</Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {Math.round(item.fte)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No workforce data available</p>
              <p className="text-sm mt-1">Configure workforce distribution to see population snapshot</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Total Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserCheck className="h-5 w-5" />
            Total Workforce: {Math.round(getTotalFte())} FTE
          </CardTitle>
        </CardHeader>
      </Card>
    </div>
  );
};