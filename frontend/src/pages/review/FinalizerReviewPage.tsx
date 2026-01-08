import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { CheckCircle, XCircle, AlertTriangle, User } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface FinalReviewItem {
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
  reviewed_by?: string;
  reviewed_at?: string;
  notes?: string;
  escalated: boolean;
}

const FinalizerReviewPage: React.FC = () => {
  const [selectedItem, setSelectedItem] = useState<FinalReviewItem | null>(null);
  const [finalNotes, setFinalNotes] = useState('');
  const [reviewItems, setReviewItems] = useState<FinalReviewItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchFinalizerQueue();
  }, []);

  const fetchFinalizerQueue = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get('/review/finalizer/queue');
      
      if (response.data.success && response.data.queue) {
        setReviewItems(response.data.queue);
      } else {
        setReviewItems([]);
      }
    } catch (error: any) {
      console.error('Error fetching finalizer queue:', error);
      
      if (error.response?.status !== 404) {
        toast.error('Failed to load finalizer queue');
      }
      setReviewItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFinalApprove = () => {
    if (!selectedItem) return;
    toast.success(`Case ${selectedItem.id} finally approved and cleared`);
    setSelectedItem(null);
    setFinalNotes('');
  };

  const handleFinalReject = () => {
    if (!selectedItem) return;
    toast.error(`Case ${selectedItem.id} finally rejected - customer blocked`);
    setSelectedItem(null);
    setFinalNotes('');
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Finalizer Review</h1>
          <p className="text-muted-foreground">
            Make final decisions on escalated cases
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Escalated Cases */}
          <Card>
            <CardHeader>
              <CardTitle>Escalated Cases ({reviewItems.length})</CardTitle>
              <CardDescription>Items requiring final approval</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">
                  Loading queue...
                </div>
              ) : reviewItems.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No cases requiring final review
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
                          <Badge variant="destructive" className="gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            {item.severity}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Match: {item.blacklist_name} ({item.match_score}%)
                        </p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <User className="h-3 w-3" />
                          {item.escalated ? 'Escalated' : 'High Severity'}
                          {item.reviewed_by && ` by ${item.reviewed_by}`}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Final Review Details */}
          <Card>
            <CardHeader>
              <CardTitle>Final Review</CardTitle>
              <CardDescription>
                {selectedItem
                  ? `Case #${selectedItem.id} - Executive Decision`
                  : 'Select a case to review'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedItem ? (
                <div className="space-y-6">
                  {/* Case Details */}
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
                      <div className="flex flex-wrap gap-2 mt-1">
                        <Badge variant="outline">{selectedItem.match_score}% match</Badge>
                        <Badge variant="outline">{selectedItem.match_type}</Badge>
                        <Badge variant="destructive">{selectedItem.severity} severity</Badge>
                        {selectedItem.escalated && <Badge variant="destructive">ESCALATED</Badge>}
                      </div>
                    </div>
                    
                    <div className="border-t pt-3 mt-3">
                      <Label className="text-base">Review History</Label>
                      <div className="space-y-2 mt-2">
                        <div className="flex flex-col gap-1 text-sm">
                          <div className="flex items-center gap-2">
                            <span className="text-muted-foreground">Flagged by:</span>
                            <span>{selectedItem.flagged_by || 'System'}</span>
                          </div>
                          {selectedItem.created_at && (
                            <span className="text-xs text-muted-foreground">
                              {new Date(selectedItem.created_at).toLocaleString()}
                            </span>
                          )}
                        </div>
                        {selectedItem.reviewed_by && (
                          <div className="flex flex-col gap-1 text-sm">
                            <div className="flex items-center gap-2">
                              <span className="text-muted-foreground">Reviewed by:</span>
                              <span>{selectedItem.reviewed_by}</span>
                            </div>
                            {selectedItem.reviewed_at && (
                              <span className="text-xs text-muted-foreground">
                                {new Date(selectedItem.reviewed_at).toLocaleString()}
                              </span>
                            )}
                          </div>
                        )}
                        {selectedItem.escalated && (
                          <div className="pt-2">
                            <Badge variant="destructive" className="text-xs">
                              ⚠️ Escalated to Finalizer
                            </Badge>
                          </div>
                        )}
                      </div>
                    </div>

                    <div>
                      <Label>Previous Notes</Label>
                      <p className="text-sm mt-1 text-muted-foreground">
                        {selectedItem.notes || 'No previous notes'}
                      </p>
                    </div>
                  </div>

                  {/* Final Decision Notes */}
                  <div className="space-y-2">
                    <Label htmlFor="final-notes">Your Final Decision Notes</Label>
                    <textarea
                      id="final-notes"
                      value={finalNotes}
                      onChange={(e) => setFinalNotes(e.target.value)}
                      className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      placeholder="Document your final decision..."
                    />
                  </div>

                  {/* Final Actions */}
                  <div className="space-y-2">
                    <Button
                      onClick={handleFinalApprove}
                      className="w-full"
                      variant="default"
                    >
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Final Approval - Clear Customer
                    </Button>
                    <Button
                      onClick={handleFinalReject}
                      className="w-full"
                      variant="destructive"
                    >
                      <XCircle className="mr-2 h-4 w-4" />
                      Final Rejection - Block Customer
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-12">
                  Select a case from the escalated queue to review
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default FinalizerReviewPage;
