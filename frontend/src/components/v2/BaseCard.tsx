import React from 'react';
import { Card } from 'antd';
import type { CardProps } from 'antd';

interface BaseCardProps extends CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'small' | 'medium' | 'large';
  elevation?: 'low' | 'medium' | 'high';
  interactive?: boolean;
}

const BaseCard: React.FC<BaseCardProps> = ({
  children,
  className = '',
  padding = 'medium',
  elevation = 'low',
  interactive = false,
  ...cardProps
}) => {
  const paddingMap = {
    small: '16px',
    medium: '24px',
    large: '32px'
  };

  const elevationMap = {
    low: '0 2px 8px rgba(0, 0, 0, 0.06)',
    medium: '0 4px 16px rgba(0, 0, 0, 0.08)',
    high: '0 8px 24px rgba(0, 0, 0, 0.12)'
  };

  const baseStyle = {
    borderRadius: '8px',
    border: '1px solid #f0f0f0',
    padding: paddingMap[padding],
    boxShadow: elevationMap[elevation],
    transition: 'all 0.3s ease',
    ...cardProps.style
  };

  const hoverStyle = interactive ? {
    cursor: 'pointer',
    ':hover': {
      boxShadow: elevationMap.high,
      transform: 'translateY(-2px)'
    }
  } : {};

  return (
    <Card
      {...cardProps}
      className={`base-card ${interactive ? 'interactive' : ''} ${className}`}
      style={{ ...baseStyle, ...hoverStyle }}
      hoverable={interactive}
    >
      {children}
    </Card>
  );
};

export default BaseCard; 