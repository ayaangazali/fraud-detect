import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  User,
  FileText,
  RefreshCw,
  ChevronRight,
  Shield,
  AlertCircle,
  Info,
  ArrowLeftRight,
  Target,
  Hash,
  Calendar,
  Globe,
  Building,
  Phone,
  Mail,
  MapPin,
  Briefcase,
  CreditCard,
} from 'lucide-react';
import apiClient from '@/services/apiClient';

interface KamcoDetails {
  civil_id?: string;
  nationality?: string;
  dob?: string;
  entity_category?: string;
  address?: string;
  phone?: string;
  email?: string;
  occupation?: string;
  employer?: string;
  account_status?: string;
  risk_level?: string;
  onboarding_date?: string;
}

interface BlacklistDetails {
  civil_id?: string;
  nationality?: string;
  dob?: string;
  list_type?: string;
  source?: string;
  reason?: string;
  risk_level?: string;
}

interface MatchDetails {
  overall_score?: number;
  name_english_score?: number;
  name_arabic_score?: number;
  civil_id_score?: number;
  passport_score?: number;
  dob_score?: number;
  nationality_score?: number;
  confidence?: string;
  match_reasons?: string[];
}

interface KamcoData {
  id?: number;
  customer_id?: string;
  name_english?: string;
  name_arabic?: string;
  civil_id?: string;
  passport_number?: string;
  date_of_birth?: string;
  nationality?: string;
  entity_type?: string;
  entity_category?: string;
  occupation?: string;
  employer?: string;
  country_of_residence?: string;
  city?: string;
  phone?: string;
  email?: string;
  account_status?: string;
  risk_level?: string;
  onboarding_date?: string;
}

interface BlacklistData {
  reference?: string;
  name_english?: string;
  name_arabic?: string;
  civil_id?: string;
  passport?: string;
  nationality?: string;
  date_of_birth?: string;
  list_type?: string;
  list_source?: string;
  risk_level?: string;
  reason?: string;
}

interface ReviewItem {
  id: number;
  kamco_name: string;
  kamco_type: string;
  kamco_id?: number;
  blacklist_name: string;
  blacklist_source?: string;
  match_score: number;
  match_type: string;
  severity: string;
  status: string;
  flagged_by?: string;
  flagged_at: string;
  flag_reason?: string;
  screener_notes?: string;
  notes?: string;
  // Full comparison data from backend
  kamco_data?: KamcoData;
  blacklist_data?: BlacklistData;
  match_details?: MatchDetails;
  // Legacy fields for backward compatibility
  kamco_details?: KamcoDetails;
  blacklist_details?: BlacklistDetails;
}

