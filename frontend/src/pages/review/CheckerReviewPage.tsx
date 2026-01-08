import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { CheckCircle, XCircle, RotateCcw, Clock, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface ReviewItem {
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
  flagged_by?: string;
  created_at?: string;
  notes?: string;
}

const CheckerReviewPage: React.FC = () => {
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [reviewItems, setReviewItems] = useState<ReviewItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchCheckerQueue();
  }, []);

  const fetchCheckerQueue = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get('/review/checker/queue');
      
      if (response.data.success && response.data.queue) {
        setReviewItems(response.data.queue);
      } else {
        setReviewItems([]);
      }
    } catch (error: any) {
      console.error('Error fetching checker queue:', error);
      
      if (error.response?.status !== 404) {
        toast.error('Failed to load checker queue');
      }
      setReviewItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = () => {
    if (!selectedItem) return;
    toast.success(`Case ${selectedItem.id} approved for clearance`);
    setSelectedItem(null);
    setReviewNotes('');
  };

  const handleReject = () => {
    if (!selectedItem) return;
    toast.error(`Case ${selectedItem.id} rejected - escalated to finalizer`);
    setSelectedItem(null);
    setReviewNotes('');
  };

  const handleRecheck = () => {
    if (!selectedItem) return;
    toast.loading(`Case ${selectedItem.id} sent back for re-screening`);
    setSelectedItem(null);
    setReviewNotes('');
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Checker Review</h1>
          <p className="text-muted-foreground">
            Review flagged items and make clearance decisions
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Review Queue */}
          <Card>
            <CardHeader>
              <CardTitle>Pending Review ({reviewItems.length})</CardTitle>
              <CardDescription>Items flagged by screeners</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">
                  Loading queue...
                </div>
              ) : reviewItems.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No items pending review
                </div>
              ) : (
                <div className="space-y-3">
                  {reviewItems.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => setSelectedItem(item)}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedItem?.id === item.id
                          ? 'border-primary bg-primary/5'
                          : 'hover:bg-muted/50'
                      }`}
                    >
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <p className="font-medium">{item.kamco_name}</p>
                          <Badge 
                            variant={
                              item.severity === 'high' || item.severity === 'critical' 
                                ? 'destructive' 
                                : 'secondary'
                            } 
                            className="gap-1"
                          >
                            <AlertTriangle className="h-3 w-3" />
                            {item.match_score}%
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Match: {item.blacklist_name}
                        </p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'}
                          <span>•</span>
                          <span>{item.severity} severity</span>
                          <span>•</span>
                          <span>{item.match_type}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Review Details */}
          <Card>
            <CardHeader>
              <CardTitle>Review Details</CardTitle>
              <CardDescription>
                {selectedItem
                  ? `Case #${selectedItem.id}`
                  : 'Select an item to review'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedItem ? (
                <div className="space-y-6">
                  {/* Match Info */}
                  <div className="space-y-3">
                    <div>
                      <Label>Kamco Entity</Label>
                      <p className="text-sm font-medium mt-1">
                        {selectedItem.kamco_name}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Type: {selectedItem.kamco_type}
                        {selectedItem.kamco_civil_id && ` • Civil ID: ${selectedItem.kamco_civil_id}`}
                      </p>
                    </div>
                    <div>
                      <Label>Blacklist Match</Label>
                      <p className="text-sm font-medium mt-1">
                        {selectedItem.blacklist_name}
                      </p>
                      {selectedItem.blacklist_civil_id && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Civil ID: {selectedItem.blacklist_civil_id}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Match Details</Label>
                      <div className="flex gap-2 mt-1">
                        <Badge variant="outline">{selectedItem.match_score}% match</Badge>
                        <Badge variant="outline">{selectedItem.match_type}</Badge>
                        <Badge variant={
                          selectedItem.severity === 'high' || selectedItem.severity === 'critical'
                            ? 'destructive'
                            : 'secondary'
                        }>
                          {selectedItem.severity} severity
                        </Badge>
                      </div>
                    </div>
                    <div>
                      <Label>Flagged By</Label>
                      <p className="text-sm mt-1">
                        {selectedItem.flagged_by || 'System'}
                      </p>
                    </div>
                    <div>
                      <Label>Screener Notes</Label>
                      <p className="text-sm mt-1">
                        {selectedItem.notes || 'No notes provided'}
                      </p>
                    </div>
                  </div>

                  {/* Checker Notes */}
                  <div className="space-y-2">
                    <Label htmlFor="notes">Your Review Notes</Label>
                    <textarea
                      id="notes"
                      value={reviewNotes}
                      onChange={(e) => setReviewNotes(e.target.value)}
                      className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      placeholder="Add your review notes here..."
                    />
                  </div>

                  {/* Actions */}
                  <div className="space-y-2">
                    <Button
                      onClick={handleApprove}
                      className="w-full"
                      variant="default"
                    >
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Approve Clearance
                    </Button>
                    <Button
                      onClick={handleReject}
                      className="w-full"
                      variant="destructive"
                    >
                      <XCircle className="mr-2 h-4 w-4" />
                      Reject & Escalate
                    </Button>
                    <Button
                      onClick={handleRecheck}
                      className="w-full"
                      variant="outline"
                    >
                      <RotateCcw className="mr-2 h-4 w-4" />
                      Request Re-screening
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-12">
                  Select an item from the queue to begin review
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default CheckerReviewPage;
