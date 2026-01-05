// src/services/screeningServiceV2.ts
import Fuse from 'fuse.js';
import { KamcoClient, ScreeningEntry, ExtendedMatchResult } from '../types';
import { readKamcoClients } from '../utils/csvHandler';

/**
 * NEW SCREENING LOGIC: Compare uploaded screening list (3rd Excel) against KAMCO clients (1st Excel)
 * Find if anyone in the screening list is already in KAMCO database
 */

interface FuzeMatchResult {
  item: KamcoClient;
  score?: number;
  matches?: readonly any[];
}

export class ScreeningServiceV2 {
  private kamcoClients: KamcoClient[] = [];
  private fuzzySearcher: Fuse<KamcoClient> | null = null;

  /**
   * Initialize service by loading KAMCO clients from backend
   */
  async initialize(): Promise<void> {
    this.kamcoClients = await readKamcoClients();
    
    // Configure Fuse.js for fuzzy matching
    this.fuzzySearcher = new Fuse(this.kamcoClients, {
      keys: [
        { name: 'name', weight: 0.7 },
        { name: 'dob_or_reg_no', weight: 0.3 },
      ],
      threshold: 0.3, // Lower = more strict (0 = exact, 1 = matches anything)
      includeScore: true,
      includeMatches: true,
      minMatchCharLength: 3,
      ignoreLocation: true,
    });

    console.log(`✅ Loaded ${this.kamcoClients.length} KAMCO clients for screening`);
  }

  /**
   * Screen a list of entries against KAMCO database
   */
  async screenAgainstKamco(
    screeningList: ScreeningEntry[],
    options: {
      threshold: number; // 0-100 percentage
      includeAliases: boolean;
    }
  ): Promise<ExtendedMatchResult[]> {
    if (!this.fuzzySearcher) {
      await this.initialize();
    }

    const startTime = Date.now();
    const matches: ExtendedMatchResult[] = [];

    for (const screeningEntry of screeningList) {
      // 1. DIRECT NAME MATCH
      const directMatch = this.findDirectMatch(screeningEntry);
      if (directMatch) {
        matches.push(this.createMatchResult(directMatch, screeningEntry, 100, 'direct', 'Exact name match'));
        continue; // Skip fuzzy if direct match found
      }

      // 2. ALIAS MATCH (if enabled)
      if (options.includeAliases && screeningEntry.alias_alternate_names) {
        const aliasMatch = this.findAliasMatch(screeningEntry);
        if (aliasMatch) {
          matches.push(
            this.createMatchResult(
              aliasMatch.client,
              screeningEntry,
              95,
              'alias',
              `Matched alias: "${aliasMatch.alias}"`
            )
          );
          continue;
        }
      }

      // 3. FUZZY MATCH
      const fuzzyMatches = this.findFuzzyMatches(screeningEntry, options.threshold);
      matches.push(...fuzzyMatches);
    }

    const processingTime = Date.now() - startTime;
    console.log(
      `🔍 Screening complete: ${matches.length} matches found in ${processingTime}ms (${screeningList.length} entries screened)`
    );

    // Sort by similarity score (highest first)
    return matches.sort((a, b) => b.similarity_score - a.similarity_score);
  }

  /**
   * Find exact name match in KAMCO database
   */
  private findDirectMatch(screeningEntry: ScreeningEntry): KamcoClient | null {
    const normalizedScreeningName = this.normalizeName(screeningEntry.full_name);

    return (
      this.kamcoClients.find((client) => {
        const normalizedClientName = this.normalizeName(client.name);
        return normalizedClientName === normalizedScreeningName;
      }) || null
    );
  }

  /**
   * Find alias match in KAMCO database
   */
  private findAliasMatch(
    screeningEntry: ScreeningEntry
  ): { client: KamcoClient; alias: string } | null {
    if (!screeningEntry.alias_alternate_names) return null;

    const aliases = screeningEntry.alias_alternate_names
      .split(/[,;|]/)
      .map((a) => this.normalizeName(a.trim()))
      .filter((a) => a.length > 2);

    for (const alias of aliases) {
      const matchedClient = this.kamcoClients.find((client) => {
        const normalizedClientName = this.normalizeName(client.name);
        return normalizedClientName === alias;
      });

      if (matchedClient) {
        return { client: matchedClient, alias };
      }
    }

    return null;
  }