const CheckerReviewPage: React.FC = () => {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState<'comparison' | 'scores' | 'details'>('comparison');

  useEffect(() => {
    fetchQueue();
  }, []);

  const fetchQueue = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/review/checker/queue');
      const data = response.data;
      // Backend returns { queue: [], data: [], count: N }
      const queueItems = data.queue || data.items || data.data || [];
      setItems(queueItems);
      if (queueItems.length > 0 && !selectedItem) {
        setSelectedItem(queueItems[0]);
      }
    } catch (err: any) {
      console.error('Failed to fetch queue:', err);
      setError(err.response?.data?.detail || 'Failed to load review queue');
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (decision: 'approved' | 'rejected' | 'recheck') => {
    if (!selectedItem) return;

    try {
      setSubmitting(true);
      await apiClient.post(`/review/checker/decision/${selectedItem.id}`, {
        decision,
        notes: reviewNotes,
      });

      const newItems = items.filter((i) => i.id !== selectedItem.id);
      setItems(newItems);
      setSelectedItem(newItems.length > 0 ? newItems[0] : null);
      setReviewNotes('');
    } catch (err: any) {
      console.error('Failed to submit decision:', err);
      setError(err.response?.data?.detail || 'Failed to submit decision');
    } finally {
      setSubmitting(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-red-500 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-yellow-500 text-black';
      case 'low': return 'bg-blue-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getScoreColor = (score: number | undefined) => {
    if (score === undefined) return 'text-gray-400';
    if (score >= 90) return 'text-red-500 font-bold';
    if (score >= 70) return 'text-orange-500 font-semibold';
    if (score >= 50) return 'text-yellow-600';
    return 'text-green-500';
  };

  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return 'N/A';
    try { return new Date(dateStr).toLocaleDateString(); } 
    catch { return dateStr; }
  };

  const getScreenerNotes = (item: ReviewItem): string => {
    return item.screener_notes || item.flag_reason || item.notes || 'No screener notes provided';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-2">Loading review queue...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="m-4">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
        <Button variant="outline" size="sm" onClick={fetchQueue} className="ml-4">Retry</Button>
      </Alert>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Checker Review Queue</h1>
          <p className="text-muted-foreground">Review flagged items and make approval decisions</p>
        </div>
        <Button variant="outline" onClick={fetchQueue} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {items.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <CheckCircle className="w-16 h-16 text-green-500 mb-4" />
            <h3 className="text-xl font-semibold">All Caught Up!</h3>
            <p className="text-muted-foreground">No items pending checker review</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-12 gap-4">
          {/* Queue List */}
          <div className="col-span-4">
            <Card className="h-[calc(100vh-200px)] overflow-auto">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Pending Items ({items.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {items.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => { setSelectedItem(item); setReviewNotes(''); }}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${selectedItem?.id === item.id ? 'border-primary bg-primary/5' : 'hover:bg-muted'}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{item.kamco_name}</p>
                        <p className="text-sm text-muted-foreground truncate">vs {item.blacklist_name}</p>
                      </div>
                      <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge className={getSeverityColor(item.severity)}>{item.severity}</Badge>
                      <Badge variant="outline" className={getScoreColor(item.match_score)}>{item.match_score?.toFixed(1)}%</Badge>
                    </div>
                    <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      {formatDate(item.flagged_at)}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Review Details */}
          <div className="col-span-8">
            {selectedItem ? (
              <div className="space-y-4">
                {/* Header Card */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          <Shield className="w-5 h-5" />
                          Match Review: {selectedItem.kamco_name}
                        </CardTitle>
                        <CardDescription>Matched against: {selectedItem.blacklist_name}</CardDescription>
                      </div>
                      <div className="flex gap-2">
                        <Badge className={getSeverityColor(selectedItem.severity)}>{selectedItem.severity} Severity</Badge>
                        <Badge variant="outline" className={getScoreColor(selectedItem.match_score)}>{selectedItem.match_score?.toFixed(1)}% Match</Badge>
                      </div>
                    </div>
                  </CardHeader>
                </Card>

                {/* Screener Notes */}
                <Alert>
                  <Info className="h-4 w-4" />
                  <div className="ml-2">
                    <p className="font-medium">Screener Notes</p>
                    <p className="text-sm text-muted-foreground mt-1">{getScreenerNotes(selectedItem)}</p>
                  </div>
                </Alert>

                {/* Tab Navigation */}
                <div className="flex gap-2 border-b pb-2">
                  <Button variant={activeTab === 'comparison' ? 'default' : 'ghost'} size="sm" onClick={() => setActiveTab('comparison')}>
                    <ArrowLeftRight className="w-4 h-4 mr-2" />Comparison
                  </Button>
                  <Button variant={activeTab === 'scores' ? 'default' : 'ghost'} size="sm" onClick={() => setActiveTab('scores')}>
                    <Target className="w-4 h-4 mr-2" />Match Scores
                  </Button>
                  <Button variant={activeTab === 'details' ? 'default' : 'ghost'} size="sm" onClick={() => setActiveTab('details')}>
                    <FileText className="w-4 h-4 mr-2" />Full Details
                  </Button>
                </div>

                {/* Comparison Tab */}
                {activeTab === 'comparison' && (
                  <div className="grid grid-cols-2 gap-4">
                    {/* Kamco Entity */}
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-base flex items-center gap-2">
                          <Building className="w-4 h-4 text-blue-500" />Kamco Database
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-2 text-sm">
                        <div className="flex items-center gap-2"><User className="w-4 h-4" /><span className="text-muted-foreground">Name:</span><span className="font-medium">{selectedItem.kamco_data?.name_english || selectedItem.kamco_name}</span></div>
                        <div className="flex items-center gap-2"><Hash className="w-4 h-4" /><span className="text-muted-foreground">Type:</span><span>{selectedItem.kamco_data?.entity_type || selectedItem.kamco_type || 'N/A'}</span></div>
                        <div className="flex items-center gap-2"><CreditCard className="w-4 h-4" /><span className="text-muted-foreground">Civil ID:</span><span>{selectedItem.kamco_data?.civil_id || 'N/A'}</span></div>
                        <div className="flex items-center gap-2"><Globe className="w-4 h-4" /><span className="text-muted-foreground">Nationality:</span><span>{selectedItem.kamco_data?.nationality || 'N/A'}</span></div>
                        <div className="flex items-center gap-2"><Calendar className="w-4 h-4" /><span className="text-muted-foreground">DOB:</span><span>{formatDate(selectedItem.kamco_data?.date_of_birth)}</span></div>
                        <hr className="my-2" />
                        <div className="flex items-center gap-2"><MapPin className="w-4 h-4" /><span className="text-muted-foreground">City:</span><span>{selectedItem.kamco_data?.city || 'N/A'}</span></div>
                        <div className="flex items-center gap-2"><Phone className="w-4 h-4" /><span className="text-muted-foreground">Phone:</span><span>{selectedItem.kamco_data?.phone || 'N/A'}</span></div>
                        <div className="flex items-center gap-2"><Mail className="w-4 h-4" /><span className="text-muted-foreground">Email:</span><span>{selectedItem.kamco_data?.email || 'N/A'}</span></div>
                        <div className="flex items-center gap-2"><Briefcase className="w-4 h-4" /><span className="text-muted-foreground">Occupation:</span><span>{selectedItem.kamco_data?.occupation || 'N/A'}</span></div>
                      </CardContent>
                    </Card>

                    {/* Blacklist Entry */}
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-base flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-red-500" />Blacklist Entry
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-2 text-sm">
                        <div className="flex items-center gap-2"><User className="w-4 h-4" /><span className="text-muted-foreground">Name:</span><span className="font-medium">{selectedItem.blacklist_data?.name_english || selectedItem.blacklist_name}</span></div>
                        <div className="flex items-center gap-2"><Hash className="w-4 h-4" /><span className="text-muted-foreground">List Type:</span><span>{selectedItem.blacklist_data?.list_type || selectedItem.match_type || 'N/A'}</span></div>
                        <div className="flex items-center gap-2"><CreditCard className="w-4 h-4" /><span className="text-muted-foreground">Civil ID:</span><span>{selectedItem.blacklist_data?.civil_id || 'N/A'}</span></div>
                        <div className="flex items-center gap-2"><Globe className="w-4 h-4" /><span className="text-muted-foreground">Nationality:</span><span>{selectedItem.blacklist_data?.nationality || 'N/A'}</span></div>
                        <div className="flex items-center gap-2"><Calendar className="w-4 h-4" /><span className="text-muted-foreground">DOB:</span><span>{formatDate(selectedItem.blacklist_data?.date_of_birth)}</span></div>
                        <hr className="my-2" />
                        <div className="flex items-center gap-2"><FileText className="w-4 h-4" /><span className="text-muted-foreground">Source:</span><span>{selectedItem.blacklist_data?.list_source || selectedItem.blacklist_source || 'N/A'}</span></div>
                        <div className="flex items-center gap-2">
                          <AlertCircle className="w-4 h-4" />
                          <span className="text-muted-foreground">Risk:</span>
                          <Badge variant="outline" className={selectedItem.blacklist_data?.risk_level === 'HIGH' ? 'border-red-500 text-red-500' : 'border-yellow-500 text-yellow-500'}>
                            {selectedItem.blacklist_data?.risk_level || 'N/A'}
                          </Badge>
                        </div>
                        <div className="mt-2 p-2 bg-red-50 rounded border border-red-200">
                          <span className="text-muted-foreground">Reason: </span>
                          {selectedItem.blacklist_data?.reason || 'No reason provided'}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {/* Match Scores Tab */}
                {activeTab === 'scores' && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Match Score Breakdown</CardTitle>
                      <CardDescription>Detailed analysis of why this match was flagged</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-3">
                          <div className="flex justify-between p-2 bg-muted rounded"><span>Overall Score</span><span className={`font-bold ${getScoreColor(selectedItem.match_details?.overall_score || selectedItem.match_score)}`}>{(selectedItem.match_details?.overall_score || selectedItem.match_score)?.toFixed(1)}%</span></div>
                          <div className="flex justify-between p-2"><span>Name (English)</span><span className={getScoreColor(selectedItem.match_details?.name_english_score)}>{selectedItem.match_details?.name_english_score?.toFixed(1) || 'N/A'}%</span></div>
                          <div className="flex justify-between p-2 bg-muted/50 rounded"><span>Name (Arabic)</span><span className={getScoreColor(selectedItem.match_details?.name_arabic_score)}>{selectedItem.match_details?.name_arabic_score?.toFixed(1) || 'N/A'}%</span></div>
                          <div className="flex justify-between p-2"><span>Civil ID</span><span className={getScoreColor(selectedItem.match_details?.civil_id_score)}>{selectedItem.match_details?.civil_id_score?.toFixed(1) || 'N/A'}%</span></div>
                        </div>
                        <div className="space-y-3">
                          <div className="flex justify-between p-2 bg-muted rounded"><span>Confidence</span><Badge variant="outline">{selectedItem.match_details?.confidence || 'N/A'}</Badge></div>
                          <div className="flex justify-between p-2"><span>Passport</span><span className={getScoreColor(selectedItem.match_details?.passport_score)}>{selectedItem.match_details?.passport_score?.toFixed(1) || 'N/A'}%</span></div>
                          <div className="flex justify-between p-2 bg-muted/50 rounded"><span>Date of Birth</span><span className={getScoreColor(selectedItem.match_details?.dob_score)}>{selectedItem.match_details?.dob_score?.toFixed(1) || 'N/A'}%</span></div>
                          <div className="flex justify-between p-2"><span>Nationality</span><span className={getScoreColor(selectedItem.match_details?.nationality_score)}>{selectedItem.match_details?.nationality_score?.toFixed(1) || 'N/A'}%</span></div>
                        </div>
                      </div>
                      {selectedItem.match_details?.match_reasons && selectedItem.match_details.match_reasons.length > 0 && (
                        <div className="mt-4 pt-4 border-t">
                          <h4 className="font-medium mb-2">Match Reasons</h4>
                          <div className="flex flex-wrap gap-2">
                            {selectedItem.match_details.match_reasons.map((reason, idx) => (<Badge key={idx} variant="secondary">{reason}</Badge>))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                {/* Full Details Tab */}
                {activeTab === 'details' && (
                  <Card>
                    <CardHeader><CardTitle className="text-base">Complete Information</CardTitle></CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-medium mb-3 text-blue-600">Kamco Entity</h4>
                          <div className="space-y-1 text-sm">
                            <p><strong>Name:</strong> {selectedItem.kamco_data?.name_english || selectedItem.kamco_name}</p>
                            <p><strong>Type:</strong> {selectedItem.kamco_data?.entity_type || selectedItem.kamco_type}</p>
                            <p><strong>Civil ID:</strong> {selectedItem.kamco_data?.civil_id || 'N/A'}</p>
                            <p><strong>Passport:</strong> {selectedItem.kamco_data?.passport_number || 'N/A'}</p>
                            <p><strong>Nationality:</strong> {selectedItem.kamco_data?.nationality || 'N/A'}</p>
                            <p><strong>DOB:</strong> {formatDate(selectedItem.kamco_data?.date_of_birth)}</p>
                            <p><strong>Category:</strong> {selectedItem.kamco_data?.entity_category || 'N/A'}</p>
                            <p><strong>City:</strong> {selectedItem.kamco_data?.city || 'N/A'}</p>
                            <p><strong>Country:</strong> {selectedItem.kamco_data?.country_of_residence || 'N/A'}</p>
                            <p><strong>Phone:</strong> {selectedItem.kamco_data?.phone || 'N/A'}</p>
                            <p><strong>Email:</strong> {selectedItem.kamco_data?.email || 'N/A'}</p>
                            <p><strong>Occupation:</strong> {selectedItem.kamco_data?.occupation || 'N/A'}</p>
                            <p><strong>Employer:</strong> {selectedItem.kamco_data?.employer || 'N/A'}</p>
                            <p><strong>Account Status:</strong> {selectedItem.kamco_data?.account_status || 'N/A'}</p>
                            <p><strong>Risk Level:</strong> {selectedItem.kamco_data?.risk_level || 'N/A'}</p>
                            <p><strong>Onboarding:</strong> {formatDate(selectedItem.kamco_data?.onboarding_date)}</p>
                          </div>
                        </div>
                        <div>
                          <h4 className="font-medium mb-3 text-red-600">Blacklist Entry</h4>
                          <div className="space-y-1 text-sm">
                            <p><strong>Name:</strong> {selectedItem.blacklist_data?.name_english || selectedItem.blacklist_name}</p>
                            <p><strong>List Type:</strong> {selectedItem.blacklist_data?.list_type || selectedItem.match_type || 'N/A'}</p>
                            <p><strong>Civil ID:</strong> {selectedItem.blacklist_data?.civil_id || 'N/A'}</p>
                            <p><strong>Passport:</strong> {selectedItem.blacklist_data?.passport || 'N/A'}</p>
                            <p><strong>Nationality:</strong> {selectedItem.blacklist_data?.nationality || 'N/A'}</p>
                            <p><strong>DOB:</strong> {formatDate(selectedItem.blacklist_data?.date_of_birth)}</p>
                            <p><strong>Source:</strong> {selectedItem.blacklist_data?.list_source || selectedItem.blacklist_source || 'N/A'}</p>
                            <p><strong>Risk Level:</strong> {selectedItem.blacklist_data?.risk_level || 'N/A'}</p>
                            <p><strong>Reason:</strong> {selectedItem.blacklist_data?.reason || 'N/A'}</p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Decision Card */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Your Decision</CardTitle>
                    <CardDescription>Review the information above and make your decision</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="notes">Checker Notes</Label>
                      <Textarea id="notes" placeholder="Add your review notes and justification..." value={reviewNotes} onChange={(e) => setReviewNotes(e.target.value)} rows={3} className="mt-1" />
                    </div>
                    <div className="flex gap-3">
                      <Button onClick={() => handleDecision('approved')} disabled={submitting} className="flex-1 bg-green-600 hover:bg-green-700"><CheckCircle className="w-4 h-4 mr-2" />Approve (Clear)</Button>
                      <Button onClick={() => handleDecision('rejected')} disabled={submitting} variant="destructive" className="flex-1"><XCircle className="w-4 h-4 mr-2" />Reject (Confirm Match)</Button>
                      <Button onClick={() => handleDecision('recheck')} disabled={submitting} variant="outline" className="flex-1"><RefreshCw className="w-4 h-4 mr-2" />Request Recheck</Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card className="h-64 flex items-center justify-center">
                <div className="text-center text-muted-foreground">
                  <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Select an item from the queue to review</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CheckerReviewPage;
