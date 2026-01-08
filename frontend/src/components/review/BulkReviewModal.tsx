import React, { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface BulkReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedItems: number[];
  onReviewComplete?: () => void;
}

type ReviewDecision = 'approved' | 'rejected';

const BulkReviewModal: React.FC<BulkReviewModalProps> = ({
  isOpen,
  onClose,
  selectedItems,
  onReviewComplete,
}) => {
  const [decision, setDecision] = useState<ReviewDecision | null>(null);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!decision) {
      toast.error('Please select a decision');
      return;
    }

    if (!notes.trim()) {
      toast.error('Please add review notes');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await apiClient.post('/reviews/review/bulk', {
        item_ids: selectedItems,
        decision,
        notes: notes.trim(),
      });

      if (response.data.success) {
        toast.success(`${selectedItems.length} items ${decision} successfully`);
        onReviewComplete?.();
        handleClose();
      } else {
        toast.error(response.data.message || 'Bulk review submission failed');
      }
    } catch (error: any) {
      console.error('Error submitting bulk review:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit bulk review');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setDecision(null);
    setNotes('');
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Bulk Review</DialogTitle>
          <DialogDescription>
            Apply the same decision to {selectedItems.length} selected items
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Warning */}
          <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-orange-600 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-orange-900">Bulk Action</p>
                <p className="text-orange-700 mt-1">
                  This will apply the same decision and notes to all {selectedItems.length} selected items.
                  Use this only when all items have the same review outcome.
                </p>
              </div>
            </div>
          </div>

          {/* Decision Buttons */}
          <div className="space-y-2">
            <Label>Decision *</Label>
            <div className="grid grid-cols-2 gap-3">
              <Button
                type="button"
                variant={decision === 'approved' ? 'default' : 'outline'}
                className={decision === 'approved' ? 'bg-green-600 hover:bg-green-700' : ''}
                onClick={() => setDecision('approved')}
              >
                <CheckCircle className="mr-2 h-4 w-4" />
                Approve All
              </Button>
              <Button
                type="button"
                variant={decision === 'rejected' ? 'default' : 'outline'}
                className={decision === 'rejected' ? 'bg-red-600 hover:bg-red-700' : ''}
                onClick={() => setDecision('rejected')}
              >
                <XCircle className="mr-2 h-4 w-4" />
                Reject All
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Note: Escalation is not available for bulk reviews. Review items individually if escalation is needed.
            </p>
          </div>

          {/* Decision Guidance */}
          {decision && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="text-sm">
                  {decision === 'approved' && (
                    <>
                      <p className="font-medium text-blue-900">Approve All: Confirm Matches</p>
                      <p className="text-blue-700 mt-1">
                        All selected items are confirmed matches. Document the common reason.
                      </p>
                    </>
                  )}
                  {decision === 'rejected' && (
                    <>
                      <p className="font-medium text-blue-900">Reject All: False Positives</p>
                      <p className="text-blue-700 mt-1">
                        All selected items are false positives. Explain the common pattern.
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Review Notes */}
          <div className="space-y-2">
            <Label htmlFor="bulk-notes">Review Notes *</Label>
            <Textarea
              id="bulk-notes"
              placeholder="Enter notes that apply to all selected items... (e.g., All items are common name false positives with no Civil ID matches.)"
              value={notes}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNotes(e.target.value)}
              rows={4}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground">
              These notes will be applied to all {selectedItems.length} selected items.
            </p>
          </div>

          {/* Summary */}
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium">Summary</p>
            <p className="text-sm text-muted-foreground mt-1">
              {selectedItems.length} items will be marked as{' '}
              <span className="font-semibold">{decision || '(not selected)'}</span>
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !decision || !notes.trim()}>
            {isSubmitting ? 'Submitting...' : `Review ${selectedItems.length} Items`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default BulkReviewModal;
