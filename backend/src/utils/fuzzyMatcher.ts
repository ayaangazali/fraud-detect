// src/utils/fuzzyMatcher.ts
import Fuse from 'fuse.js';
import { normalizeName, parseAliases } from './nameNormalizer';
import { CustomerRow, BlacklistRow, MatchResult } from '../types';

interface BlacklistEntry {
  originalName: string;
  normalizedName: string;
  matchedAlias: string | null;
  source: string;
  effectiveDate: string;
  blacklistType: 'regulator' | 'user';
}

/**
 * Performs fuzzy matching between customers and blacklist entries
 */
export function performFuzzyMatching(
  customers: CustomerRow[],
  blacklist: BlacklistRow[],
  threshold: number,
  includeAliases: boolean
): MatchResult[] {
  const matches: MatchResult[] = [];

  // Build searchable blacklist entries
  const blacklistEntries: BlacklistEntry[] = [];

  for (const entry of blacklist) {
    // Add main name
    blacklistEntries.push({
      originalName: entry.full_name,
      normalizedName: normalizeName(entry.full_name),
      matchedAlias: null,
      source: entry.source,
      effectiveDate: entry.effective_date,
      blacklistType: entry.blacklist_type || 'user', // Default to 'user' if not specified
    });

    // Add aliases if enabled
    if (includeAliases && entry.alias_alternate_names) {
      const aliases = parseAliases(entry.alias_alternate_names);
      for (const alias of aliases) {
        blacklistEntries.push({
          originalName: entry.full_name,
          normalizedName: normalizeName(alias),
          matchedAlias: alias,
          source: entry.source,
          effectiveDate: entry.effective_date,
          blacklistType: entry.blacklist_type || 'user',
        });
      }
    }
  }

  // Configure Fuse.js for fuzzy matching
  const fuse = new Fuse(blacklistEntries, {
    keys: ['normalizedName'],
    includeScore: true,
    threshold: 1 - threshold / 100, // Fuse uses 0 (perfect) to 1 (worst)
    ignoreLocation: true,
    minMatchCharLength: 2,
  });

  // Match each customer against blacklist
  for (const customer of customers) {
    const normalizedCustomerName = normalizeName(customer.full_name_en);
    
    if (!normalizedCustomerName) continue;

    const results = fuse.search(normalizedCustomerName);

    for (const result of results) {
      if (result.score === undefined) continue;

      // Convert Fuse score (0=perfect, 1=worst) to similarity (0-100)
      const similarityScore = Math.round((1 - result.score) * 100);

      if (similarityScore >= threshold) {
        const entry = result.item;
        
        // Determine match type and reason
        const isAlias = entry.matchedAlias !== null;
        const isDirect = similarityScore >= 95;
        const matchType: 'direct' | 'alias' | 'fuzzy' = isDirect ? 'direct' : (isAlias ? 'alias' : 'fuzzy');
        
        let matchReason = '';
        if (isDirect && !isAlias) {
          matchReason = 'Direct name match - Names are virtually identical';
        } else if (isAlias) {
          matchReason = `Matched via alias "${entry.matchedAlias}" with ${similarityScore}% similarity`;
        } else {
          matchReason = `Fuzzy match detected - ${similarityScore}% similarity in name patterns`;
        }
        
        const matchedField = isAlias ? `alias: ${entry.matchedAlias}` : 'full_name';
        
        matches.push({
          customer_id: customer.customer_id,
          customer_name: customer.full_name_en,
          customer_type: customer.type,
          dob_or_reg_no:
            customer.type === 'individual'
              ? customer.date_of_birth || ''
              : customer.company_reg_no || '',
          nationality_country: customer.nationality_country,
          matched_blacklist_name: entry.originalName,
          matched_alias: entry.matchedAlias,
          source: entry.source,
          effective_date: entry.effectiveDate,
          similarity_score: similarityScore,
          blacklist_type: entry.blacklistType,
          match_type: matchType,
          match_reason: matchReason,
          matched_field: matchedField,
          score_breakdown: {
            name_similarity: isAlias ? 0 : similarityScore,
            alias_similarity: isAlias ? similarityScore : 0,
            best_match: isAlias ? (entry.matchedAlias || entry.originalName) : entry.originalName,
          },
        });
      }
    }
  }

  // Sort by similarity score descending
  matches.sort((a, b) => b.similarity_score - a.similarity_score);

  return matches;
}
