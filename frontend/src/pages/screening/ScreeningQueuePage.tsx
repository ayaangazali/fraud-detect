import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Search, AlertTriangle, CheckCircle, Clock, Upload, FileX, BarChart3, Mail, Eye, CheckSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';
import ReviewModal from '@/components/review/ReviewModal';
import BulkReviewModal from '@/components/review/BulkReviewModal';
import ItemDetailReport from '@/components/review/ItemDetailReport';
import CumulativeReport from '@/components/review/CumulativeReport';
import EmailReportModal from '@/components/review/EmailReportModal';

interface QueueItem {
  id: number;
  match_id?: number;
  kamco_name: string;
  kamco_type: string;
  kamco_civil_id?: string;
  blacklist_name: string;
  blacklist_civil_id?: string;
  match_score: number;
  match_type: string;
  severity: string;
  status: 'pending' | 'flagged' | 'cleared';
  flagged_by?: string;
  flagged_at?: string;
  notes?: string;
}

/**
 * Screening Queue Page
 * 
 * This page displays screening matches from uploaded blacklist files.
 * Connected to: GET /api/screening/v2/pending-matches
 */

const ScreeningQueuePage: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  
  // Modal states
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [bulkReviewModalOpen, setBulkReviewModalOpen] = useState(false);
  const [detailReportModalOpen, setDetailReportModalOpen] = useState(false);
  const [cumulativeReportModalOpen, setCumulativeReportModalOpen] = useState(false);
  const [emailModalOpen, setEmailModalOpen] = useState(false);
  const [selectedItemForReview, setSelectedItemForReview] = useState<QueueItem | null>(null);
  const [selectedItemForDetail, setSelectedItemForDetail] = useState<number | null>(null);

  // Fetch screening queue data from backend
  useEffect(() => {
    fetchScreeningQueue();
  }, []);

  const fetchScreeningQueue = async () => {
    setIsLoading(true);
    try {
      // Use V2 endpoint that reads from ScreeningMatch table
      const response = await apiClient.get('/screening/v2/pending-matches');
      
      if (response.data.success && (response.data.queue || response.data.matches)) {
        // Map V2 response to QueueItem format
        const matches = response.data.queue || response.data.matches || [];
        const queueData: QueueItem[] = matches.map((match: any) => ({
          id: match.match_id || match.id,
          match_id: match.match_id || match.id,
          kamco_name: match.kamco_name || 'Unknown',
          kamco_type: match.kamco_type || 'Unknown',
          kamco_civil_id: match.kamco_civil_id,
          blacklist_name: match.blacklist_name || match.blacklist_name_english || 'Unknown',
          blacklist_civil_id: match.blacklist_civil_id,
          match_score: match.match_score || 0,
          match_type: match.match_type || match.confidence || 'potential',
          severity: match.severity || 'medium',
          status: match.status || match.decision_status || 'pending',
          flagged_at: match.flagged_at || match.screened_at,
        }));
        setQueueItems(queueData);
      } else {
        setQueueItems([]);
      }
      
    } catch (error: any) {
      console.error('Error fetching screening queue:', error);
      
      // Don't show error if it's just empty data
      if (error.response?.status !== 404) {
        toast.error('Failed to load screening queue');
      }
      setQueueItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Review handlers
  const handleReviewClick = (item: QueueItem) => {
    setSelectedItemForReview(item);
    setReviewModalOpen(true);
  };

  const handleViewDetailReport = (itemId: number) => {
    setSelectedItemForDetail(itemId);
    setDetailReportModalOpen(true);
  };

  const handleReviewComplete = () => {
    fetchScreeningQueue(); // Refresh the queue
    setSelectedItems([]); // Clear selection
  };

  const handleToggleSelectItem = (itemId: number) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const handleToggleSelectAll = () => {
    if (selectedItems.length === queueItems.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(queueItems.map(item => item.id));
    }
  };

  const filteredItems = queueItems.filter(item =>
    item.kamco_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.blacklist_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'flagged':
        return <AlertTriangle className="h-4 w-4" />;
      case 'cleared':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'flagged':
        return 'destructive';
      case 'cleared':
        return 'default';
      default:
        return 'secondary';
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Screening Queue</h1>
            <p className="text-muted-foreground">
              Review and manage screening matches
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setCumulativeReportModalOpen(true)}>
              <BarChart3 className="mr-2 h-4 w-4" />
              Summary Report
            </Button>
            <Button variant="outline" onClick={() => setEmailModalOpen(true)}>
              <Mail className="mr-2 h-4 w-4" />
              Email Report
            </Button>
          </div>
        </div>

        {/* Search */}
        <Card>
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by customer name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
          </CardContent>
        </Card>

        {/* Bulk Actions */}
        {selectedItems.length > 0 && (
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">
                  {selectedItems.length} item{selectedItems.length > 1 ? 's' : ''} selected
                </p>
                <div className="flex gap-2">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => setSelectedItems([])}
                  >
                    Clear Selection
                  </Button>
                  <Button 
                    size="sm"
                    onClick={() => setBulkReviewModalOpen(true)}
                  >
                    <CheckSquare className="mr-2 h-4 w-4" />
                    Bulk Review
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Queue Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Matches Found ({filteredItems.length})</CardTitle>
              {queueItems.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleToggleSelectAll}
                >
                  {selectedItems.length === queueItems.length ? 'Deselect All' : 'Select All'}
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">Loading screening results...</p>
              </div>
            ) : filteredItems.length === 0 && searchQuery ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">No matches found for "{searchQuery}"</p>
              </div>
            ) : queueItems.length === 0 ? (
              /* Empty State - No Data Uploaded Yet */
              <div className="text-center py-12 space-y-6">
                <div className="flex justify-center">
                  <div className="rounded-full bg-muted p-6">
                    <FileX className="h-12 w-12 text-muted-foreground" />
                  </div>
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">No Screening Results Yet</h3>
                  <p className="text-muted-foreground max-w-md mx-auto">
                    Upload a blacklist file to start screening. The system will automatically detect matches 
                    and display them here for your review.
                  </p>
                </div>
                <div className="flex justify-center gap-4">
                  <Button onClick={() => navigate('/upload')} className="gap-2">
                    <Upload className="h-4 w-4" />
                    Upload Blacklist File
                  </Button>
                </div>
                
                {/* Format Reference */}
                <div className="mt-8 text-left max-w-2xl mx-auto bg-muted/50 p-6 rounded-lg">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <FileX className="h-5 w-5" />
                    Expected Blacklist File Format
                  </h4>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p className="font-medium">Excel columns (use blacklist_comprehensive.xlsx as reference):</p>
                    <ul className="list-disc list-inside space-y-1 ml-4">
                      <li><strong>name_arabic</strong> (Required): Arabic name of sanctioned entity</li>
                      <li><strong>name_english</strong> (Optional): English name translation</li>
                      <li><strong>civil_id</strong> (Optional): Civil ID or identification number</li>
                      <li><strong>decree_number</strong> (Optional): Sanction decree number</li>
                      <li><strong>decree_date</strong> (Optional): Date of sanction decree</li>
                      <li><strong>type</strong> (Optional): Individual/Entity/Organization type</li>
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              /* Results List */
              <div className="space-y-4">
                {filteredItems.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center gap-3 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    {/* Checkbox */}
                    <div className="flex items-center">
                      <Checkbox
                        checked={selectedItems.includes(item.id)}
                        onCheckedChange={() => handleToggleSelectItem(item.id)}
                      />
                    </div>

                    {/* Item Details */}
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{item.kamco_name}</p>
                        <span className="text-muted-foreground">→</span>
                        <p className="text-muted-foreground">{item.blacklist_name}</p>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>Match Score: {item.match_score}%</span>
                        <span>•</span>
                        <span>{item.kamco_type}</span>
                        <span>•</span>
                        <span>{item.match_type}</span>
                        {item.severity && (
                          <>
                            <span>•</span>
                            <span className={
                              item.severity === 'high' || item.severity === 'critical' 
                                ? 'text-red-600 font-medium' 
                                : ''
                            }>
                              {item.severity} severity
                            </span>
                          </>
                        )}
                        {item.flagged_at && (
                          <>
                            <span>•</span>
                            <span>{new Date(item.flagged_at).toLocaleDateString()}</span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Status & Actions */}
                    <div className="flex items-center gap-3">
                      <Badge variant={getStatusColor(item.status)} className="gap-1">
                        {getStatusIcon(item.status)}
                        {item.status}
                      </Badge>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleViewDetailReport(item.id)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleReviewClick(item)}
                        disabled={item.status !== 'pending'}
                      >
                        Review
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Review Modals */}
      {selectedItemForReview && (
        <ReviewModal
          isOpen={reviewModalOpen}
          onClose={() => setReviewModalOpen(false)}
          item={selectedItemForReview}
          onReviewComplete={handleReviewComplete}
        />
      )}

      <BulkReviewModal
        isOpen={bulkReviewModalOpen}
        onClose={() => setBulkReviewModalOpen(false)}
        selectedItems={selectedItems}
        onReviewComplete={handleReviewComplete}
      />

      {selectedItemForDetail && (
        <ItemDetailReport
          isOpen={detailReportModalOpen}
          onClose={() => setDetailReportModalOpen(false)}
          itemId={selectedItemForDetail}
        />
      )}

      <CumulativeReport
        isOpen={cumulativeReportModalOpen}
        onClose={() => setCumulativeReportModalOpen(false)}
        onEmailReport={() => {
          setCumulativeReportModalOpen(false);
          setEmailModalOpen(true);
        }}
      />

      <EmailReportModal
        isOpen={emailModalOpen}
        onClose={() => setEmailModalOpen(false)}
      />
    </MainLayout>
  );
};

export default ScreeningQueuePage;
