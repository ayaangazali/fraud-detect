import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertTriangle, ChevronLeft, ChevronRight, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface BulkReviewWizardProps {
  isOpen: boolean;
  onClose: () => void;
  selectedItemIds: number[];
  onReviewComplete?: () => void;
}

interface ItemDetails {
  id: number;
  match_info: {
    match_score: number;
    match_type: string;
    severity: string;
    confidence_level: string;
    recommended_action: string;
  };
  kamco_entity: {
    name: string;
    name_arabic?: string;
    type: string;
    civil_id?: string;
    nationality?: string;
    country?: string;
    risk_level?: string;
    status?: string;
    [key: string]: any;
  };
  blacklist_entry: {
    name_english: string;
    name_arabic?: string;
    civil_id?: string;
    country?: string;
    list_name?: string;
    reason?: string;
    date_added?: string;
    [key: string]: any;
  };
  current_status: string;
  flagged_at: string;
}

interface ReviewDecision {
  item_id: number;
  decision: 'approved' | 'rejected' | 'escalated' | null;
  notes: string;
  escalation_notes?: string;
}

const BulkReviewWizard: React.FC<BulkReviewWizardProps> = ({
  isOpen,
  onClose,
  selectedItemIds,
  onReviewComplete,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [itemsDetails, setItemsDetails] = useState<ItemDetails[]>([]);
  const [decisions, setDecisions] = useState<Map<number, ReviewDecision>>(new Map());
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generateReports, setGenerateReports] = useState(false);

  const currentItem = itemsDetails[currentIndex];
  const currentDecision = currentItem ? decisions.get(currentItem.id) : null;

  // Fetch details for all items
  useEffect(() => {
    if (isOpen && selectedItemIds.length > 0) {
      fetchItemsDetails();
    }
  }, [isOpen, selectedItemIds]);

  const fetchItemsDetails = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.post('/reviews/bulk-items-details', {
        item_ids: selectedItemIds,
      });

      if (response.data.success) {
        setItemsDetails(response.data.items);
        // Initialize decisions map
        const initialDecisions = new Map<number, ReviewDecision>();
        response.data.items.forEach((item: ItemDetails) => {
          initialDecisions.set(item.id, {
            item_id: item.id,
            decision: null,
            notes: '',
          });
        });
        setDecisions(initialDecisions);
      } else {
        toast.error('Failed to load item details');
      }
    } catch (error: any) {
      console.error('Error fetching items details:', error);
      toast.error(error.response?.data?.detail || 'Failed to load items');
    } finally {
      setIsLoading(false);
    }
  };

  const updateDecision = (field: keyof ReviewDecision, value: any) => {
    if (!currentItem) return;

    const updated = new Map(decisions);
    const current = updated.get(currentItem.id) || {
      item_id: currentItem.id,
      decision: null,
      notes: '',
    };

    updated.set(currentItem.id, {
      ...current,
      [field]: value,
    });

    setDecisions(updated);
  };

  const goToNext = () => {
    if (currentIndex < itemsDetails.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const goToPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleSubmitAll = async () => {
    // Validate all decisions
    const reviewsToSubmit: any[] = [];
    let hasInvalidDecisions = false;

    decisions.forEach((decision) => {
      if (!decision.decision) {
        hasInvalidDecisions = true;
        return;
      }
      if (!decision.notes.trim()) {
        hasInvalidDecisions = true;
        return;
      }
      reviewsToSubmit.push(decision);
    });

    if (hasInvalidDecisions) {
      toast.error('Please complete all reviews with decisions and notes');
      return;
    }

    setIsSubmitting(true);

    try {
      // Submit all reviews
      const response = await apiClient.post('/reviews/submit-bulk-wizard', reviewsToSubmit);

      if (response.data.success) {
        toast.success('Successfully reviewed ' + response.data.processed + ' items');

        // Generate reports if requested
        if (generateReports) {
          await generateBatchReports();
        }

        onReviewComplete?.();
        handleClose();
      } else {
        toast.error(response.data.failed + ' items failed to process');
      }
    } catch (error: any) {
      console.error('Error submitting bulk reviews:', error);
      // Handle different error formats properly
      let errorMessage = 'Failed to submit reviews';
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          // Handle validation error array format
          errorMessage = error.response.data.detail
            .map((e: any) => (typeof e === 'string' ? e : e.msg || JSON.stringify(e)))
            .join(', ');
        } else if (typeof error.response.data.detail === 'object') {
          errorMessage = error.response.data.detail.msg || JSON.stringify(error.response.data.detail);
        }
      }
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const generateBatchReports = async () => {
    try {
      const response = await apiClient.post('/reviews/generate-reports-batch', {
        item_ids: selectedItemIds,
        report_format: 'pdf',
      });

      if (response.data.success) {
        toast.success(`Generated ${response.data.generated} reports`);
        // You could trigger downloads here
      }
    } catch (error: any) {
      console.error('Error generating reports:', error);
      toast.error('Failed to generate some reports');
    }
  };

  const handleClose = () => {
    setCurrentIndex(0);
    setItemsDetails([]);
    setDecisions(new Map());
    setGenerateReports(false);
    onClose();
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getProgressPercentage = () => {
    const completed = Array.from(decisions.values()).filter(d => d.decision !== null).length;
    return Math.round((completed / itemsDetails.length) * 100);
  };

  if (isLoading) {
    return (
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="max-w-5xl">
          <div className="flex items-center justify-center p-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Loading item details...</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (!currentItem) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-6xl max-h-[95vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            Bulk Review Wizard - Item {currentIndex + 1} of {itemsDetails.length}
          </DialogTitle>
          <DialogDescription>
            Review each item individually with full details. Navigate through all items before submitting.
          </DialogDescription>
        </DialogHeader>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">
              Progress: {getProgressPercentage()}% complete
            </span>
            <span className="text-sm font-medium">
              {Array.from(decisions.values()).filter(d => d.decision !== null).length} / {itemsDetails.length} reviewed
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
        </div>

        {/* Side-by-Side Comparison */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Left: Kamco Entity */}
          <div className="border rounded-lg p-4 bg-blue-50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                🏢 Kamco Entity
              </h3>
              <Badge className={getSeverityColor(currentItem.match_info.severity)}>
                {currentItem.match_info.severity.toUpperCase()}
              </Badge>
            </div>
            
            <div className="space-y-2 text-sm">
              <div>
                <p className="text-muted-foreground">Name (English)</p>
                <p className="font-medium">{currentItem.kamco_entity.name}</p>
              </div>
              
              {currentItem.kamco_entity.name_arabic && (
                <div>
                  <p className="text-muted-foreground">Name (Arabic)</p>
                  <p className="font-medium text-right" dir="rtl">{currentItem.kamco_entity.name_arabic}</p>
                </div>
              )}
              
              <div>
                <p className="text-muted-foreground">Type</p>
                <p className="font-medium">{currentItem.kamco_entity.type}</p>
              </div>
              
              {currentItem.kamco_entity.civil_id && (
                <div>
                  <p className="text-muted-foreground">Civil ID</p>
                  <p className="font-medium">{currentItem.kamco_entity.civil_id}</p>
                </div>
              )}
              
              {currentItem.kamco_entity.nationality && (
                <div>
                  <p className="text-muted-foreground">Nationality</p>
                  <p className="font-medium">{currentItem.kamco_entity.nationality}</p>
                </div>
              )}
              
              {currentItem.kamco_entity.country && (
                <div>
                  <p className="text-muted-foreground">Country</p>
                  <p className="font-medium">{currentItem.kamco_entity.country}</p>
                </div>
              )}
              
              {currentItem.kamco_entity.risk_level && (
                <div>
                  <p className="text-muted-foreground">Risk Level</p>
                  <p className="font-medium">{currentItem.kamco_entity.risk_level}</p>
                </div>
              )}
              
              <div>
                <p className="text-muted-foreground">Status</p>
                <p className="font-medium">{currentItem.kamco_entity.status || 'Active'}</p>
              </div>
            </div>
          </div>

          {/* Right: Blacklist Entry */}
          <div className="border rounded-lg p-4 bg-red-50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                ⚠️ Blacklist Entry
              </h3>
            </div>
            
            <div className="space-y-2 text-sm">
              <div>
                <p className="text-muted-foreground">Name (English)</p>
                <p className="font-medium">{currentItem.blacklist_entry.name_english}</p>
              </div>
              
              {currentItem.blacklist_entry.name_arabic && (
                <div>
                  <p className="text-muted-foreground">Name (Arabic)</p>
                  <p className="font-medium text-right" dir="rtl">{currentItem.blacklist_entry.name_arabic}</p>
                </div>
              )}
              
              {currentItem.blacklist_entry.list_name && (
                <div>
                  <p className="text-muted-foreground">List</p>
                  <p className="font-medium">{currentItem.blacklist_entry.list_name}</p>
                </div>
              )}
              
              {currentItem.blacklist_entry.civil_id && (
                <div>
                  <p className="text-muted-foreground">Civil ID</p>
                  <p className="font-medium">{currentItem.blacklist_entry.civil_id}</p>
                </div>
              )}
              
              {currentItem.blacklist_entry.country && (
                <div>
                  <p className="text-muted-foreground">Country</p>
                  <p className="font-medium">{currentItem.blacklist_entry.country}</p>
                </div>
              )}
              
              {currentItem.blacklist_entry.reason && (
                <div>
                  <p className="text-muted-foreground">Reason</p>
                  <p className="font-medium">{currentItem.blacklist_entry.reason}</p>
                </div>
              )}
              
              {currentItem.blacklist_entry.date_added && (
                <div>
                  <p className="text-muted-foreground">Added</p>
                  <p className="font-medium">{new Date(currentItem.blacklist_entry.date_added).toLocaleDateString()}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Match Information */}
        <div className="border rounded-lg p-4 bg-muted mb-6">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-muted-foreground">Match Score</p>
              <p className="text-2xl font-bold">{currentItem.match_info.match_score}%</p>
              <p className="text-xs text-muted-foreground">{currentItem.match_info.confidence_level}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Match Type</p>
              <p className="text-lg font-medium">{currentItem.match_info.match_type.replace('_', ' ').toUpperCase()}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Current Status</p>
              <p className="text-lg font-medium capitalize">{currentItem.current_status}</p>
            </div>
          </div>
          
          <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
            <p className="font-medium text-blue-900">Recommended Action:</p>
            <p className="text-blue-700">{currentItem.match_info.recommended_action}</p>
          </div>
        </div>

        {/* Decision Section */}
        <div className="space-y-4 mb-6">
          <div>
            <Label className="text-base font-semibold mb-3 block">Decision for This Item *</Label>
            <div className="grid grid-cols-3 gap-3">
              <Button
                type="button"
                variant={currentDecision?.decision === 'approved' ? 'default' : 'outline'}
                className={currentDecision?.decision === 'approved' ? 'bg-green-600 hover:bg-green-700' : ''}
                onClick={() => updateDecision('decision', 'approved')}
              >
                <CheckCircle className="mr-2 h-4 w-4" />
                Flagged (Approve)
              </Button>
              <Button
                type="button"
                variant={currentDecision?.decision === 'rejected' ? 'default' : 'outline'}
                className={currentDecision?.decision === 'rejected' ? 'bg-red-600 hover:bg-red-700' : ''}
                onClick={() => updateDecision('decision', 'rejected')}
              >
                <XCircle className="mr-2 h-4 w-4" />
                Not Flagged (Reject)
              </Button>
              <Button
                type="button"
                variant={currentDecision?.decision === 'escalated' ? 'default' : 'outline'}
                className={currentDecision?.decision === 'escalated' ? 'bg-orange-600 hover:bg-orange-700' : ''}
                onClick={() => updateDecision('decision', 'escalated')}
              >
                <AlertTriangle className="mr-2 h-4 w-4" />
                Needs Escalation
              </Button>
            </div>
          </div>

          <div>
            <Label htmlFor="notes">Review Notes *</Label>
            <Textarea
              id="notes"
              placeholder="Enter your review notes for this item..."
              value={currentDecision?.notes || ''}
              onChange={(e) => updateDecision('notes', e.target.value)}
              rows={3}
              className="resize-none"
            />
          </div>

          {currentDecision?.decision === 'escalated' && (
            <div>
              <Label htmlFor="escalation">Escalation Reason</Label>
              <Textarea
                id="escalation"
                placeholder="Why does this case need escalation?"
                value={currentDecision?.escalation_notes || ''}
                onChange={(e) => updateDecision('escalation_notes', e.target.value)}
                rows={2}
                className="resize-none"
              />
            </div>
          )}
        </div>

        {/* Navigation and Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={goToPrevious}
              disabled={currentIndex === 0}
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>
            <Button
              variant="outline"
              onClick={goToNext}
              disabled={currentIndex === itemsDetails.length - 1}
            >
              Next
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </div>

          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={generateReports}
                onChange={(e) => setGenerateReports(e.target.checked)}
                className="rounded"
              />
              <FileText className="h-4 w-4" />
              Generate Reports
            </label>

            <Button variant="outline" onClick={handleClose} disabled={isSubmitting}>
              Cancel
            </Button>
            
            <Button
              onClick={handleSubmitAll}
              disabled={isSubmitting || getProgressPercentage() < 100}
              className="min-w-[150px]"
            >
              {isSubmitting ? 'Submitting...' : `Submit All (${itemsDetails.length})`}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default BulkReviewWizard;
