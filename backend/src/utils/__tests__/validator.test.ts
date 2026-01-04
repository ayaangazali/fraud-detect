// src/utils/__tests__/validator.test.ts
import { validateCustomers, validateBlacklist } from '../validator';

describe('validator', () => {
  describe('validateCustomers', () => {
    test('should validate correct customer data', () => {
      const data = [
        {
          customer_id: 'C001',
          type: 'individual',
          full_name_en: 'John Doe',
          date_of_birth: '1990-01-01',
          nationality_country: 'USA',
        },
      ];

      const { rows, errors } = validateCustomers(data);
      expect(rows).toHaveLength(1);
      expect(errors).toHaveLength(0);
    });

    test('should flag missing customer_id', () => {
      const data = [
        {
          customer_id: '',
          type: 'individual',
          full_name_en: 'John Doe',
          date_of_birth: '1990-01-01',
          nationality_country: 'USA',
        },
      ];

      const { rows, errors } = validateCustomers(data);
      expect(errors).toHaveLength(1);
      expect(errors[0].field).toBe('customer_id');
    });

    test('should require date_of_birth for individuals', () => {
      const data = [
        {
          customer_id: 'C001',
          type: 'individual',
          full_name_en: 'John Doe',
          nationality_country: 'USA',
        },
      ];

      const { rows, errors } = validateCustomers(data);
      expect(errors.some(e => e.field === 'date_of_birth')).toBe(true);
    });

    test('should require company_reg_no for corporates', () => {
      const data = [
        {
          customer_id: 'C001',
          type: 'corporate',
          full_name_en: 'ABC Corp',
          nationality_country: 'USA',
        },
      ];

      const { rows, errors } = validateCustomers(data);
      expect(errors.some(e => e.field === 'company_reg_no')).toBe(true);
    });

    test('should validate invalid type', () => {
      const data = [
        {
          customer_id: 'C001',
          type: 'invalid',
          full_name_en: 'John Doe',
          nationality_country: 'USA',
        },
      ];

      const { rows, errors } = validateCustomers(data);
      expect(errors.some(e => e.field === 'type')).toBe(true);
    });
  });

  describe('validateBlacklist', () => {
    test('should validate correct blacklist data', () => {
      const data = [
        {
          full_name: 'Bad Actor',
          source: 'government',
          effective_date: '2024-01-01',
        },
      ];

      const { rows, errors } = validateBlacklist(data);
      expect(rows).toHaveLength(1);
      expect(errors).toHaveLength(0);
    });

    test('should flag missing full_name', () => {
      const data = [
        {
          full_name: '',
          source: 'government',
          effective_date: '2024-01-01',
        },
      ];

      const { rows, errors } = validateBlacklist(data);
      expect(errors.some(e => e.field === 'full_name')).toBe(true);
    });

    test('should validate source field', () => {
      const data = [
        {
          full_name: 'Bad Actor',
          source: 'invalid',
          effective_date: '2024-01-01',
        },
      ];

      const { rows, errors } = validateBlacklist(data);
      expect(errors.some(e => e.field === 'source')).toBe(true);
    });

    test('should accept optional aliases', () => {
      const data = [
        {
          full_name: 'Bad Actor',
          alias_alternate_names: 'Evil Person, Villain',
          source: 'regulator',
          effective_date: '2024-01-01',
        },
      ];

      const { rows, errors } = validateBlacklist(data);
      expect(rows[0].alias_alternate_names).toBe('Evil Person, Villain');
      expect(errors).toHaveLength(0);
    });
  });
});
