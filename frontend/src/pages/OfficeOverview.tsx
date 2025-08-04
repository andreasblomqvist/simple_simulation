import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { OfficeView } from '../components/office/OfficeView';
import { Button } from '../components/ui/button';
import { ArrowLeft, Building2 } from 'lucide-react';
import type { OfficeConfig } from '../types/office';

export const OfficeOverview: React.FC = () => {
  const { officeId } = useParams<{ officeId: string }>();
  const navigate = useNavigate();
  const [offices, setOffices] = useState<OfficeConfig[]>([]);
  const [loading, setLoading] = useState(true);

  console.log('OfficeOverview component rendered with officeId:', officeId);

  useEffect(() => {
    const fetchOffices = async () => {
      try {
        const response = await fetch('/api/offices/config');
        if (response.ok) {
          const data = await response.json();
          setOffices(data);
        }
      } catch (error) {
        console.error('Failed to fetch offices:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOffices();
  }, []);

  const selectedOffice = offices.find(office => office.id === officeId);

  // If no office is selected, redirect to offices page
  if (!officeId) {
    navigate('/offices');
    return null;
  }

  // If an office is selected, show the office view
  if (!selectedOffice) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-6">
          <div className="text-center py-12">
            <div className="text-gray-500 mb-4">Office not found</div>
            <Button onClick={() => navigate('/office-overview')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Offices
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-6">
        {/* Back Button */}
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/office-overview')}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Offices
          </Button>
        </div>

        {/* Office View */}
        <OfficeView office={selectedOffice} />
      </div>
    </div>
  );
}; 