  /**
   * Find fuzzy matches using Fuse.js
   */
  private findFuzzyMatches(screeningEntry: ScreeningEntry, threshold: number): ExtendedMatchResult[] {
    if (!this.fuzzySearcher) return [];

    const searchResults: FuzeMatchResult[] = this.fuzzySearcher.search(screeningEntry.full_name);
    const matches: ExtendedMatchResult[] = [];

    for (const result of searchResults) {
      if (!result.score) continue;

      // Convert Fuse.js score (0 = perfect, 1 = no match) to percentage (100 = perfect, 0 = no match)
      const similarityScore = Math.round((1 - result.score) * 100);

      if (similarityScore >= threshold) {
        const matchReason = this.buildMatchReason(result, similarityScore);
        matches.push(this.createMatchResult(result.item, screeningEntry, similarityScore, 'fuzzy', matchReason));
      }
    }

    return matches;
  }

  /**
   * Create standardized match result
   */
  private createMatchResult(
    kamcoClient: KamcoClient,
    screeningEntry: ScreeningEntry,
    similarityScore: number,
    matchType: 'direct' | 'alias' | 'fuzzy',
    matchReason: string
  ): ExtendedMatchResult {
    return {
      // Customer data (from KAMCO database - 1st Excel)
      customer_id: kamcoClient.customer_id,
      customer_name: kamcoClient.name,
      customer_type: kamcoClient.type === 'individual' ? 'individual' : 'corporate',
      dob_or_reg_no: kamcoClient.dob_or_reg_no,
      nationality_country: kamcoClient.nationality_country,

      // Matched data (from screening list - 3rd Excel)
      matched_blacklist_name: screeningEntry.full_name,
      matched_alias: screeningEntry.alias_alternate_names || null,
      source: screeningEntry.source || 'Unknown',
      effective_date: screeningEntry.effective_date || 'N/A',

      // Match metadata
      similarity_score: similarityScore,
      match_type: matchType,
      match_reason: matchReason,
      matched_field: 'name',
      blacklist_type: 'user', // Always 'user' for uploaded screening lists

      // Score breakdown
      score_breakdown: {
        name_similarity: similarityScore,
        alias_similarity: 0,
        best_match: screeningEntry.full_name,
      },

      // Review state
      review_status: 'pending',

      // Embedded data for review UI
      kamco_client: kamcoClient,
      screening_entry: screeningEntry,
    };
  }

  /**
   * Build human-readable match reason
   */
  private buildMatchReason(result: FuzeMatchResult, similarityScore: number): string {
    const client = result.item;
    const reasons: string[] = [`${similarityScore}% name similarity`];

    if (result.matches && result.matches.length > 0) {
      const matchedFields = result.matches.map((m) => m.key).join(', ');
      reasons.push(`matched fields: ${matchedFields}`);
    }

    return reasons.join(' | ');
  }

  /**
   * Normalize name for comparison
   */
  private normalizeName(name: string): string {
    return name
      .toLowerCase()
      .trim()
      .replace(/\s+/g, ' ') // Multiple spaces to single space
      .replace(/[^\w\s]/g, '') // Remove special characters
      .replace(/\b(mr|mrs|ms|dr|prof|sir|ltd|llc|inc|corp)\b/gi, ''); // Remove titles/suffixes
  }

  /**
   * Get KAMCO clients count
   */
  getKamcoClientsCount(): number {
    return this.kamcoClients.length;
  }

  /**
   * Get specific KAMCO client by ID
   */
  getKamcoClient(customerId: string): KamcoClient | undefined {
    return this.kamcoClients.find((c) => c.customer_id === customerId);
  }
}

// Singleton instance
export const screeningServiceV2 = new ScreeningServiceV2();
