import React, { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Mail, Plus, X } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface EmailReportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const EmailReportModal: React.FC<EmailReportModalProps> = ({ isOpen, onClose }) => {
  const [recipients, setRecipients] = useState<string[]>(['']);
  const [includeSummary, setIncludeSummary] = useState(true);
  const [includeIndividual, setIncludeIndividual] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const handleAddRecipient = () => {
    setRecipients([...recipients, '']);
  };

  const handleRemoveRecipient = (index: number) => {
    if (recipients.length > 1) {
      setRecipients(recipients.filter((_, i) => i !== index));
    }
  };

  const handleRecipientChange = (index: number, value: string) => {
    const newRecipients = [...recipients];
    newRecipients[index] = value;
    setRecipients(newRecipients);
  };

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSend = async () => {
    // Validate recipients
    const validRecipients = recipients.filter(r => r.trim() !== '');
    
    if (validRecipients.length === 0) {
      toast.error('Please add at least one recipient');
      return;
    }

    const invalidEmails = validRecipients.filter(r => !validateEmail(r));
    if (invalidEmails.length > 0) {
      toast.error('Please enter valid email addresses');
      return;
    }

    if (!includeSummary && !includeIndividual) {
      toast.error('Please select at least one report type to include');
      return;
    }

    setIsSending(true);

    try {
      const response = await apiClient.post('/reviews/email/report', {
        recipients: validRecipients,
        include_summary: includeSummary,
        include_individual_reports: includeIndividual,
      });

      if (response.data.success) {
        toast.success(`Report sent to ${validRecipients.length} recipient${validRecipients.length > 1 ? 's' : ''}`);
        handleClose();
      } else {
        toast.error(response.data.message || 'Failed to send email');
      }
    } catch (error: any) {
      console.error('Error sending email:', error);
      toast.error(error.response?.data?.detail || 'Failed to send email report');
    } finally {
      setIsSending(false);
    }
  };

  const handleClose = () => {
    setRecipients(['']);
    setIncludeSummary(true);
    setIncludeIndividual(false);
    onClose();
  };

  // Predefined recipient groups
  const recipientGroups = [
    {
      name: 'Compliance Team',
      emails: ['compliance@kamcoinvest.com'],
    },
    {
      name: 'Risk Management',
      emails: ['risk@kamcoinvest.com'],
    },
    {
      name: 'Management',
      emails: ['management@kamcoinvest.com'],
    },
  ];

  const addRecipientGroup = (emails: string[]) => {
    const newRecipients = [...recipients];
    // Remove empty entries
    const filtered = newRecipients.filter(r => r.trim() !== '');
    // Add new emails if not already present
    emails.forEach(email => {
      if (!filtered.includes(email)) {
        filtered.push(email);
      }
    });
    setRecipients(filtered.length > 0 ? filtered : ['']);
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Email Screening Report
          </DialogTitle>
          <DialogDescription>
            Send the screening report to compliance and management teams
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Quick Add Groups */}
          <div className="space-y-2">
            <Label>Quick Add Recipient Groups</Label>
            <div className="flex flex-wrap gap-2">
              {recipientGroups.map((group) => (
                <Button
                  key={group.name}
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => addRecipientGroup(group.emails)}
                >
                  <Plus className="mr-1 h-3 w-3" />
                  {group.name}
                </Button>
              ))}
            </div>
          </div>

          {/* Recipients */}
          <div className="space-y-2">
            <Label>Recipients *</Label>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {recipients.map((recipient, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    type="email"
                    placeholder="email@example.com"
                    value={recipient}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                      handleRecipientChange(index, e.target.value)
                    }
                    className={
                      recipient && !validateEmail(recipient) ? 'border-red-500' : ''
                    }
                  />
                  {recipients.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveRecipient(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAddRecipient}
              className="w-full"
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Recipient
            </Button>
          </div>

          {/* Report Options */}
          <div className="space-y-3">
            <Label>Report Contents *</Label>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="summary"
                checked={includeSummary}
                onCheckedChange={(checked) => setIncludeSummary(checked as boolean)}
              />
              <Label htmlFor="summary" className="font-normal cursor-pointer">
                Include Executive Summary
              </Label>
            </div>
            <p className="text-xs text-muted-foreground ml-6">
              Overall statistics and breakdowns (recommended)
            </p>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="individual"
                checked={includeIndividual}
                onCheckedChange={(checked) => setIncludeIndividual(checked as boolean)}
              />
              <Label htmlFor="individual" className="font-normal cursor-pointer">
                Include Individual Item Reports
              </Label>
            </div>
            <p className="text-xs text-muted-foreground ml-6">
              Detailed reports for each flagged item (may be large for many items)
            </p>
          </div>

          {/* Preview */}
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium mb-2">Email Preview:</p>
            <div className="space-y-1 text-xs text-muted-foreground">
              <p>
                <strong>To:</strong>{' '}
                {recipients.filter(r => r.trim() !== '').length > 0
                  ? recipients.filter(r => r.trim() !== '').join(', ')
                  : 'No recipients'}
              </p>
              <p>
                <strong>Subject:</strong> Kamco Screening Report - {new Date().toLocaleDateString()}
              </p>
              <p>
                <strong>Includes:</strong>{' '}
                {includeSummary && includeIndividual
                  ? 'Summary + Individual Reports'
                  : includeSummary
                  ? 'Summary Only'
                  : includeIndividual
                  ? 'Individual Reports Only'
                  : 'None selected'}
              </p>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={isSending}>
            Cancel
          </Button>
          <Button onClick={handleSend} disabled={isSending}>
            <Mail className="mr-2 h-4 w-4" />
            {isSending ? 'Sending...' : 'Send Report'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default EmailReportModal;
