/**
 * Integration tests for Office API endpoints
 * Tests real API interactions with backend services
 */
import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';

// API base URL - adjust based on your backend configuration
const API_BASE = 'http://localhost:8000';

// Test data
const testOfficeData = {
  name: 'Test Office Integration',
  journey: 'emerging',
  timezone: 'UTC',
  economic_parameters: {
    cost_of_living: 1.0,
    market_multiplier: 1.0,
    tax_rate: 0.25,
  },
  total_fte: 50,
  roles: {
    Consultant: {
      A: { fte: 10 },
      AC: { fte: 15 },
      C: { fte: 25 },
    },
  },
};

describe('Office API Integration Tests', () => {
  let createdOfficeId: string | null = null;

  beforeAll(async () => {
    // Verify backend is running
    try {
      const response = await fetch(`${API_BASE}/health`);
      if (!response.ok) {
        throw new Error('Backend not accessible');
      }
    } catch (error) {
      console.warn('Backend not running - integration tests will be skipped');
      return;
    }
  });

  afterAll(async () => {
    // Cleanup: Delete any created test data
    if (createdOfficeId) {
      try {
        await fetch(`${API_BASE}/offices/${createdOfficeId}`, {
          method: 'DELETE',
        });
      } catch (error) {
        console.warn('Failed to cleanup test office:', error);
      }
    }
  });

  describe('GET /offices', () => {
    it('should return list of offices', async () => {
      const response = await fetch(`${API_BASE}/offices`);
      
      expect(response.status).toBe(200);
      expect(response.headers.get('content-type')).toContain('application/json');
      
      const offices = await response.json();
      expect(Array.isArray(offices)).toBe(true);
      
      if (offices.length > 0) {
        const office = offices[0];
        expect(office).toHaveProperty('id');
        expect(office).toHaveProperty('name');
        expect(office).toHaveProperty('journey');
        expect(office).toHaveProperty('timezone');
        expect(office).toHaveProperty('economic_parameters');
        expect(office).toHaveProperty('total_fte');
        expect(office).toHaveProperty('roles');
        
        // Validate economic parameters structure
        expect(office.economic_parameters).toHaveProperty('cost_of_living');
        expect(office.economic_parameters).toHaveProperty('market_multiplier');
        expect(office.economic_parameters).toHaveProperty('tax_rate');
        
        // Validate that values are numbers
        expect(typeof office.total_fte).toBe('number');
        expect(typeof office.economic_parameters.cost_of_living).toBe('number');
        expect(typeof office.economic_parameters.market_multiplier).toBe('number');
        expect(typeof office.economic_parameters.tax_rate).toBe('number');
      }
    });

    it('should return offices with specific known offices', async () => {
      const response = await fetch(`${API_BASE}/offices`);
      const offices = await response.json();
      
      // Check for known offices from configuration
      const officeNames = offices.map((office: any) => office.name);
      expect(officeNames).toContain('Stockholm');
      expect(officeNames).toContain('Munich');
      
      // Find Stockholm office and validate structure
      const stockholm = offices.find((office: any) => office.name === 'Stockholm');
      expect(stockholm).toBeDefined();
      expect(stockholm.id).toBe('Stockholm');
      expect(stockholm.journey).toBe('mature');
      expect(stockholm.total_fte).toBeGreaterThan(0);
    });

    it('should handle CORS headers correctly', async () => {
      const response = await fetch(`${API_BASE}/offices`);
      
      // Check CORS headers are present
      const corsOrigin = response.headers.get('access-control-allow-origin');
      expect(corsOrigin).toBeTruthy();
    });
  });

  describe('GET /offices/{office_id}', () => {
    it('should return specific office details', async () => {
      const response = await fetch(`${API_BASE}/offices/Stockholm`);
      
      expect(response.status).toBe(200);
      
      const office = await response.json();
      expect(office.id).toBe('Stockholm');
      expect(office.name).toBe('Stockholm');
      expect(office.journey).toBe('mature');
      expect(office.roles).toHaveProperty('Consultant');
      
      // Validate roles structure
      const consultant = office.roles.Consultant;
      expect(consultant).toHaveProperty('A');
      expect(consultant).toHaveProperty('AC');
      expect(consultant.A).toHaveProperty('fte');
      expect(typeof consultant.A.fte).toBe('number');
    });

    it('should return 404 for non-existent office', async () => {
      const response = await fetch(`${API_BASE}/offices/NonExistentOffice`);
      
      expect(response.status).toBe(404);
    });

    it('should return Munich office with correct structure', async () => {
      const response = await fetch(`${API_BASE}/offices/Munich`);
      
      expect(response.status).toBe(200);
      
      const office = await response.json();
      expect(office.id).toBe('Munich');
      expect(office.name).toBe('Munich');
      expect(office.journey).toBe('established');
      expect(office.total_fte).toBeGreaterThan(0);
      
      // Check economic parameters
      expect(office.economic_parameters.cost_of_living).toBeGreaterThan(0);
      expect(office.economic_parameters.market_multiplier).toBeGreaterThan(0);
      expect(office.economic_parameters.tax_rate).toBeGreaterThan(0);
    });
  });

  describe('POST /offices', () => {
    it('should create a new office successfully', async () => {
      const response = await fetch(`${API_BASE}/offices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testOfficeData),
      });
      
      expect(response.status).toBe(201);
      
      const createdOffice = await response.json();
      createdOfficeId = createdOffice.id;
      
      expect(createdOffice).toHaveProperty('id');
      expect(createdOffice.name).toBe(testOfficeData.name);
      expect(createdOffice.journey).toBe(testOfficeData.journey);
      expect(createdOffice.timezone).toBe(testOfficeData.timezone);
      expect(createdOffice.total_fte).toBe(testOfficeData.total_fte);
      
      // Verify economic parameters
      expect(createdOffice.economic_parameters).toEqual(testOfficeData.economic_parameters);
      
      // Verify roles structure
      expect(createdOffice.roles).toEqual(testOfficeData.roles);
    });

    it('should reject invalid office data', async () => {
      const invalidData = {
        // Missing required fields
        name: '',
        journey: 'invalid_journey',
      };
      
      const response = await fetch(`${API_BASE}/offices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(invalidData),
      });
      
      expect(response.status).toBe(422);
      
      const error = await response.json();
      expect(error).toHaveProperty('detail');
    });

    it('should validate economic parameters ranges', async () => {
      const invalidEconomicData = {
        ...testOfficeData,
        name: 'Invalid Economic Test',
        economic_parameters: {
          cost_of_living: -1, // Invalid negative value
          market_multiplier: 0, // Invalid zero value
          tax_rate: 1.5, // Invalid > 100% tax rate
        },
      };
      
      const response = await fetch(`${API_BASE}/offices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(invalidEconomicData),
      });
      
      // Should either reject or normalize values
      expect([400, 422, 201]).toContain(response.status);
      
      if (response.status === 201) {
        const created = await response.json();
        // Values should be normalized
        expect(created.economic_parameters.cost_of_living).toBeGreaterThanOrEqual(0);
        expect(created.economic_parameters.market_multiplier).toBeGreaterThan(0);
        expect(created.economic_parameters.tax_rate).toBeLessThanOrEqual(1);
        
        // Cleanup
        await fetch(`${API_BASE}/offices/${created.id}`, { method: 'DELETE' });
      }
    });
  });

  describe('PUT /offices/{office_id}', () => {
    beforeEach(async () => {
      // Create a test office for update tests
      if (!createdOfficeId) {
        const response = await fetch(`${API_BASE}/offices`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(testOfficeData),
        });
        const created = await response.json();
        createdOfficeId = created.id;
      }
    });

    it('should update existing office', async () => {
      const updatedData = {
        ...testOfficeData,
        id: createdOfficeId,
        name: 'Updated Test Office',
        total_fte: 75,
        economic_parameters: {
          cost_of_living: 1.2,
          market_multiplier: 1.1,
          tax_rate: 0.28,
        },
      };
      
      const response = await fetch(`${API_BASE}/offices/${createdOfficeId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
      });
      
      expect(response.status).toBe(200);
      
      const updated = await response.json();
      expect(updated.name).toBe('Updated Test Office');
      expect(updated.total_fte).toBe(75);
      expect(updated.economic_parameters.cost_of_living).toBe(1.2);
    });

    it('should return 404 for non-existent office update', async () => {
      const response = await fetch(`${API_BASE}/offices/NonExistentOffice`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ...testOfficeData, id: 'NonExistentOffice' }),
      });
      
      expect(response.status).toBe(404);
    });
  });

  describe('DELETE /offices/{office_id}', () => {
    it('should delete existing office', async () => {
      // Create a test office specifically for deletion
      const createResponse = await fetch(`${API_BASE}/offices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...testOfficeData,
          name: 'Office To Delete',
        }),
      });
      
      const created = await createResponse.json();
      const officeIdToDelete = created.id;
      
      // Delete the office
      const deleteResponse = await fetch(`${API_BASE}/offices/${officeIdToDelete}`, {
        method: 'DELETE',
      });
      
      expect(deleteResponse.status).toBe(204);
      
      // Verify it's deleted by trying to fetch it
      const fetchResponse = await fetch(`${API_BASE}/offices/${officeIdToDelete}`);
      expect(fetchResponse.status).toBe(404);
    });

    it('should return 404 for non-existent office deletion', async () => {
      const response = await fetch(`${API_BASE}/offices/NonExistentOffice`, {
        method: 'DELETE',
      });
      
      expect(response.status).toBe(404);
    });
  });

  describe('Office Business Plans API', () => {
    it('should get business plans for office', async () => {
      const response = await fetch(`${API_BASE}/offices/Stockholm/business-plans`);
      
      // Should return either empty array or business plans
      expect([200, 404]).toContain(response.status);
      
      if (response.status === 200) {
        const plans = await response.json();
        expect(Array.isArray(plans)).toBe(true);
        
        if (plans.length > 0) {
          const plan = plans[0];
          expect(plan).toHaveProperty('id');
          expect(plan).toHaveProperty('office_id');
          expect(plan).toHaveProperty('year');
          expect(plan).toHaveProperty('month');
          expect(plan.office_id).toBe('Stockholm');
        }
      }
    });

    it('should get workforce distribution for office', async () => {
      const response = await fetch(`${API_BASE}/offices/Stockholm/workforce-distribution`);
      
      // Should return either workforce data or 404
      expect([200, 404]).toContain(response.status);
      
      if (response.status === 200) {
        const workforce = await response.json();
        expect(workforce).toHaveProperty('office_id');
        expect(workforce).toHaveProperty('workforce');
        expect(workforce.office_id).toBe('Stockholm');
        expect(Array.isArray(workforce.workforce)).toBe(true);
        
        if (workforce.workforce.length > 0) {
          const entry = workforce.workforce[0];
          expect(entry).toHaveProperty('role');
          expect(entry).toHaveProperty('level');
          expect(entry).toHaveProperty('fte');
          expect(typeof entry.fte).toBe('number');
        }
      }
    });

    it('should get office summary with combined data', async () => {
      const response = await fetch(`${API_BASE}/offices/Stockholm/summary`);
      
      expect([200, 404]).toContain(response.status);
      
      if (response.status === 200) {
        const summary = await response.json();
        expect(summary).toHaveProperty('office_id');
        expect(summary.office_id).toBe('Stockholm');
        expect(summary).toHaveProperty('monthly_plans');
        expect(Array.isArray(summary.monthly_plans)).toBe(true);
        
        // Workforce distribution might be optional
        if (summary.workforce_distribution) {
          expect(summary.workforce_distribution).toHaveProperty('office_id');
          expect(summary.workforce_distribution).toHaveProperty('workforce');
        }
      }
    });
  });

  describe('Performance and Reliability', () => {
    it('should respond to office list within reasonable time', async () => {
      const start = Date.now();
      const response = await fetch(`${API_BASE}/offices`);
      const duration = Date.now() - start;
      
      expect(response.status).toBe(200);
      expect(duration).toBeLessThan(5000); // Should respond within 5 seconds
    });

    it('should handle concurrent requests correctly', async () => {
      const requests = Array(10).fill(null).map(() => 
        fetch(`${API_BASE}/offices/Stockholm`)
      );
      
      const responses = await Promise.all(requests);
      
      // All requests should succeed
      responses.forEach(response => {
        expect(response.status).toBe(200);
      });
      
      // All responses should have same data
      const data = await Promise.all(responses.map(r => r.json()));
      data.forEach(office => {
        expect(office.id).toBe('Stockholm');
        expect(office.name).toBe('Stockholm');
      });
    });

    it('should handle large office configurations', async () => {
      const largeOfficeData = {
        ...testOfficeData,
        name: 'Large Test Office',
        total_fte: 1000,
        roles: {
          Consultant: Object.fromEntries(
            Array(20).fill(null).map((_, i) => [
              `Level${i}`,
              { fte: 50, price: 1000 + i * 100, salary: 40000 + i * 5000 }
            ])
          )
        }
      };
      
      const response = await fetch(`${API_BASE}/offices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(largeOfficeData),
      });
      
      expect([201, 413]).toContain(response.status); // 413 = Payload Too Large
      
      if (response.status === 201) {
        const created = await response.json();
        expect(created.total_fte).toBe(1000);
        
        // Cleanup
        await fetch(`${API_BASE}/offices/${created.id}`, { method: 'DELETE' });
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle malformed JSON requests', async () => {
      const response = await fetch(`${API_BASE}/offices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: 'invalid json{',
      });
      
      expect(response.status).toBe(422);
    });

    it('should handle missing content-type header', async () => {
      const response = await fetch(`${API_BASE}/offices`, {
        method: 'POST',
        body: JSON.stringify(testOfficeData),
      });
      
      // Should either work or return 415 Unsupported Media Type
      expect([201, 415, 422]).toContain(response.status);
    });

    it('should provide helpful error messages', async () => {
      const response = await fetch(`${API_BASE}/offices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          // Missing required fields
          name: '',
        }),
      });
      
      expect(response.status).toBe(422);
      
      const error = await response.json();
      expect(error).toHaveProperty('detail');
      
      // Error should be descriptive
      const detail = Array.isArray(error.detail) ? error.detail : [error.detail];
      expect(detail.some((d: any) => 
        typeof d === 'string' ? d.includes('name') : d.msg?.includes('name')
      )).toBe(true);
    });
  });
});