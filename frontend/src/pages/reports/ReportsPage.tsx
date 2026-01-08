import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { FileText, Download, TrendingUp, BarChart3 } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface ReportData {
  total_screenings?: number;
  total_matches?: number;
  total_flagged?: number;
  match_rate?: number;
  high_risk_count?: number;
  medium_risk_count?: number;
  low_risk_count?: number;
  pending_review?: number;
  approved?: number;
  rejected?: number;
}

const ReportsPage: React.FC = () => {
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-01-07');
  const [complianceData, setComplianceData] = useState<ReportData | null>(null);
  const [screeningData, setScreeningData] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchReportData();
  }, []);

  const fetchReportData = async () => {
    setIsLoading(true);
    try {
      // Fetch multiple report types
      const [complianceRes, screeningRes] = await Promise.all([
        apiClient.get('/reports/compliance'),
        apiClient.get('/reports/screening-summary'),
      ]);

      if (complianceRes.data.success) {
        setComplianceData(complianceRes.data.data);
      }
      
      if (screeningRes.data.success) {
        setScreeningData(screeningRes.data.data);
      }
    } catch (error: any) {
      console.error('Error fetching report data:', error);
      
      if (error.response?.status !== 403) {
        toast.error('Failed to load report data');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    try {
      toast('Generating PDF report...', { icon: '📄' });
      // TODO: Call generate endpoint with PDF format
      // await apiClient.post('/reports/generate', { report_type: 'compliance_audit', report_format: 'pdf' });
      toast.success('PDF report will be ready soon');
    } catch (error) {
      toast.error('Failed to generate PDF');
    }
  };

  const handleGenerateExcel = async () => {
    try {
      toast('Generating Excel report...', { icon: '📊' });
      // TODO: Call generate endpoint with Excel format
      toast.success('Excel report will be ready soon');
    } catch (error) {
      toast.error('Failed to generate Excel');
    }
  };

  const handleGenerateCSV = async () => {
    try {
      toast('Generating CSV report...', { icon: '📋' });
      // TODO: Call generate endpoint with CSV format
      toast.success('CSV report will be ready soon');
    } catch (error) {
      toast.error('Failed to generate CSV');
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Reports & Analytics</h1>
            <p className="text-muted-foreground">
              Generate and download compliance reports
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleGeneratePDF} variant="outline">
              <FileText className="mr-2 h-4 w-4" />
              Generate PDF
            </Button>
            <Button onClick={handleGenerateExcel} variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Generate Excel
            </Button>
            <Button onClick={handleGenerateCSV} variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Generate CSV
            </Button>
          </div>
        </div>

        {/* Date Range Filter */}
        <Card>
          <CardHeader>
            <CardTitle>Report Period</CardTitle>
            <CardDescription>Select date range for reports</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start-date">Start Date</Label>
                <Input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end-date">End Date</Label>
                <Input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
            </div>
            <Button onClick={fetchReportData} className="mt-4">
              <TrendingUp className="mr-2 h-4 w-4" />
              Refresh Data
            </Button>
          </CardContent>
        </Card>

        {isLoading ? (
          <div className="text-center py-12 text-muted-foreground">
            Loading report data...
          </div>
        ) : (
          <>
            {/* Summary Statistics */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Screenings</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {screeningData?.total_screenings || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    +{screeningData?.total_matches || 0} matches found
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Flagged Items</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {screeningData?.total_flagged || complianceData?.total_flagged || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Requires review
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Match Rate</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {screeningData?.match_rate || 0}%
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Of all screenings
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">High Risk</CardTitle>
                  <FileText className="h-4 w-4 text-red-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">
                    {complianceData?.high_risk_count || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Critical items
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Detailed Reports */}
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Screening Summary</CardTitle>
                  <CardDescription>Breakdown of screening results</CardDescription>
                </CardHeader>
                <CardContent>
                  {screeningData ? (
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Total Screenings:</span>
                        <span className="font-medium">{screeningData.total_screenings}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Total Matches:</span>
                        <span className="font-medium">{screeningData.total_matches}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Match Rate:</span>
                        <span className="font-medium">{screeningData.match_rate}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Total Flagged:</span>
                        <span className="font-medium text-red-600">{screeningData.total_flagged}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      No screening data available
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Risk Assessment</CardTitle>
                  <CardDescription>Risk level distribution</CardDescription>
                </CardHeader>
                <CardContent>
                  {complianceData ? (
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">High Risk:</span>
                        <span className="font-medium text-red-600">{complianceData.high_risk_count || 0}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Medium Risk:</span>
                        <span className="font-medium text-orange-600">{complianceData.medium_risk_count || 0}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Low Risk:</span>
                        <span className="font-medium text-yellow-600">{complianceData.low_risk_count || 0}</span>
                      </div>
                      <div className="border-t pt-4 mt-4">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Pending Review:</span>
                          <span className="font-medium">{complianceData.pending_review || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Approved:</span>
                          <span className="font-medium text-green-600">{complianceData.approved || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Rejected:</span>
                          <span className="font-medium text-red-600">{complianceData.rejected || 0}</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      No compliance data available
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </MainLayout>
  );
};

export default ReportsPage;
