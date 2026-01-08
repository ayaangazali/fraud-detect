import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { FileText, Download, Calendar, TrendingUp } from 'lucide-react';
import toast from 'react-hot-toast';

const ReportsPage: React.FC = () => {
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-01-07');

  // Mock data for charts
  const screeningTrends = [
    { date: 'Jan 1', screenings: 320, flagged: 45 },
    { date: 'Jan 2', screenings: 298, flagged: 38 },
    { date: 'Jan 3', screenings: 405, flagged: 52 },
    { date: 'Jan 4', screenings: 378, flagged: 41 },
    { date: 'Jan 5', screenings: 442, flagged: 58 },
    { date: 'Jan 6', screenings: 391, flagged: 47 },
    { date: 'Jan 7', screenings: 456, flagged: 61 },
  ];

  const statusData = [
    { name: 'Approved', value: 2189, color: '#10b981' },
    { name: 'Flagged', value: 127, color: '#ef4444' },
    { name: 'Pending', value: 227, color: '#f59e0b' },
  ];

  const performanceData = [
    { role: 'Screeners', processed: 2543 },
    { role: 'Checkers', processed: 354 },
    { role: 'Finalizers', processed: 127 },
  ];

  const handleGeneratePDF = () => {
    toast.success('PDF report generated successfully!');
  };

  const handleGenerateExcel = () => {
    toast.success('Excel report generated successfully!');
  };

  const handleGenerateCSV = () => {
    toast.success('CSV export generated successfully!');
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Reports & Analytics</h1>
            <p className="text-muted-foreground">
              View screening statistics and generate compliance reports
            </p>
          </div>
          <Button>
            <FileText className="mr-2 h-4 w-4" />
            New Report
          </Button>
        </div>

        {/* Date Range Filter */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Report Parameters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
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
              <div className="flex items-end gap-2">
                <Button onClick={handleGeneratePDF} className="flex-1">
                  <Download className="mr-2 h-4 w-4" />
                  PDF
                </Button>
                <Button onClick={handleGenerateExcel} variant="outline" className="flex-1">
                  <Download className="mr-2 h-4 w-4" />
                  Excel
                </Button>
                <Button onClick={handleGenerateCSV} variant="outline" className="flex-1">
                  <Download className="mr-2 h-4 w-4" />
                  CSV
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Key Metrics */}
        <div className="grid md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Screenings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">2,543</div>
              <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                <TrendingUp className="h-3 w-3 text-green-600" />
                +12.5% from last period
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Flagged Items</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">127</div>
              <p className="text-xs text-muted-foreground mt-1">5.0% of total</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Approved</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">2,189</div>
              <p className="text-xs text-muted-foreground mt-1">86.1% of total</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Avg Processing Time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">4.2h</div>
              <p className="text-xs text-muted-foreground mt-1">Per case</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Screening Trends */}
          <Card>
            <CardHeader>
              <CardTitle>Screening Trends</CardTitle>
              <CardDescription>Daily screening and flagging activity</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={screeningTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="screenings"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    name="Total Screenings"
                  />
                  <Line
                    type="monotone"
                    dataKey="flagged"
                    stroke="#ef4444"
                    strokeWidth={2}
                    name="Flagged Items"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Status Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Status Distribution</CardTitle>
              <CardDescription>Current case status breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name}: ${((percent || 0) * 100).toFixed(0)}%`
                    }
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Team Performance */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Team Performance</CardTitle>
              <CardDescription>Cases processed by role</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="role" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="processed" fill="#3b82f6" name="Cases Processed" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Recent Reports */}
        <Card>
          <CardHeader>
            <CardTitle>Report History</CardTitle>
            <CardDescription>Previously generated reports</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                {
                  name: 'Weekly Compliance Report',
                  date: '2026-01-07',
                  format: 'PDF',
                },
                {
                  name: 'Monthly Screening Summary',
                  date: '2026-01-01',
                  format: 'Excel',
                },
                {
                  name: 'Audit Trail Export',
                  date: '2025-12-31',
                  format: 'CSV',
                },
              ].map((report, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium">{report.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {report.date} • {report.format}
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
};

export default ReportsPage;
