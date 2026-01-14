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
  Shield,
  ChevronRight,
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

const Dashboard: React.FC = () => {
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

  // Fetch real data from API
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      // Fetch screening summary
      const [screeningRes, uploadsRes, pendingRes] = await Promise.all([
        apiClient.get('/reports/screening-summary').catch(() => ({ data: { data: {} } })),
        apiClient.get('/screening/v2/uploads').catch(() => ({ data: { uploads: [] } })),
        apiClient.get('/screening/v2/pending-matches').catch(() => ({ data: { matches: [] } })),
      ]);

      const screeningData = screeningRes.data?.data || screeningRes.data || {};
      const uploads = uploadsRes.data?.uploads || [];
      const pendingMatches = pendingRes.data?.matches || [];

      // Calculate stats from real data
      const totalScreenings = screeningData.total_screenings || uploads.reduce((sum: number, u: any) => sum + (u.total_entries || 0), 0) || 0;
      const flaggedItems = screeningData.total_flagged || pendingMatches.filter((m: any) => m.decision_status === 'flagged').length || 0;
      const approved = screeningData.approved || pendingMatches.filter((m: any) => m.decision_status === 'approved').length || 0;
      const pendingReview = pendingMatches.filter((m: any) => !m.decision_status || m.decision_status === 'pending').length || 0;

      setStats({
        totalScreenings,
        flaggedItems,
        approved,
        pendingReview,
      });

      // Build recent activity from uploads
      const activities: ActivityItem[] = [];
      uploads.slice(0, 4).forEach((upload: any, index: number) => {
        activities.push({
          id: upload.id || index + 1,
          action: `Blacklist uploaded: ${upload.filename || 'file'}`,
          user: upload.uploaded_by || 'System',
          time: upload.uploaded_at ? formatTimeAgo(new Date(upload.uploaded_at)) : 'Recently',
          status: upload.matched_entries > 0 ? 'warning' : 'success',
        });
      });

      // Add some context-aware activities
      if (pendingReview > 0) {
        activities.unshift({
          id: Date.now(),
          action: `${pendingReview} items pending review`,
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
    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
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
        {/* Welcome Section */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-muted-foreground">
            Here's what's happening with your compliance screening today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <div className={`${stat.bgColor} p-2 rounded-lg`}>
                  <stat.icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                  <TrendingUp className="h-3 w-3" />
                  {stat.change} from last month
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="col-span-1">
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest actions in the system
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start gap-3 pb-3 border-b last:border-0 last:pb-0"
                  >
                    <div
                      className={`w-2 h-2 rounded-full mt-2 ${
                        activity.status === 'success'
                          ? 'bg-green-500'
                          : activity.status === 'warning'
                          ? 'bg-orange-500'
                          : 'bg-blue-500'
                      }`}
                    />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">
                        by {activity.user} • {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="col-span-1">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common tasks for your role
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {user?.role === 'screener' && (
                  <>
                    <button className="w-full text-left px-4 py-3 rounded-lg border hover:bg-muted transition-colors">
                      <p className="font-medium text-sm">Upload Blacklist File</p>
                      <p className="text-xs text-muted-foreground">
                        Screen blacklist against KAMCO entities
                      </p>
                    </button>
                    <button className="w-full text-left px-4 py-3 rounded-lg border hover:bg-muted transition-colors">
                      <p className="font-medium text-sm">View Screening Results</p>
                      <p className="text-xs text-muted-foreground">
                        Review potential matches found
                      </p>
                    </button>
                  </>
                )}
                {user?.role === 'checker' && (
                  <>
                    <button className="w-full text-left px-4 py-3 rounded-lg border hover:bg-muted transition-colors">
                      <p className="font-medium text-sm">Review Flagged Items</p>
                      <p className="text-xs text-muted-foreground">
                        Check items awaiting approval
                      </p>
                    </button>
                    <button className="w-full text-left px-4 py-3 rounded-lg border hover:bg-muted transition-colors">
                      <p className="font-medium text-sm">Generate Report</p>
                      <p className="text-xs text-muted-foreground">
                        Create compliance report
                      </p>
                    </button>
                  </>
                )}
                {user?.role === 'finalizer' && (
                  <>
                    <button className="w-full text-left px-4 py-3 rounded-lg border hover:bg-muted transition-colors">
                      <p className="font-medium text-sm">Final Review</p>
                      <p className="text-xs text-muted-foreground">
                        Approve or reject items
                      </p>
                    </button>
                    <button className="w-full text-left px-4 py-3 rounded-lg border hover:bg-muted transition-colors">
                      <p className="font-medium text-sm">View Reports</p>
                      <p className="text-xs text-muted-foreground">
                        Access compliance reports
                      </p>
                    </button>
                  </>
                )}
                {(user?.role === 'checker' || user?.role === 'finalizer') && (
                  <>
                    <button className="w-full text-left px-4 py-3 rounded-lg border hover:bg-muted transition-colors">
                      <p className="font-medium text-sm">View Audit Logs</p>
                      <p className="text-xs text-muted-foreground">
                        Monitor system activity
                      </p>
                    </button>
                    <button className="w-full text-left px-4 py-3 rounded-lg border hover:bg-muted transition-colors">
                      <p className="font-medium text-sm">System Reports</p>
                      <p className="text-xs text-muted-foreground">
                        View comprehensive analytics
                      </p>
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

export default Dashboard;
