import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { OfficeViewWithTabs } from '../components/office/OfficeViewWithTabs';
import { Button } from '../components/ui/button';
import { ArrowLeft, Building2 } from 'lucide-react';
import { useOfficeStore } from '../stores/officeStore';
import type { OfficeConfig } from '../types/office';

export const OfficeOverview: React.FC = () => {
  const { officeId } = useParams<{ officeId: string }>();
  const navigate = useNavigate();
  
  const {
    offices,
    loading,
    error,
    loadOffices
  } = useOfficeStore();

  console.log('OfficeOverview component rendered with officeId:', officeId, 'loading:', loading, 'offices.length:', offices.length);

  useEffect(() => {
    console.log('OfficeOverview: calling loadOffices');
    loadOffices();
  }, []); // Remove loadOffices from dependency array to prevent infinite loop

  // If no office is selected, redirect to offices page
  useEffect(() => {
    if (!officeId) {
      navigate('/offices');
    }
  }, [officeId, navigate]);

  const selectedOffice = useMemo(() => 
    offices.find(office => office.id === officeId), 
    [offices, officeId]
  );

  // Memoized callback to prevent unnecessary re-renders
  const handleEdit = useCallback(() => {
    if (selectedOffice) {
      navigate(`/offices/${selectedOffice.id}`);
    }
  }, [selectedOffice, navigate]);

  // Return early if no officeId (but don't render anything while redirect is happening)
  if (!officeId) {
    return null;
  }

  // Handle loading state
  if (loading) {
    return (
      <div style={{ backgroundColor: '#111827', minHeight: '100vh' }}>
        <div className="container mx-auto py-6">
          <div className="text-center py-12">
            <Building2 className="h-12 w-12 mx-auto mb-4 animate-pulse" style={{ color: '#9ca3af' }} />
            <div className="text-lg font-medium mb-4" style={{ color: '#f3f4f6' }}>
              Loading office data...
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Handle error state
  if (error) {
    return (
      <div style={{ backgroundColor: '#111827', minHeight: '100vh' }}>
        <div className="container mx-auto py-6">
          <div className="text-center py-12">
            <Building2 className="h-12 w-12 mx-auto mb-4" style={{ color: '#ef4444' }} />
            <div className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>
              Error loading offices
            </div>
            <div className="text-sm mb-4" style={{ color: '#9ca3af' }}>
              {error}
            </div>
            <Button 
              onClick={() => navigate('/offices')}
              style={{
                height: '36px',
                padding: '0 1rem',
                fontWeight: '500',
                border: '1px solid #374151',
                backgroundColor: '#1f2937',
                color: '#f3f4f6'
              }}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Offices
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Handle office not found
  if (!selectedOffice) {
    return (
      <div style={{ backgroundColor: '#111827', minHeight: '100vh' }}>
        <div className="container mx-auto py-6">
          <div className="text-center py-12">
            <Building2 className="h-12 w-12 mx-auto mb-4" style={{ color: '#9ca3af' }} />
            <div className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>
              Office not found
            </div>
            <div className="text-sm mb-4" style={{ color: '#9ca3af' }}>
              The office "{officeId}" could not be found.
            </div>
            <Button 
              onClick={() => navigate('/offices')}
              style={{
                height: '36px',
                padding: '0 1rem',
                fontWeight: '500',
                border: '1px solid #374151',
                backgroundColor: '#1f2937',
                color: '#f3f4f6'
              }}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Offices
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: '#111827', minHeight: '100vh' }}>
      {/* Back Button */}
      <div className="p-4">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => navigate('/offices')}
          style={{
            height: '36px',
            padding: '0 1rem',
            fontWeight: '500',
            border: '1px solid #374151',
            backgroundColor: '#1f2937',
            color: '#f3f4f6',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#374151';
            e.currentTarget.style.borderColor = '#4b5563';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#1f2937';
            e.currentTarget.style.borderColor = '#374151';
          }}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Offices
        </Button>
      </div>

      {/* Office View with Tabs */}
      <OfficeViewWithTabs 
        office={selectedOffice} 
        onEdit={handleEdit}
      />
    </div>
  );
}; 