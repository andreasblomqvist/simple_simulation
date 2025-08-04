/**
 * Wrapper component to integrate OfficeConfigPage with shadcn/ui theming
 */
import React, { useEffect } from 'react';
import { OfficeConfigPage } from './OfficeConfigPage';
import type { OfficeConfig } from '../../types/office';

interface OfficeConfigPageWrapperProps {
  office: OfficeConfig;
  onOfficeUpdate: (office: OfficeConfig) => void;
}

export const OfficeConfigPageWrapper: React.FC<OfficeConfigPageWrapperProps> = ({
  office,
  onOfficeUpdate
}) => {
  return (
    <div className="w-full">
      <OfficeConfigPage 
        office={office}
        onOfficeUpdate={onOfficeUpdate}
      />
    </div>
  );
};