import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Download, Mail, BarChart3, TrendingUp, Users, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface CumulativeReportProps {
  isOpen: boolean;
  onClose: () => void;
  onEmailReport?: () => void;
}

interface CumulativeReportData {
  summary: {
    total_items: number;
    pending: number;
    approved: number;
    rejected: number;
    escalated: number;
    approval_rate: number;
    rejection_rate: number;
  };
  by_severity: Record<string, number>;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  top_matches: Array<{
    id: number;
    kamco_name: string;
    blacklist_name: string;
    match_score: number;
    severity: string;
  }>;
  reviewer_stats?: Array<{
    reviewer: string;
    reviewed: number;
    approved: number;
    rejected: number;
    escalated: number;
  }>;
}

const CumulativeReport: React.FC<CumulativeReportProps> = ({ isOpen, onClose, onEmailReport }) => {
  const [report, setReport] = useState<CumulativeReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchReport();
    }
  }, [isOpen]);

  const fetchReport = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get('/reviews/report/cumulative');
      if (response.data.success && response.data.data) {
        // Map backend response to frontend expected format
        const backendData = response.data.data;
        const mappedReport: CumulativeReportData = {
          summary: {
            total_items: backendData.summary?.total_flagged_items || 0,
            pending: backendData.summary?.total_pending || 0,
            approved: backendData.summary?.total_approved || 0,
            rejected: backendData.summary?.total_rejected || 0,
            escalated: backendData.summary?.total_escalated || 0,
            approval_rate: backendData.summary?.approval_rate || 0,
            rejection_rate: backendData.summary?.rejection_rate || 0,
          },
          by_severity: backendData.breakdowns?.by_severity || {},
          by_type: backendData.breakdowns?.by_entity_type || {},
          by_status: backendData.breakdowns?.by_status || {},
          top_matches: backendData.top_matches || [],
          reviewer_stats: backendData.reviewer_stats?.map((r: any) => ({
            reviewer: r.reviewer_name,
            reviewed: r.items_reviewed,
            approved: 0,
            rejected: 0,
            escalated: 0,
          })) || [],
        };
        setReport(mappedReport);
      } else {
        toast.error('Failed to load cumulative report');
      }
    } catch (error: any) {
      console.error('Error fetching cumulative report:', error);
      // Handle error object properly
      let errorMessage = 'Failed to load cumulative report';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (typeof detail === 'object') {
          errorMessage = detail.msg || JSON.stringify(detail);
        }
      }
      toast.error(errorMessage);
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
    a.download = `cumulative_report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Report downloaded');
  };

  const getPercentageColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Cumulative Screening Report
            </DialogTitle>
            <div className="flex gap-2">
              {onEmailReport && (
                <Button variant="outline" size="sm" onClick={onEmailReport}>
                  <Mail className="mr-2 h-4 w-4" />
                  Email
                </Button>
              )}
              {report && (
                <Button variant="outline" size="sm" onClick={downloadReport}>
                  <Download className="mr-2 h-4 w-4" />
                  Download
                </Button>
              )}
            </div>
          </div>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : report ? (
          <div className="space-y-6">
            {/* Executive Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Executive Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Total Items</p>
                    <p className="text-2xl font-bold">{report.summary.total_items}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Pending</p>
                    <p className="text-2xl font-bold text-orange-600">{report.summary.pending}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Approved</p>
                    <p className="text-2xl font-bold text-green-600">{report.summary.approved}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Rejected</p>
                    <p className="text-2xl font-bold text-red-600">{report.summary.rejected}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Approval Rate</p>
                    <p className={`text-xl font-semibold ${getPercentageColor(report.summary.approval_rate)}`}>
                      {report.summary.approval_rate.toFixed(1)}%
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Rejection Rate</p>
                    <p className={`text-xl font-semibold ${getPercentageColor(100 - report.summary.approval_rate)}`}>
                      {report.summary.rejection_rate.toFixed(1)}%
                    </p>
                  </div>
                </div>

                {report.summary.escalated > 0 && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-lg">
                      <AlertTriangle className="h-5 w-5 text-orange-600" />
                      <div>
                        <p className="text-sm font-medium">
                          {report.summary.escalated} item{report.summary.escalated > 1 ? 's' : ''} escalated
                        </p>
                        <p className="text-xs text-muted-foreground">Requires finalizer review</p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="grid md:grid-cols-2 gap-6">
              {/* By Severity */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">By Severity</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {Object.entries(report.by_severity).map(([severity, count]) => (
                    <div key={severity} className="flex items-center justify-between">
                      <Badge className={getSeverityColor(severity)}>
                        {severity}
                      </Badge>
                      <span className="text-lg font-semibold">{count}</span>
                    </div>
                  ))}
                  {Object.keys(report.by_severity).length === 0 && (
                    <p className="text-sm text-muted-foreground text-center py-4">No data available</p>
                  )}
                </CardContent>
              </Card>

              {/* By Type */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">By Entity Type</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {Object.entries(report.by_type).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <Badge variant="outline">{type}</Badge>
                      <span className="text-lg font-semibold">{count}</span>
                    </div>
                  ))}
                  {Object.keys(report.by_type).length === 0 && (
                    <p className="text-sm text-muted-foreground text-center py-4">No data available</p>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Top Matches */}
            {report.top_matches.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Top Matches</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {report.top_matches.map((match) => (
                      <div key={match.id} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium text-sm">{match.kamco_name}</p>
                          <p className="text-xs text-muted-foreground">→ {match.blacklist_name}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge className={getSeverityColor(match.severity)}>
                            {match.severity}
                          </Badge>
                          <Badge variant="outline">{match.match_score}%</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Reviewer Performance */}
            {report.reviewer_stats && report.reviewer_stats.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Reviewer Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {report.reviewer_stats.map((stat, index) => (
                      <div key={index} className="p-3 bg-muted rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <p className="font-medium">{stat.reviewer}</p>
                          <Badge variant="outline">{stat.reviewed} reviewed</Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-sm">
                          <div className="text-center">
                            <p className="text-green-600 font-semibold">{stat.approved}</p>
                            <p className="text-xs text-muted-foreground">Approved</p>
                          </div>
                          <div className="text-center">
                            <p className="text-red-600 font-semibold">{stat.rejected}</p>
                            <p className="text-xs text-muted-foreground">Rejected</p>
                          </div>
                          <div className="text-center">
                            <p className="text-orange-600 font-semibold">{stat.escalated}</p>
                            <p className="text-xs text-muted-foreground">Escalated</p>
                          </div>
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

export default CumulativeReport;
