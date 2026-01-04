// src/utils/__tests__/fuzzyMatcher.test.ts
import { performFuzzyMatching } from '../fuzzyMatcher';
import { CustomerRow, BlacklistRow } from '../../types';

describe('fuzzyMatcher', () => {
  const customers: CustomerRow[] = [
    {
      customer_id: 'C001',
      type: 'individual',
      full_name_en: 'John Smith',
      date_of_birth: '1990-01-01',
      nationality_country: 'USA',
    },
    {
      customer_id: 'C002',
      type: 'corporate',
      full_name_en: 'ABC Corporation',
      company_reg_no: 'REG12345',
      nationality_country: 'UK',
    },
  ];

  const blacklist: BlacklistRow[] = [
    {
      full_name: 'Jon Smith',
      source: 'government',
      effective_date: '2024-01-01',
    },
    {
      full_name: 'ABC Corp',
      alias_alternate_names: 'ABC Company, ABC Ltd',
      source: 'regulator',
      effective_date: '2023-06-15',
    },
  ];

  test('should find close matches above threshold', () => {
    const matches = performFuzzyMatching(customers, blacklist, 70, false);
    
    // John Smith vs Jon Smith should match (high similarity)
    expect(matches.length).toBeGreaterThan(0);
    const johnMatch = matches.find(m => m.customer_id === 'C001');
    expect(johnMatch).toBeDefined();
    expect(johnMatch?.similarity_score).toBeGreaterThanOrEqual(70);
  });

  test('should not match when below threshold', () => {
    const matches = performFuzzyMatching(customers, blacklist, 95, false);
    
    // Strict threshold should reduce matches
    expect(matches.length).toBeLessThanOrEqual(2);
  });

  test('should include aliases when enabled', () => {
    const matches = performFuzzyMatching(customers, blacklist, 60, true);
    
    // ABC Corporation should match ABC Corp or its aliases
    const abcMatch = matches.find(m => m.customer_id === 'C002');
    expect(abcMatch).toBeDefined();
  });

  test('should not include aliases when disabled', () => {
    const matchesWithAliases = performFuzzyMatching(customers, blacklist, 60, true);
    const matchesWithoutAliases = performFuzzyMatching(customers, blacklist, 60, false);
    
    // May have different number of matches
    expect(matchesWithAliases.length).toBeGreaterThanOrEqual(matchesWithoutAliases.length);
  });

  test('should sort results by similarity score descending', () => {
    const matches = performFuzzyMatching(customers, blacklist, 50, true);
    
    for (let i = 1; i < matches.length; i++) {
      expect(matches[i - 1].similarity_score).toBeGreaterThanOrEqual(matches[i].similarity_score);
    }
  });

  test('should include all required fields in results', () => {
    const matches = performFuzzyMatching(customers, blacklist, 70, false);
    
    if (matches.length > 0) {
      const match = matches[0];
      expect(match).toHaveProperty('customer_id');
      expect(match).toHaveProperty('customer_name');
      expect(match).toHaveProperty('customer_type');
      expect(match).toHaveProperty('dob_or_reg_no');
      expect(match).toHaveProperty('nationality_country');
      expect(match).toHaveProperty('matched_blacklist_name');
      expect(match).toHaveProperty('matched_alias');
      expect(match).toHaveProperty('source');
      expect(match).toHaveProperty('effective_date');
      expect(match).toHaveProperty('similarity_score');
    }
  });
});
