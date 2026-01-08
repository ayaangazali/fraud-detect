import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Download, AlertTriangle, CheckCircle, Clock, User, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface ItemDetailReportProps {
  isOpen: boolean;
  onClose: () => void;
  itemId: number;
}

interface DetailedReport {
  item_id: number;
  match_details: {
    match_score: number;
    match_type: string;
    severity: string;
    flagged_at: string;
    flagged_by: string;
  };
  kamco_entity: {
    name: string;
    type: string;
    civil_id?: string;
    details: Record<string, any>;
  };
  blacklist_entry: {
    name_english?: string;
    name_arabic?: string;
    civil_id?: string;
    list_type?: string;
    list_date?: string;
    decree_number?: string;
    decree_date?: string;
  };
  review_status: {
    status: string;
    reviewed_by?: string;
    reviewed_at?: string;
    checker_notes?: string;
    finalizer_notes?: string;
  };
  audit_trail: Array<{
    timestamp: string;
    user: string;
    action: string;
    notes?: string;
  }>;
  risk_assessment: {
    risk_level: string;
    recommended_action: string;
    factors: string[];
  };
}

const ItemDetailReport: React.FC<ItemDetailReportProps> = ({ isOpen, onClose, itemId }) => {
  const [report, setReport] = useState<DetailedReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen && itemId) {
      fetchReport();
    }
  }, [isOpen, itemId]);

  const fetchReport = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get(`/reviews/report/item/${itemId}`);
      if (response.data.success) {
        setReport(response.data.report);
      } else {
        toast.error('Failed to load report');
      }
    } catch (error: any) {
      console.error('Error fetching report:', error);
      toast.error(error.response?.data?.detail || 'Failed to load detailed report');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadReport = () => {
    if (!report) return;
    
    const reportText = JSON.stringify(report, null, 2);
    const blob = new Blob([reportText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `item_${itemId}_report.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Report downloaded');
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

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return <CheckCircle className="h-4 w-4" />;
      case 'rejected':
        return <FileText className="h-4 w-4" />;
      case 'escalated':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle>Detailed Item Report</DialogTitle>
            {report && (
              <Button variant="outline" size="sm" onClick={downloadReport}>
                <Download className="mr-2 h-4 w-4" />
                Download
              </Button>
            )}
          </div>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : report ? (
          <div className="space-y-4">
            {/* Match Details */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Match Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Match Score</span>
                  <Badge variant="outline">{report.match_details.match_score}%</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Match Type</span>
                  <Badge variant="outline">{report.match_details.match_type}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Severity</span>
                  <Badge className={getSeverityColor(report.match_details.severity)}>
                    {report.match_details.severity}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Flagged At</span>
                  <span className="text-sm">{new Date(report.match_details.flagged_at).toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Flagged By</span>
                  <span className="text-sm">{report.match_details.flagged_by}</span>
                </div>
              </CardContent>
            </Card>

            {/* Kamco Entity */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Kamco Entity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Name</span>
                  <span className="text-sm font-medium">{report.kamco_entity.name}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Type</span>
                  <Badge variant="outline">{report.kamco_entity.type}</Badge>
                </div>
                {report.kamco_entity.civil_id && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Civil ID</span>
                    <span className="text-sm font-mono">{report.kamco_entity.civil_id}</span>
                  </div>
                )}
                {Object.keys(report.kamco_entity.details).length > 0 && (
                  <div className="mt-3 pt-3 border-t">
                    <p className="text-sm font-medium mb-2">Additional Details:</p>
                    <div className="space-y-1">
                      {Object.entries(report.kamco_entity.details).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between text-xs">
                          <span className="text-muted-foreground">{key}</span>
                          <span>{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Blacklist Entry */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Blacklist Entry</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {report.blacklist_entry.name_english && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">English Name</span>
                    <span className="text-sm font-medium">{report.blacklist_entry.name_english}</span>
                  </div>
                )}
                {report.blacklist_entry.name_arabic && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Arabic Name</span>
                    <span className="text-sm font-medium">{report.blacklist_entry.name_arabic}</span>
                  </div>
                )}
                {report.blacklist_entry.civil_id && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Civil ID</span>
                    <span className="text-sm font-mono">{report.blacklist_entry.civil_id}</span>
                  </div>
                )}
                {report.blacklist_entry.list_type && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">List Type</span>
                    <Badge variant="outline">{report.blacklist_entry.list_type}</Badge>
                  </div>
                )}
                {report.blacklist_entry.decree_number && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Decree Number</span>
                    <span className="text-sm">{report.blacklist_entry.decree_number}</span>
                  </div>
                )}
                {report.blacklist_entry.decree_date && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Decree Date</span>
                    <span className="text-sm">{report.blacklist_entry.decree_date}</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Review Status */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Review Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <Badge variant="outline" className="gap-1">
                    {getStatusIcon(report.review_status.status)}
                    {report.review_status.status}
                  </Badge>
                </div>
                {report.review_status.reviewed_by && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Reviewed By</span>
                      <span className="text-sm">{report.review_status.reviewed_by}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Reviewed At</span>
                      <span className="text-sm">{new Date(report.review_status.reviewed_at!).toLocaleString()}</span>
                    </div>
                  </>
                )}
                {report.review_status.checker_notes && (
                  <div className="mt-3 pt-3 border-t">
                    <p className="text-sm font-medium mb-1">Checker Notes:</p>
                    <p className="text-sm text-muted-foreground">{report.review_status.checker_notes}</p>
                  </div>
                )}
                {report.review_status.finalizer_notes && (
                  <div className="mt-3 pt-3 border-t">
                    <p className="text-sm font-medium mb-1">Finalizer Notes:</p>
                    <p className="text-sm text-muted-foreground">{report.review_status.finalizer_notes}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Risk Assessment */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Risk Assessment</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Risk Level</span>
                  <Badge className={getSeverityColor(report.risk_assessment.risk_level)}>
                    {report.risk_assessment.risk_level}
                  </Badge>
                </div>
                <div className="mt-3 pt-3 border-t">
                  <p className="text-sm font-medium mb-1">Recommended Action:</p>
                  <p className="text-sm text-muted-foreground">{report.risk_assessment.recommended_action}</p>
                </div>
                {report.risk_assessment.factors.length > 0 && (
                  <div className="mt-3 pt-3 border-t">
                    <p className="text-sm font-medium mb-2">Risk Factors:</p>
                    <ul className="space-y-1">
                      {report.risk_assessment.factors.map((factor, index) => (
                        <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-orange-500 mt-1">•</span>
                          <span>{factor}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Audit Trail */}
            {report.audit_trail.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Audit Trail</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {report.audit_trail.map((entry, index) => (
                      <div key={index} className="flex items-start gap-3 pb-3 border-b last:border-0">
                        <User className="h-4 w-4 text-muted-foreground mt-1" />
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">{entry.action}</span>
                            <span className="text-xs text-muted-foreground">
                              {new Date(entry.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">By: {entry.user}</p>
                          {entry.notes && (
                            <p className="text-sm text-muted-foreground italic">"{entry.notes}"</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No report data available</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default ItemDetailReport;
