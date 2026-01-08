import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Search,
  Filter,
  Download,
  Shield,
  AlertTriangle,
  Info,
  CheckCircle,
  Clock,
  User,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface AuditLog {
  id: number;
  timestamp: string;
  user: string;
  role: string;
  action: string;
  resource: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  details: string;
  ipAddress: string;
}

const AuditLogsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-01-07');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');

  // Mock audit logs
  const auditLogs: AuditLog[] = [
    {
      id: 1,
      timestamp: '2026-01-07 14:32:15',
      user: 'finalizer_john',
      role: 'Finalizer',
      action: 'USER_LOGIN',
      resource: 'Authentication',
      severity: 'success',
      details: 'Successful login from known location',
      ipAddress: '192.168.1.100',
    },
    {
      id: 2,
      timestamp: '2026-01-07 14:28:43',
      user: 'screener_bob',
      role: 'Screener',
      action: 'FILE_UPLOAD',
      resource: 'Customer Data',
      severity: 'info',
      details: 'Uploaded customer file: customers_2026_01.xlsx',
      ipAddress: '192.168.1.105',
    },
    {
      id: 3,
      timestamp: '2026-01-07 14:15:22',
      user: 'checker_jane',
      role: 'Checker',
      action: 'CASE_APPROVED',
      resource: 'Case #1234',
      severity: 'success',
      details: 'Approved clearance for John Smith',
      ipAddress: '192.168.1.110',
    },
    {
      id: 4,
      timestamp: '2026-01-07 13:45:18',
      user: 'unknown_user',
      role: 'N/A',
      action: 'LOGIN_FAILED',
      resource: 'Authentication',
      severity: 'warning',
      details: 'Failed login attempt - invalid credentials',
      ipAddress: '203.0.113.42',
    },
    {
      id: 5,
      timestamp: '2026-01-07 12:30:05',
      user: 'finalizer_mike',
      role: 'Finalizer',
      action: 'CASE_REJECTED',
      resource: 'Case #1235',
      severity: 'error',
      details: 'Final rejection - customer blocked',
      ipAddress: '192.168.1.115',
    },
  ];

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'success':
        return <CheckCircle className="h-4 w-4" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />;
      case 'error':
        return <Shield className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'success':
        return 'default';
      case 'warning':
        return 'secondary';
      case 'error':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const handleExportCSV = () => {
    toast.success('Audit log exported to CSV');
  };

  const filteredLogs = auditLogs.filter((log) => {
    const matchesSearch =
      searchQuery === '' ||
      log.user.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.action.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity =
      selectedSeverity === 'all' || log.severity === selectedSeverity;
    return matchesSearch && matchesSeverity;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Audit Logs</h1>
            <p className="text-muted-foreground">
              Monitor system activity and security events
            </p>
          </div>
          <Button onClick={handleExportCSV}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>

        {/* Security Dashboard */}
        <div className="grid md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">5,234</div>
              <p className="text-xs text-muted-foreground mt-1">Last 7 days</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Security Warnings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">12</div>
              <p className="text-xs text-muted-foreground mt-1">Requires attention</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Failed Logins</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">8</div>
              <p className="text-xs text-muted-foreground mt-1">Last 24 hours</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Active Users</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-muted-foreground mt-1">Currently online</p>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Filters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label htmlFor="search">Search</Label>
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    placeholder="User or action..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-8"
                  />
                </div>
              </div>
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
              <div className="space-y-2">
                <Label htmlFor="severity">Severity</Label>
                <select
                  id="severity"
                  value={selectedSeverity}
                  onChange={(e) => setSelectedSeverity(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="all">All Severities</option>
                  <option value="success">Success</option>
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Audit Log Table */}
        <Card>
          <CardHeader>
            <CardTitle>Activity Timeline ({filteredLogs.length} events)</CardTitle>
            <CardDescription>Chronological system activity log</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {filteredLogs.map((log) => (
                <div
                  key={log.id}
                  className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-3">
                        <Badge
                          variant={getSeverityColor(log.severity)}
                          className="gap-1"
                        >
                          {getSeverityIcon(log.severity)}
                          {log.severity}
                        </Badge>
                        <span className="font-medium">{log.action}</span>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-sm text-muted-foreground">
                          {log.resource}
                        </span>
                      </div>
                      <p className="text-sm">{log.details}</p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {log.timestamp}
                        </span>
                        <span className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          {log.user} ({log.role})
                        </span>
                        <span>IP: {log.ipAddress}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
};

export default AuditLogsPage;
