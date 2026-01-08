import React, { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface ReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: {
    id: number;
    kamco_name: string;
    kamco_type: string;
    kamco_civil_id?: string;
    blacklist_name: string;
    blacklist_civil_id?: string;
    match_score: number;
    match_type: string;
    severity: string;
    status: string;
  };
  onReviewComplete?: () => void;
}

type ReviewDecision = 'approved' | 'rejected' | 'escalated';

const ReviewModal: React.FC<ReviewModalProps> = ({ isOpen, onClose, item, onReviewComplete }) => {
  const [decision, setDecision] = useState<ReviewDecision | null>(null);
  const [notes, setNotes] = useState('');
  const [escalationReason, setEscalationReason] = useState('');
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

    if (decision === 'escalated' && !escalationReason.trim()) {
      toast.error('Please provide an escalation reason');
      return;
    }

    setIsSubmitting(true);

    try {
      const payload: any = {
        decision,
        notes: notes.trim(),
      };

      if (decision === 'escalated') {
        payload.escalate_to_finalizer = true;
        payload.escalation_notes = escalationReason.trim();
      }

      const response = await apiClient.post(`/reviews/review/${item.id}`, payload);

      if (response.data.success) {
        toast.success(`Item ${decision} successfully`);
        onReviewComplete?.();
        handleClose();
      } else {
        toast.error(response.data.message || 'Review submission failed');
      }
    } catch (error: any) {
      console.error('Error submitting review:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit review');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setDecision(null);
    setNotes('');
    setEscalationReason('');
    onClose();
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
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

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Review Flagged Item</DialogTitle>
          <DialogDescription>
            Review the match details and make a decision
          </DialogDescription>
        </DialogHeader>

        {/* Item Details */}
        <div className="space-y-4">
          {/* Match Information */}
          <div className="p-4 bg-muted rounded-lg space-y-3">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Kamco Entity</p>
                <p className="font-semibold">{item.kamco_name}</p>
                <p className="text-sm text-muted-foreground">
                  {item.kamco_type} {item.kamco_civil_id && `• Civil ID: ${item.kamco_civil_id}`}
                </p>
              </div>
              <Badge className={getSeverityColor(item.severity)}>
                {item.severity.toUpperCase()}
              </Badge>
            </div>

            <div className="flex items-center justify-center py-2">
              <div className="flex items-center gap-2">
                <div className="h-px w-12 bg-border" />
                <span className="text-sm font-medium">
                  {item.match_score}% Match
                </span>
                <div className="h-px w-12 bg-border" />
              </div>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Blacklist Entry</p>
              <p className="font-semibold">{item.blacklist_name}</p>
              <p className="text-sm text-muted-foreground">
                {item.match_type} {item.blacklist_civil_id && `• Civil ID: ${item.blacklist_civil_id}`}
              </p>
            </div>
          </div>

          {/* Decision Buttons */}
          <div className="space-y-2">
            <Label>Decision *</Label>
            <div className="grid grid-cols-3 gap-3">
              <Button
                type="button"
                variant={decision === 'approved' ? 'default' : 'outline'}
                className={decision === 'approved' ? 'bg-green-600 hover:bg-green-700' : ''}
                onClick={() => setDecision('approved')}
              >
                <CheckCircle className="mr-2 h-4 w-4" />
                Approve
              </Button>
              <Button
                type="button"
                variant={decision === 'rejected' ? 'default' : 'outline'}
                className={decision === 'rejected' ? 'bg-red-600 hover:bg-red-700' : ''}
                onClick={() => setDecision('rejected')}
              >
                <XCircle className="mr-2 h-4 w-4" />
                Reject
              </Button>
              <Button
                type="button"
                variant={decision === 'escalated' ? 'default' : 'outline'}
                className={decision === 'escalated' ? 'bg-orange-600 hover:bg-orange-700' : ''}
                onClick={() => setDecision('escalated')}
              >
                <AlertTriangle className="mr-2 h-4 w-4" />
                Escalate
              </Button>
            </div>
          </div>

          {/* Decision Guidance */}
          {decision && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="text-sm">
                  {decision === 'approved' && (
                    <>
                      <p className="font-medium text-blue-900">Approve: Confirm Match</p>
                      <p className="text-blue-700 mt-1">
                        This entity matches the blacklist entry. Document the reason and any additional context.
                      </p>
                    </>
                  )}
                  {decision === 'rejected' && (
                    <>
                      <p className="font-medium text-blue-900">Reject: False Positive</p>
                      <p className="text-blue-700 mt-1">
                        This is not a true match. Explain why this is a false positive (e.g., different person, common name).
                      </p>
                    </>
                  )}
                  {decision === 'escalated' && (
                    <>
                      <p className="font-medium text-blue-900">Escalate: Needs Senior Review</p>
                      <p className="text-blue-700 mt-1">
                        This case requires additional expertise. Provide detailed context for the finalizer.
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Review Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Review Notes *</Label>
            <Textarea
              id="notes"
              placeholder="Enter your review notes here... (e.g., Match confirmed based on Civil ID match and similar name. Verified against source document.)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground">
              Provide detailed reasoning for your decision. This will be logged for audit purposes.
            </p>
          </div>

          {/* Escalation Reason (only if escalated) */}
          {decision === 'escalated' && (
            <div className="space-y-2">
              <Label htmlFor="escalation">Escalation Reason *</Label>
              <Textarea
                id="escalation"
                placeholder="Why does this case need escalation? (e.g., Complex case with multiple partial matches. Need senior analyst review of source documents.)"
                value={escalationReason}
                onChange={(e) => setEscalationReason(e.target.value)}
                rows={3}
                className="resize-none"
              />
              <p className="text-xs text-muted-foreground">
                Explain why this requires finalizer review. Admins will be notified automatically.
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !decision || !notes.trim()}>
            {isSubmitting ? 'Submitting...' : 'Submit Review'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ReviewModal;
