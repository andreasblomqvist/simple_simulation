/**
 * Main office management page with office selection and configuration.
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Select, Row, Col, Spin, Alert } from 'antd';
import { OfficeConfigPage } from '../components/office-config/OfficeConfigPage';
import { useOfficeStore } from '../stores/officeStore';
import { ErrorBoundary } from '../components/ui/ErrorBoundary';

const { Title } = Typography;
const { Option } = Select;

interface OfficeManagementProps {
  className?: string;
}

export const OfficeManagement: React.FC<OfficeManagementProps> = ({ className }) => {
  const { officeId } = useParams<{ officeId: string }>();
  const navigate = useNavigate();
  
  const {
    offices,
    currentOffice,
    loading,
    error,
    loadOffices,
    selectOffice,
    officesByJourney
  } = useOfficeStore();


  // Load offices on mount
  useEffect(() => {
    loadOffices();
  }, [loadOffices]);

  // Handle office selection from URL
  useEffect(() => {
    if (officeId && offices.length > 0) {
      const office = offices.find(o => o.id === officeId);
      if (office && currentOffice?.id !== officeId) {
        selectOffice(officeId);
      } else if (!office) {
        // Office not found, redirect to first available office
        if (offices.length > 0) {
          navigate(`/offices/${offices[0].id}`);
        }
      }
    }
  }, [officeId, offices, currentOffice, selectOffice, navigate]);

  const handleOfficeSelect = (selectedOfficeId: string) => {
    navigate(`/offices/${selectedOfficeId}`);
  };

  if (loading && offices.length === 0) {
    return (
      <Card>
        <Spin size="large" />
        <div style={{ textAlign: 'center', marginTop: 16 }}>Loading offices...</div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <Alert 
          message="Error Loading Offices" 
          description={error}
          type="error" 
          showIcon 
          action={
            <button onClick={loadOffices} style={{ border: 'none', background: 'none', color: '#1890ff', cursor: 'pointer' }}>
              Retry
            </button>
          }
        />
      </Card>
    );
  }

  if (offices.length === 0) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Title level={3}>No Offices Found</Title>
          <p>No offices are currently configured in the system.</p>
        </div>
      </Card>
    );
  }

  return (
    <ErrorBoundary>
      <Card 
        title={
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Title level={4} style={{ margin: 0 }}>Office Management</Title>
            {offices.length > 0 && (
              <Select
                style={{ width: 200 }}
                placeholder="Select an office"
                value={currentOffice?.id}
                onChange={handleOfficeSelect}
                showSearch
                optionFilterProp="children"
              >
                {offices.map(office => (
                  <Option key={office.id} value={office.id}>
                    {office.name} ({office.journey})
                  </Option>
                ))}
              </Select>
            )}
          </div>
        }
      >
        {currentOffice ? (
          <OfficeConfigPage office={currentOffice} />
        ) : (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Title level={3}>Select an Office</Title>
            <p>Choose an office from the dropdown above to view and manage its configuration.</p>
          </div>
        )}
      </Card>
    </ErrorBoundary>
  );
};

export default OfficeManagement;