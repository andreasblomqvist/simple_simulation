import React from 'react';
import { Collapse } from 'antd';
import type { CollapseProps } from 'antd';

interface CollapsibleSectionProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  className?: string;
  extra?: React.ReactNode;
  disabled?: boolean;
  forceRender?: boolean;
  key?: string;
}

/**
 * Standalone CollapsibleSection Component
 * Uses modern Ant Design Collapse with items pattern
 */
const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  children,
  defaultOpen = false,
  className = '',
  extra,
  disabled = false,
  forceRender = false,
  key = 'default'
}) => {
  const items: CollapseProps['items'] = [
    {
      key: key,
      label: title,
      children: (
        <div className="section-content" style={{ padding: '0' }}>
          {children}
        </div>
      ),
      extra,
      forceRender,
      style: {
        marginBottom: '16px',
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        border: '1px solid #f0f0f0',
      }
    }
  ];

  return (
    <Collapse
      items={items}
      defaultActiveKey={defaultOpen ? [key] : []}
      className={`collapsible-section ${className} ${disabled ? 'disabled' : ''}`}
      ghost={false}
      size="small"
      style={{
        backgroundColor: 'transparent',
        border: 'none',
        opacity: disabled ? 0.6 : 1,
        pointerEvents: disabled ? 'none' : 'auto',
      }}
    />
  );
};

export { CollapsibleSection };
export default CollapsibleSection; 