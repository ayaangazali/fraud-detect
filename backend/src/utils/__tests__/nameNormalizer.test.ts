// src/utils/__tests__/nameNormalizer.test.ts
import { normalizeName, parseAliases } from '../nameNormalizer';

describe('nameNormalizer', () => {
  describe('normalizeName', () => {
    test('should convert to lowercase', () => {
      expect(normalizeName('JOHN DOE')).toBe('john doe');
    });

    test('should remove punctuation', () => {
      expect(normalizeName('O\'Brien, John')).toBe('o brien john');
    });

    test('should collapse multiple spaces', () => {
      expect(normalizeName('John    Doe')).toBe('john doe');
    });

    test('should remove common titles', () => {
      expect(normalizeName('Mr. John Doe')).toBe('john doe');
      expect(normalizeName('Dr. Jane Smith')).toBe('jane smith');
    });

    test('should handle empty strings', () => {
      expect(normalizeName('')).toBe('');
    });

    test('should normalize complex names', () => {
      expect(normalizeName('Dr. O\'Brien-Smith, Jr.')).toBe('o brien smith jr');
    });
  });

  describe('parseAliases', () => {
    test('should parse comma-separated aliases', () => {
      const result = parseAliases('John Smith, Johnny Smith, J. Smith');
      expect(result).toEqual(['John Smith', 'Johnny Smith', 'J. Smith']);
    });

    test('should handle empty strings', () => {
      expect(parseAliases('')).toEqual([]);
      expect(parseAliases(undefined)).toEqual([]);
    });

    test('should trim whitespace', () => {
      const result = parseAliases('  John Smith  ,  Johnny  ');
      expect(result).toEqual(['John Smith', 'Johnny']);
    });
  });
});
