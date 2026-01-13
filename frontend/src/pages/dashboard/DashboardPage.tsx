import React from 'react';
import { useAuthStore } from '@/stores/authStore';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();

  const stats = [
    {
      title: 'Total Screenings',
      value: '2,543',
      change: '+12.5%',
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Flagged Items',
      value: '127',
      change: '-4.3%',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
    {
      title: 'Approved',
      value: '2,189',
      change: '+8.1%',
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Pending Review',
      value: '227',
      change: '+3.2%',
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  const recentActivity = [
    {
      id: 1,
      action: 'New screening completed',
      user: 'John Doe',
      time: '5 minutes ago',
      status: 'success',
    },
    {
      id: 2,
      action: 'Item flagged for review',
      user: 'Jane Smith',
      time: '15 minutes ago',
      status: 'warning',
    },
    {
      id: 3,
      action: 'Final approval granted',
      user: 'Mike Johnson',
      time: '1 hour ago',
      status: 'success',
    },
    {
      id: 4,
      action: 'Blacklist updated',
      user: 'System',
      time: '2 hours ago',
      status: 'info',
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
