// src/utils/nameNormalizer.ts

/**
 * Normalizes a name for fuzzy matching by:
 * - Converting to lowercase
 * - Trimming whitespace
 * - Removing punctuation
 * - Collapsing repeated spaces
 * - Removing common titles/stopwords
 */
export function normalizeName(name: string): string {
  if (!name) return '';

  let normalized = name.toLowerCase().trim();

  // Remove punctuation
  normalized = normalized.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, ' ');

  // Collapse multiple spaces
  normalized = normalized.replace(/\s+/g, ' ').trim();

  // Remove common titles and stopwords
  const stopwords = ['mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam', 'miss'];
  const words = normalized.split(' ');
  const filtered = words.filter(word => !stopwords.includes(word));

  return filtered.join(' ');
}

/**
 * Parse comma-separated aliases into an array
 */
export function parseAliases(aliasString?: string): string[] {
  if (!aliasString) return [];
  return aliasString
    .split(',')
    .map(alias => alias.trim())
    .filter(alias => alias.length > 0);
}
