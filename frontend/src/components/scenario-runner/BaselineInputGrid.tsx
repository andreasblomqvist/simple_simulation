import React, { useState } from 'react';
import { Tabs, Table, InputNumber, Typography, Alert } from 'antd';

const { TabPane } = Tabs;
const { Text } = Typography;

// Example roles and months (customize as needed)
const ROLES = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
const MONTHS = [
  '202501', '202502', '202503', '202504', '202505', '202506',
  '202507', '202508', '202509', '202510', '202511', '202512',
  '202601', '202602', '202603', '202604', '202605', '202606',
  '202607', '202608', '202609', '202610', '202611', '202612',
  '202701', '202702', '202703', '202704', '202705', '202706',
  '202707', '202708', '202709', '202710', '202711', '202712',
  '202801', '202802', '202803', '202804', '202805', '202806',
  '202807', '202808', '202809', '202810', '202811', '202812',
  '202901', '202902', '202903', '202904', '202905', '202906',
  '202907', '202908', '202909', '202910', '202911', '202912',
  '203001', '203002', '203003', '203004', '203005', '203006',
  '203007', '203008', '203009', '203010', '203011', '203012',
];

// Helper to initialize recruitment data with provided values
const recruitmentDefaults: Record<string, Record<string, number | undefined>> = {
  '202501': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202502': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202503': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202504': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202505': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202506': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202507': { A: 5, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202508': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202509': { A: 90, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202510': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202511': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202512': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, Pi: undefined, P: undefined },
  '202601': { A: 21, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202602': { A: 21, AC: 8, C: 3, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202603': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202604': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202605': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202606': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202607': { A: 5, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202608': { A: 21, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202609': { A: 93, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202610': { A: 21, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202611': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202612': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202701': { A: 22, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202702': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202703': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202704': { A: 15, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202705': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202706': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202707': { A: 5, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202708': { A: 22, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202709': { A: 96, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202710': { A: 22, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202711': { A: 22, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202712': { A: 24, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202801': { A: 23, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202802': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202803': { A: 8, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202804': { A: 15, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202805': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202806': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202807': { A: 8, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202808': { A: 23, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202809': { A: 39, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202810': { A: 23, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202811': { A: 15, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202812': { A: 8, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202901': { A: 24, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202902': { A: 8, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202903': { A: 8, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202904': { A: 15, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202905': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202906': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202907': { A: 5, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202908': { A: 24, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202909': { A: 102, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202910': { A: 24, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202911': { A: 15, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '202912': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203001': { A: 25, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203002': { A: 8, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203003': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203004': { A: 15, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203005': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203006': { A: 10, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203007': { A: 8, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203008': { A: 25, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203009': { A: 15, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203010': { A: 8, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203011': { A: 15, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
  '203012': { A: 8, AC: 8, C: 4, SrC: 1, AM: 0, M: 0, SrM: undefined, Pi: undefined, P: undefined },
};

// Helper to initialize recruitment data with provided values
const initRecruitmentData = () => {
  const data: Record<string, Record<string, number | undefined>> = {};
  MONTHS.forEach(month => {
    data[month] = {};
    ROLES.forEach(role => {
      data[month][role] = recruitmentDefaults[month]?.[role] ?? undefined;
    });
  });
  return data;
};

// Helper to initialize leavers data with provided values
const leaversDefaults: Record<string, Record<string, number | undefined>> = {
  '202501': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, Pi: 0, P: 0 },
  '202502': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202503': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, Pi: 1, P: 0 },
  '202504': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, Pi: 0, P: 0 },
  '202505': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, Pi: 0, P: 0 },
  '202506': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202507': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 0, Pi: 0, P: 0 },
  '202508': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202509': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 2, Pi: 0, P: 0 },
  '202510': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202511': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 1, Pi: 1, P: 0 },
  '202512': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202601': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202602': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202603': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202604': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202605': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202606': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202607': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 0, Pi: 0, P: 0 },
  '202608': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202609': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 2, Pi: 0, P: 0 },
  '202610': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202611': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 1, Pi: 1, P: 0 },
  '202612': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202701': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202702': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202703': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202704': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202705': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202706': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202707': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 0, Pi: 0, P: 0 },
  '202708': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202709': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 2, Pi: 0, P: 0 },
  '202710': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202711': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 1, Pi: 1, P: 0 },
  '202712': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202801': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202802': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202803': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202804': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202805': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202806': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202807': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 0, Pi: 0, P: 0 },
  '202808': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202809': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 2, Pi: 0, P: 0 },
  '202810': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202811': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 1, Pi: 1, P: 0 },
  '202812': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202901': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202902': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202903': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202904': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202905': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202906': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '202907': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 0, Pi: 0, P: 0 },
  '202908': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202909': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 2, Pi: 0, P: 0 },
  '202910': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '202911': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 1, Pi: 1, P: 0 },
  '202912': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '203001': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '203002': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '203003': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '203004': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '203005': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '203006': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
  '203007': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 0, Pi: 0, P: 0 },
  '203008': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '203009': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 2, Pi: 0, P: 0 },
  '203010': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 1, P: 0 },
  '203011': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 1, Pi: 1, P: 0 },
  '203012': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, Pi: 0, P: 0 },
};

const initLeaversData = () => {
  const data: Record<string, Record<string, number | undefined>> = {};
  MONTHS.forEach(month => {
    data[month] = {};
    ROLES.forEach(role => {
      data[month][role] = leaversDefaults[month]?.[role] ?? undefined;
    });
  });
  return data;
};

// Helper to calculate summary totals for a data grid
const getSummaryTotals = (data: Record<string, Record<string, number | undefined>>) => {
  const totals: Record<string, number> = {};
  ROLES.forEach(role => {
    totals[role] = 0;
  });
  MONTHS.forEach(month => {
    ROLES.forEach(role => {
      const val = data[month][role];
      totals[role] += typeof val === 'number' && !isNaN(val) ? val : 0;
    });
  });
  return totals;
};

// Helper to group data by year for expandable table
const getYearlyGroupedData = (data: Record<string, Record<string, number | undefined>>) => {
  const grouped: any[] = [];
  const years = Array.from(new Set(MONTHS.map(m => m.slice(0, 4))));
  years.forEach(year => {
    // Get all months for this year
    const months = MONTHS.filter(m => m.startsWith(year));
    // Calculate yearly totals
    const yearTotals: Record<string, number> = {};
    ROLES.forEach(role => {
      yearTotals[role] = months.reduce((sum, m) => sum + (typeof data[m][role] === 'number' && !isNaN(data[m][role]!) ? data[m][role]! : 0), 0);
    });
    // Build children (months)
    const children = months.map(month => ({
      key: `${year}-${month}`,
      isMonth: true,
      year,
      month: month.slice(4),
      ...data[month],
    }));
    // Parent row (year)
    grouped.push({
      key: year,
      isYear: true,
      year,
      month: '',
      ...yearTotals,
      children,
    });
  });
  return grouped;
};

export default function BaselineInputGrid(props) {
  const [activeTab, setActiveTab] = useState<'recruitment' | 'leavers'>('recruitment');
  const [recruitmentData, setRecruitmentData] = useState(initRecruitmentData());
  const [leaversData, setLeaversData] = useState(initLeaversData());
  const [validationError, setValidationError] = useState<string | null>(null);

  // Columns for expandable table
  const columns = [
    {
      title: 'Year/Month',
      dataIndex: 'isYear',
      key: 'year',
      width: 110,
      render: (_: any, record: any) =>
        record.isYear ? (
          <Text strong>{record.year}</Text>
        ) : (
          <span style={{ paddingLeft: 24 }}>{record.month}</span>
        ),
    },
    ...ROLES.map(role => ({
      title: role,
      dataIndex: role,
      key: role,
      width: 80,
      render: (value: number | undefined, record: any) =>
        record.isYear ? (
          <Text strong>{value ?? 0}</Text>
        ) : (
          <InputNumber
            min={0}
            value={value ?? 0}
            onChange={val => handleCellChange(`${record.year}${record.month}`, role, val)}
            style={{ width: '100%' }}
          />
        ),
    })),
  ];

  // Handle cell edit
  const handleCellChange = (month: string, role: string, value: number | null) => {
    if (activeTab === 'recruitment') {
      setRecruitmentData(prev => ({
        ...prev,
        [month]: { ...prev[month], [role]: value === null ? undefined : value }
      }));
    } else {
      setLeaversData(prev => ({
        ...prev,
        [month]: { ...prev[month], [role]: value === null ? undefined : value }
      }));
    }
    // Validation: no negatives
    if (value !== null && value !== undefined && value < 0) {
      setValidationError('Negative numbers are not allowed.');
    } else {
      setValidationError(null);
    }
  };

  return (
    <div style={{ marginLeft: 24, marginRight: 24 }}>
      <Tabs
        activeKey={activeTab}
        onChange={key => setActiveTab(key as 'recruitment' | 'leavers')}
        style={{ marginBottom: 16 }}
      >
        <TabPane tab="Recruitment (Starters)" key="recruitment">
          <Table
            columns={columns}
            dataSource={getYearlyGroupedData(recruitmentData)}
            pagination={false}
            bordered
            size="small"
            scroll={{ x: 'max-content', y: 400 }}
            rowKey="key"
            expandable={{
              defaultExpandAllRows: true,
              expandRowByClick: true,
              rowExpandable: record => record.isYear,
            }}
          />
        </TabPane>
        <TabPane tab="Leavers (Churn)" key="leavers">
          <Table
            columns={columns}
            dataSource={getYearlyGroupedData(leaversData)}
            pagination={false}
            bordered
            size="small"
            scroll={{ x: 'max-content', y: 400 }}
            rowKey="key"
            expandable={{
              defaultExpandAllRows: true,
              expandRowByClick: true,
              rowExpandable: record => record.isYear,
            }}
          />
        </TabPane>
      </Tabs>
      {validationError && (
        <Alert message={validationError} type="error" showIcon style={{ marginTop: 16 }} />
      )}
    </div>
  );
} 