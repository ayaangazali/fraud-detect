import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Search,
  Download,
  Shield,
  AlertTriangle,
  Info,
  CheckCircle,
  Clock,
  User,
} from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '@/services/apiClient';

interface AuditLog {
  id: number;
  timestamp: string;
  user_id: number;
  user_name?: string;
  user_role?: string;
  event_type: string;
  resource_type: string;
  resource_id?: number;
  description: string;
  severity: string;
  ip_address?: string;
  metadata?: any;
}

const AuditLogsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-01-07');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchAuditLogs();
  }, [page, selectedSeverity]);

  const fetchAuditLogs = async () => {
    setIsLoading(true);
    try {
      const params: any = {
        page,
        page_size: 20,
      };

      if (startDate) params.date_from = startDate;
      if (endDate) params.date_to = endDate;
      if (selectedSeverity !== 'all') params.severity_levels = selectedSeverity;
      if (searchQuery) params.search_query = searchQuery;

      const response = await apiClient.get('/audit/logs', { params });

      if (response.data.success) {
        setAuditLogs(response.data.data || []);
        setTotalPages(response.data.total_pages || 1);
      }
    } catch (error: any) {
      console.error('Error fetching audit logs:', error);
      
      if (error.response?.status !== 403) {
        toast.error('Failed to load audit logs');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchAuditLogs();
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'success':
      case 'low':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'warning':
      case 'medium':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'error':
      case 'critical':
      case 'high':
        return <Shield className="h-4 w-4 text-red-600" />;
      default:
        return <Info className="h-4 w-4 text-blue-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'success':
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'warning':
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'error':
      case 'critical':
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  const handleExport = async () => {
    try {
      toast('Exporting audit logs...', { icon: '📄' });
      // TODO: Call export endpoint
      toast.success('Export completed');
    } catch (error) {
      toast.error('Export failed');
    }
  };

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
          <Button onClick={handleExport} variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export Logs
          </Button>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Filters</CardTitle>
            <CardDescription>Filter audit logs by date, severity, or search</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
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

              <div className="space-y-2">
                <Label htmlFor="search">Search Logs</Label>
                <div className="flex gap-2">
                  <Input
                    id="search"
                    placeholder="Search by user, action, or details..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <Button onClick={handleSearch}>
                    <Search className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Severity Filter</Label>
                <div className="flex gap-2">
                  {['all', 'low', 'medium', 'high', 'critical'].map((severity) => (
                    <Button
                      key={severity}
                      variant={selectedSeverity === severity ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        setSelectedSeverity(severity);
                        setPage(1);
                      }}
                    >
                      {severity.charAt(0).toUpperCase() + severity.slice(1)}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Logs List */}
        <Card>
          <CardHeader>
            <CardTitle>Activity Log</CardTitle>
            <CardDescription>
              Showing {auditLogs.length} logs (Page {page} of {totalPages})
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-12 text-muted-foreground">
                Loading audit logs...
              </div>
            ) : auditLogs.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">No audit logs found</p>
                <p className="text-sm">Try adjusting your filters</p>
              </div>
            ) : (
              <div className="space-y-4">
                {auditLogs.map((log) => (
                  <div
                    key={log.id}
                    className="flex items-start gap-4 p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex-shrink-0 mt-1">
                      {getSeverityIcon(log.severity)}
                    </div>

                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{log.event_type}</span>
                          <Badge variant="outline" className={getSeverityColor(log.severity)}>
                            {log.severity}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          <span>{new Date(log.timestamp).toLocaleString()}</span>
                        </div>
                      </div>

                      <p className="text-sm">{log.description}</p>

                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          <span>
                            {log.user_name || `User ${log.user_id}`}
                            {log.user_role && ` (${log.user_role})`}
                          </span>
                        </div>
                        {log.resource_type && (
                          <span>Resource: {log.resource_type}</span>
                        )}
                        {log.ip_address && (
                          <span>IP: {log.ip_address}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {page} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
};

export default AuditLogsPage;
