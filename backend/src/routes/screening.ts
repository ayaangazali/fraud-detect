// src/routes/screening.ts
import { Router, Request, Response } from 'express';
import { performFuzzyMatching } from '../utils/fuzzyMatcher';
import { ScreeningRequest, ScreeningResponse, BlacklistRow } from '../types';
import { REGULATOR_BLACKLIST } from '../data/regulator-blacklist';

const router = Router();

/**
 * POST /api/screen
 * Perform fuzzy name matching between customers and blacklist
 */
router.post('/screen', async (req: Request, res: Response) => {
  try {
    const { customers, blacklist, threshold, includeAliases }: ScreeningRequest = req.body;

    // Validate inputs
    if (!customers || !Array.isArray(customers) || customers.length === 0) {
      return res.status(400).json({ error: 'customers array is required' });
    }

    if (!blacklist || !Array.isArray(blacklist) || blacklist.length === 0) {
      return res.status(400).json({ error: 'blacklist array is required' });
    }

    if (typeof threshold !== 'number' || threshold < 0 || threshold > 100) {
      return res.status(400).json({ error: 'threshold must be a number between 0 and 100' });
    }

    const startTime = Date.now();

    // Prepare regulator blacklist with blacklist_type marker
    const regulatorBlacklist: BlacklistRow[] = REGULATOR_BLACKLIST.map(entry => ({
      ...entry,
      blacklist_type: 'regulator' as const,
    }));

    // Prepare user blacklist with blacklist_type marker
    const userBlacklist: BlacklistRow[] = blacklist.map(entry => ({
      ...entry,
      blacklist_type: 'user' as const,
    }));

    // Merge both blacklists for screening
    const combinedBlacklist = [...regulatorBlacklist, ...userBlacklist];

    console.log(`Screening against ${regulatorBlacklist.length} regulator entries and ${userBlacklist.length} user entries`);

    // Perform fuzzy matching
    const matches = performFuzzyMatching(
      customers,
      combinedBlacklist,
      threshold,
      includeAliases
    );

    const processingTime = Date.now() - startTime;

    const response: ScreeningResponse = {
      matches,
      totalCustomers: customers.length,
      totalBlacklist: combinedBlacklist.length,
      matchesFound: matches.length,
      processingTime,
    };

    res.json(response);
  } catch (error: any) {
    console.error('Screening error:', error);
    res.status(500).json({ error: error.message });
  }
});

export default router;
