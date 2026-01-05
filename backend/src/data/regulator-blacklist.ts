// src/data/regulator-blacklist.ts
/**
 * Hardcoded regulator blacklist containing known dangerous individuals,
 * international criminals, terrorists, and sanctioned entities.
 * This list is always checked in addition to user-uploaded blacklists.
 */

import { BlacklistRow } from '../types';

export const REGULATOR_BLACKLIST: BlacklistRow[] = [
  // International Terrorists
  {
    full_name: 'Osama Bin Laden',
    alias_alternate_names: 'Usama Bin Laden;Osama Bin Muhammad;UBL',
    source: 'REGULATOR',
    effective_date: '2001-09-14',
  },
  {
    full_name: 'Ayman Al-Zawahiri',
    alias_alternate_names: 'Ayman Zawahiri;Abu Muhammad;The Doctor',
    source: 'REGULATOR',
    effective_date: '2001-10-10',
  },
  {
    full_name: 'Abu Bakr Al-Baghdadi',
    alias_alternate_names: 'Ibrahim Awad;Abu Dua;Caliph Ibrahim',
    source: 'REGULATOR',
    effective_date: '2014-06-29',
  },
  {
    full_name: 'Khalid Sheikh Mohammed',
    alias_alternate_names: 'KSM;Khalid Shaikh Mohammad;The Brain',
    source: 'REGULATOR',
    effective_date: '2003-03-01',
  },
  {
    full_name: 'Abu Musab Al-Zarqawi',
    alias_alternate_names: 'Ahmad Fadil;Abu Musab',
    source: 'REGULATOR',
    effective_date: '2004-02-05',
  },
  
  // Drug Lords & International Criminals
  {
    full_name: 'Joaquin Guzman Loera',
    alias_alternate_names: 'El Chapo;Joaquin Archivaldo Guzman',
    source: 'REGULATOR',
    effective_date: '1993-06-09',
  },
  {
    full_name: 'Pablo Escobar',
    alias_alternate_names: 'Pablo Emilio Escobar Gaviria;The King of Cocaine',
    source: 'REGULATOR',
    effective_date: '1976-01-01',
  },
  {
    full_name: 'Ismael Zambada Garcia',
    alias_alternate_names: 'El Mayo;Mayo Zambada',
    source: 'REGULATOR',
    effective_date: '2002-08-01',
  },
  {
    full_name: 'Nemesio Oseguera Cervantes',
    alias_alternate_names: 'El Mencho;Ruben Oseguera Cervantes',
    source: 'REGULATOR',
    effective_date: '2015-04-08',
  },
  
  // Arms Dealers
  {
    full_name: 'Viktor Bout',
    alias_alternate_names: 'Victor Bout;The Merchant of Death;Viktor Anatolyevich Bout',
    source: 'REGULATOR',
    effective_date: '2008-03-06',
  },
  {
    full_name: 'Monzer Al-Kassar',
    alias_alternate_names: 'Monzer Al Kassar;The Prince of Marbella',
    source: 'REGULATOR',
    effective_date: '2007-06-07',
  },
  
  // War Criminals
  {
    full_name: 'Ratko Mladic',
    alias_alternate_names: 'Ratko Mladić;The Butcher of Bosnia',
    source: 'REGULATOR',
    effective_date: '1995-07-25',
  },
  {
    full_name: 'Radovan Karadzic',
    alias_alternate_names: 'Radovan Karadžić;Dragan Dabic',
    source: 'REGULATOR',
    effective_date: '1996-07-25',
  },
  {
    full_name: 'Joseph Kony',
    alias_alternate_names: 'Joseph Rao Kony;Kony',
    source: 'REGULATOR',
    effective_date: '2005-10-13',
  },
  
  // Financial Criminals & Fraudsters
  {
    full_name: 'Bernard Madoff',
    alias_alternate_names: 'Bernie Madoff;Bernard Lawrence Madoff',
    source: 'REGULATOR',
    effective_date: '2008-12-11',
  },
  {
    full_name: 'Allen Stanford',
    alias_alternate_names: 'Robert Allen Stanford;Sir Allen Stanford',
    source: 'REGULATOR',
    effective_date: '2009-02-17',
  },
  
  // Cyber Criminals
  {
    full_name: 'Evgeniy Bogachev',
    alias_alternate_names: 'lucky12345;slavik;Evgeniy Mikhailovich Bogachev',
    source: 'REGULATOR',
    effective_date: '2014-06-02',
  },
  {
    full_name: 'Maksim Yakubets',
    alias_alternate_names: 'aqua;Maksim Viktorovich Yakubets',
    source: 'REGULATOR',
    effective_date: '2019-12-05',
  },
  
  // Human Traffickers
  {
    full_name: 'Matteo Messina Denaro',
    alias_alternate_names: 'Diabolik;Matteo Messina',
    source: 'REGULATOR',
    effective_date: '1993-01-01',
  },
  
  // Middle Eastern Sanctioned Entities
  {
    full_name: 'Qasem Soleimani',
    alias_alternate_names: 'Qassem Soleimani;Qasim Sulaymani;Hajj Qassem',
    source: 'REGULATOR',
    effective_date: '2020-01-03',
  },
  {
    full_name: 'Hassan Nasrallah',
    alias_alternate_names: 'Hasan Nasrallah;Hassan Nasrullah',
    source: 'REGULATOR',
    effective_date: '2012-08-02',
  },
  {
    full_name: 'Ismail Haniyeh',
    alias_alternate_names: 'Ismail Haniya;Ismail Abd al-Salam Haniyeh',
    source: 'REGULATOR',
    effective_date: '2018-01-31',
  },
  
  // International Fugitives (INTERPOL Red Notice)
  {
    full_name: 'Semion Mogilevich',
    alias_alternate_names: 'Don Semyon;Seva Moguilevich;The Brainy Don',
    source: 'REGULATOR',
    effective_date: '2009-10-21',
  },
  {
    full_name: 'Dawood Ibrahim',
    alias_alternate_names: 'Dawood Ibrahim Kaskar;Sheikh Dawood Hassan',
    source: 'REGULATOR',
    effective_date: '2003-11-03',
  },
  {
    full_name: 'Matteo Messina Denaro',
    alias_alternate_names: 'Diabolik;U Siccu',
    source: 'REGULATOR',
    effective_date: '1993-04-12',
  },
  
  // Piracy & Maritime Criminals
  {
    full_name: 'Abduwali Muse',
    alias_alternate_names: 'Abduwali Abdukhadir Muse',
    source: 'REGULATOR',
    effective_date: '2009-04-12',
  },
  
  // Notorious Gang Leaders
  {
    full_name: 'Daut Kadriovski',
    alias_alternate_names: 'The Boss;Daut Kadriu',
    source: 'REGULATOR',
    effective_date: '2015-06-10',
  },
  
  // Additional Middle Eastern Entries for Regional Relevance
  {
    full_name: 'Omar Abdullah Bin Laden',
    alias_alternate_names: 'Omar Bin Laden;Omar Osama Bin Laden',
    source: 'REGULATOR',
    effective_date: '2018-03-01',
  },
  {
    full_name: 'Hamza Bin Laden',
    alias_alternate_names: 'Hamza Bin Osama;Hamza Bin Ladin',
    source: 'REGULATOR',
    effective_date: '2017-01-05',
  },
  {
    full_name: 'Abdullah Ahmed Abdullah',
    alias_alternate_names: 'Abu Muhammad al-Masri;Saleh',
    source: 'REGULATOR',
    effective_date: '1998-08-07',
  },
];
