import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Upload,
  FileSearch,
  BarChart3,
  ChevronRight,
  Loader2,
} from 'lucide-react';
import apiClient from '@/services/apiClient';

interface DashboardStats {
  totalScreenings: number;
  flaggedItems: number;
  approved: number;
  pendingReview: number;
}

interface ActivityItem {
  id: number;
  action: string;
  user: string;
  time: string;
  status: 'success' | 'warning' | 'info';
}

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    totalScreenings: 0,
    flaggedItems: 0,
    approved: 0,
    pendingReview: 0,
  });
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const [screeningRes, uploadsRes, pendingRes] = await Promise.all([
        apiClient.get('/reports/screening-summary').catch(() => ({ data: { data: {} } })),
        apiClient.get('/screening/v2/uploads').catch(() => ({ data: { uploads: [] } })),
        apiClient.get('/screening/v2/pending-matches').catch(() => ({ data: { matches: [] } })),
      ]);

      const screeningData = screeningRes.data?.data || screeningRes.data || {};
      const uploads = uploadsRes.data?.uploads || [];
      const pendingMatches = pendingRes.data?.matches || [];

      const totalScreenings = screeningData.total_screenings || uploads.reduce((sum: number, u: any) => sum + (u.total_entries || 0), 0) || 0;
      const flaggedItems = screeningData.total_flagged || pendingMatches.filter((m: any) => m.decision_status === 'flagged').length || 0;
      const approved = screeningData.approved || pendingMatches.filter((m: any) => m.decision_status === 'approved').length || 0;
      const pendingReview = pendingMatches.filter((m: any) => !m.decision_status || m.decision_status === 'pending').length || 0;

      setStats({ totalScreenings, flaggedItems, approved, pendingReview });

      const activities: ActivityItem[] = [];
      uploads.slice(0, 4).forEach((upload: any, index: number) => {
        activities.push({
          id: upload.id || index + 1,
          action: "Blacklist uploaded: " + (upload.filename || 'file'),
          user: upload.uploaded_by || 'System',
          time: upload.uploaded_at ? formatTimeAgo(new Date(upload.uploaded_at)) : 'Recently',
          status: upload.matched_entries > 0 ? 'warning' : 'success',
        });
      });

      if (pendingReview > 0) {
        activities.unshift({
          id: Date.now(),
          action: pendingReview + " items pending review",
          user: 'System',
          time: 'Now',
          status: 'warning',
        });
      }

      setRecentActivity(activities.slice(0, 4));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimeAgo = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return diffMins + ' minutes ago';
    if (diffHours < 24) return diffHours + ' hours ago';
    return diffDays + ' days ago';
  };

  const statsDisplay = [
    {
      title: 'Total Screenings',
      value: stats.totalScreenings.toLocaleString(),
      change: '+12.5%',
      icon: Activity,
      color: 'text-[#0B5394]',
      bgColor: 'bg-[#0B5394]/10',
    },
    {
      title: 'Flagged Items',
      value: stats.flaggedItems.toLocaleString(),
      change: '-4.3%',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      title: 'Approved',
      value: stats.approved.toLocaleString(),
      change: '+8.1%',
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Pending Review',
      value: stats.pendingReview.toLocaleString(),
      change: '+3.2%',
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-[#0B5394]">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-muted-foreground">
            Here is what is happening with your compliance screening today.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {isLoading ? (
            <div className="col-span-4 flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-[#0B5394]" />
              <span className="ml-2 text-muted-foreground">Loading stats...</span>
            </div>
          ) : (
            statsDisplay.map((stat) => (
              <Card key={stat.title} className="border-0 shadow-sm hover:shadow-md transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    {stat.title}
                  </CardTitle>
                  <div className={stat.bgColor + " p-2 rounded-lg"}>
                    <stat.icon className={"h-4 w-4 " + stat.color} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <TrendingUp className="h-3 w-3" />
                    {stat.change} from last month
                  </p>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card className="col-span-1 border-0 shadow-sm">
            <CardHeader>
              <CardTitle className="text-[#0B5394]">Recent Activity</CardTitle>
              <CardDescription>Latest actions in the system</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-5 w-5 animate-spin text-[#0B5394]" />
                </div>
              ) : recentActivity.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No recent activity</p>
                  <p className="text-sm mt-1">Upload a blacklist to get started</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {recentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-start gap-3 pb-3 border-b last:border-0 last:pb-0">
                      <div className={"w-2 h-2 rounded-full mt-2 " + (activity.status === 'success' ? 'bg-green-500' : activity.status === 'warning' ? 'bg-orange-500' : 'bg-[#0B5394]')} />
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium">{activity.action}</p>
                        <p className="text-xs text-muted-foreground">by {activity.user} - {activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="col-span-1 border-0 shadow-sm">
            <CardHeader>
              <CardTitle className="text-[#0B5394]">Quick Actions</CardTitle>
              <CardDescription>Common tasks for your role</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {user?.role === 'screener' && (
                  <>
                    <button onClick={() => navigate('/upload')} className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:bg-[#0B5394]/5 hover:border-[#0B5394]/30 transition-all group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Upload className="h-5 w-5 text-[#0B5394]" />
                          <div>
                            <p className="font-medium text-sm">Upload Blacklist File</p>
                            <p className="text-xs text-muted-foreground">Screen blacklist against KAMCO entities</p>
                          </div>
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-[#0B5394] transition-colors" />
                      </div>
                    </button>
                    <button onClick={() => navigate('/screening')} className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:bg-[#0B5394]/5 hover:border-[#0B5394]/30 transition-all group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <FileSearch className="h-5 w-5 text-[#0B5394]" />
                          <div>
                            <p className="font-medium text-sm">View Screening Results</p>
                            <p className="text-xs text-muted-foreground">Review potential matches found</p>
                          </div>
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-[#0B5394] transition-colors" />
                      </div>
                    </button>
                  </>
                )}
                {user?.role === 'checker' && (
                  <>
                    <button onClick={() => navigate('/checker')} className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:bg-[#0B5394]/5 hover:border-[#0B5394]/30 transition-all group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <CheckCircle className="h-5 w-5 text-[#0B5394]" />
                          <div>
                            <p className="font-medium text-sm">Review Flagged Items</p>
                            <p className="text-xs text-muted-foreground">Check items awaiting approval</p>
                          </div>
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-[#0B5394] transition-colors" />
                      </div>
                    </button>
                    <button onClick={() => navigate('/reports')} className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:bg-[#0B5394]/5 hover:border-[#0B5394]/30 transition-all group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <BarChart3 className="h-5 w-5 text-[#0B5394]" />
                          <div>
                            <p className="font-medium text-sm">Generate Report</p>
                            <p className="text-xs text-muted-foreground">Create compliance report</p>
                          </div>
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-[#0B5394] transition-colors" />
                      </div>
                    </button>
                  </>
                )}
                {user?.role === 'finalizer' && (
                  <>
                    <button onClick={() => navigate('/finalizer')} className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:bg-[#0B5394]/5 hover:border-[#0B5394]/30 transition-all group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <CheckCircle className="h-5 w-5 text-[#0B5394]" />
                          <div>
                            <p className="font-medium text-sm">Final Review</p>
                            <p className="text-xs text-muted-foreground">Approve or reject items</p>
                          </div>
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-[#0B5394] transition-colors" />
                      </div>
                    </button>
                    <button onClick={() => navigate('/reports')} className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:bg-[#0B5394]/5 hover:border-[#0B5394]/30 transition-all group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <BarChart3 className="h-5 w-5 text-[#0B5394]" />
                          <div>
                            <p className="font-medium text-sm">View Reports</p>
                            <p className="text-xs text-muted-foreground">Access compliance reports</p>
                          </div>
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-[#0B5394] transition-colors" />
                      </div>
                    </button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default DashboardPage;
