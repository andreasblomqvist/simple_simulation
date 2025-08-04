/**
 * Aggregated Business Planning V2 Page
 * 
 * Enterprise-level business planning with multi-office aggregation
 */
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { CleanBusinessPlanTable } from '../components/business-planning/CleanBusinessPlanTable';
import { 
  Calendar,
  Building2,
  Globe,
  Filter,
  Download,
  Settings,
  Users,
  TrendingUp,
  BarChart3,
  Play
} from 'lucide-react';
import { cn } from '../lib/utils';

interface Office {
  id: string;
  name: string;
  journey?: string;
  total_fte?: number;
}

const JOURNEY_TYPES = [
  { value: 'emerging', label: 'Emerging Offices', color: 'bg-green-100 text-green-800' },
  { value: 'established', label: 'Established Offices', color: 'bg-blue-100 text-blue-800' },
  { value: 'mature', label: 'Mature Offices', color: 'bg-purple-100 text-purple-800' }
];

export const AggregatedBusinessPlanningV2: React.FC = () => {
  const [year, setYear] = useState(new Date().getFullYear());
  const [offices, setOffices] = useState<Office[]>([]);
  const [selectedOffices, setSelectedOffices] = useState<string[]>([]);
  const [journeyFilter, setJourneyFilter] = useState<string | undefined>();
  const [showFilters, setShowFilters] = useState(false);
  const [loading, setLoading] = useState(false);

  // Load available offices
  useEffect(() => {
    const loadOffices = async () => {
      try {
        const response = await fetch('/api/offices');
        if (response.ok) {
          const officesData = await response.json();
          setOffices(officesData);
          
          // Auto-select first few offices by default
          const defaultSelection = officesData.slice(0, 3).map((office: Office) => office.id);
          setSelectedOffices(defaultSelection);
        }
      } catch (error) {
        console.error('Failed to load offices:', error);
      }
    };

    loadOffices();
  }, []);

  const handleOfficeSelection = (officeId: string, checked: boolean) => {
    setSelectedOffices(prev => 
      checked 
        ? [...prev, officeId]
        : prev.filter(id => id !== officeId)
    );
  };

  const handleSelectAllOffices = () => {
    setSelectedOffices(offices.map(office => office.id));
  };

  const handleClearOffices = () => {
    setSelectedOffices([]);
  };

  const handleJourneyFilter = (journey: string) => {
    const newJourney = journey === 'all' ? undefined : journey;
    setJourneyFilter(newJourney);
    
    // Auto-select offices matching the journey
    if (newJourney) {
      const matchingOffices = offices
        .filter(office => office.journey?.toLowerCase() === newJourney.toLowerCase())
        .map(office => office.id);
      setSelectedOffices(matchingOffices);
    }
  };

  const selectedOfficeDetails = offices.filter(office => selectedOffices.includes(office.id));
  const totalSelectedFTE = selectedOfficeDetails.reduce((sum, office) => sum + (office.total_fte || 0), 0);

  return (
    <div className="aggregated-business-planning-page space-y-6 p-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Globe className="h-8 w-8" />
            Aggregated Business Planning
          </h1>
          <p className="text-muted-foreground mt-2">
            Enterprise-level workforce planning across multiple offices
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2"
          >
            <Filter className="h-4 w-4" />
            Filters
          </Button>
          <div className="flex items-center gap-2">
            <Button variant="outline" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Export Excel
            </Button>
            <Button className="flex items-center gap-2">
              <Play className="h-4 w-4" />
              Create Scenario Baseline
            </Button>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Aggregation Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Year Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Planning Year
              </label>
              <Input
                type="number"
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
                className="w-32"
                min="2020"
                max="2030"
              />
            </div>

            {/* Journey Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Office Journey Filter</label>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant={!journeyFilter ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleJourneyFilter('all')}
                >
                  All Offices
                </Button>
                {JOURNEY_TYPES.map(journey => (
                  <Button
                    key={journey.value}
                    variant={journeyFilter === journey.value ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleJourneyFilter(journey.value)}
                    className={cn(
                      journeyFilter === journey.value && journey.color
                    )}
                  >
                    {journey.label}
                  </Button>
                ))}
              </div>
            </div>

            {/* Office Selection */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  Office Selection ({selectedOffices.length} selected)
                </label>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={handleSelectAllOffices}>
                    Select All
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleClearOffices}>
                    Clear All
                  </Button>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-h-48 overflow-y-auto border rounded-lg p-4">
                {offices.map(office => (
                  <div key={office.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={office.id}
                      checked={selectedOffices.includes(office.id)}
                      onCheckedChange={(checked) => handleOfficeSelection(office.id, checked as boolean)}
                    />
                    <label htmlFor={office.id} className="text-sm font-medium capitalize cursor-pointer">
                      {office.name}
                      {office.total_fte && (
                        <span className="text-xs text-muted-foreground ml-1">
                          ({office.total_fte} FTE)
                        </span>
                      )}
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Selection Summary */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span className="font-medium">Year:</span>
              <Badge variant="outline">{year}</Badge>
            </div>
            
            <div className="flex items-center gap-2">
              <Building2 className="h-4 w-4" />
              <span className="font-medium">Offices:</span>
              <Badge variant="outline">{selectedOffices.length} selected</Badge>
            </div>
            
            {totalSelectedFTE > 0 && (
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                <span className="font-medium">Total FTE:</span>
                <Badge variant="outline">{totalSelectedFTE.toLocaleString()}</Badge>
              </div>
            )}
            
            {journeyFilter && (
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                <span className="font-medium">Journey:</span>
                <Badge variant="outline" className="capitalize">{journeyFilter}</Badge>
              </div>
            )}
          </div>
          
          {selectedOfficeDetails.length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <div className="flex flex-wrap gap-2">
                <span className="text-xs font-medium text-muted-foreground">Selected offices:</span>
                {selectedOfficeDetails.map(office => (
                  <Badge key={office.id} variant="secondary" className="text-xs capitalize">
                    {office.name}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Aggregated Planning Grid */}
      {selectedOffices.length > 0 ? (
        <AggregatedPlanningGrid
          year={year}
          onYearChange={setYear}
          selectedOffices={selectedOffices}
          onOfficesChange={setSelectedOffices}
          journeyFilter={journeyFilter}
          onJourneyFilterChange={setJourneyFilter}
        />
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <Building2 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No Offices Selected</h3>
            <p className="text-muted-foreground mb-4">
              Please select one or more offices to view the aggregated business plan.
            </p>
            <Button onClick={handleSelectAllOffices}>
              Select All Offices
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};