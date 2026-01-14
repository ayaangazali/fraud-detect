import React, { useState, useEffect } from 'react';
import { Menu, Bell, Search, X, Clock, AlertTriangle, CheckCircle, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import apiClient from '@/services/apiClient';

interface HeaderProps {
  onMenuClick: () => void;
}

interface Notification {
  id: number;
  type: 'info' | 'warning' | 'success';
  title: string;
  message: string;
  time: string;
  read: boolean;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      // Fetch recent activity for notifications
      const [uploadsRes, pendingRes] = await Promise.all([
        apiClient.get('/screening/v2/uploads').catch(() => ({ data: { uploads: [] } })),
        apiClient.get('/screening/v2/pending-matches').catch(() => ({ data: { matches: [] } })),
      ]);

      const uploads = uploadsRes.data?.uploads || [];
      const pendingMatches = pendingRes.data?.matches || [];

      const newNotifications: Notification[] = [];

      // Add pending review notifications
      if (pendingMatches.length > 0) {
        newNotifications.push({
          id: 1,
          type: 'warning',
          title: 'Pending Reviews',
          message: pendingMatches.length + ' items awaiting your review',
          time: 'Now',
          read: false,
        });
      }

      // Add recent upload notifications
      uploads.slice(0, 3).forEach((upload: any, index: number) => {
        newNotifications.push({
          id: index + 10,
          type: upload.matched_entries > 0 ? 'warning' : 'success',
          title: 'Blacklist Upload',
          message: (upload.filename || 'File') + ' processed - ' + (upload.matched_entries || 0) + ' matches found',
          time: formatTimeAgo(new Date(upload.uploaded_at || Date.now())),
          read: false,
        });
      });

      // Add system notification
      newNotifications.push({
        id: 99,
        type: 'info',
        title: 'System Ready',
        message: 'All screening services are operational',
        time: '1 hour ago',
        read: true,
      });

      setNotifications(newNotifications);
      setUnreadCount(newNotifications.filter(n => !n.read).length);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const formatTimeAgo = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return diffMins + 'm ago';
    if (diffHours < 24) return diffHours + 'h ago';
    return Math.floor(diffMs / 86400000) + 'd ago';
  };

  const markAllRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'warning': return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'success': return <CheckCircle className="h-4 w-4 text-green-500" />;
      default: return <FileText className="h-4 w-4 text-[#0B5394]" />;
    }
  };

  return (
    <header className="sticky top-0 z-30 w-full border-b border-gray-100 bg-white shadow-sm">
      <div className="flex h-16 items-center gap-4 px-4">
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
        >
          <Menu className="h-5 w-5 text-[#0B5394]" />
        </Button>

        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search..."
              className="pl-8 w-full border-gray-200 focus:border-[#0B5394] focus:ring-[#0B5394]/20"
            />
          </div>
        </div>

        {/* Right section - Notifications */}
        <div className="flex items-center gap-2 relative">
          <Button 
            variant="ghost" 
            size="icon" 
            className="relative hover:bg-[#0B5394]/5"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell className="h-5 w-5 text-gray-600" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 h-4 w-4 rounded-full bg-red-500 text-[10px] text-white flex items-center justify-center font-medium">
                {unreadCount}
              </span>
            )}
          </Button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 top-12 w-80 bg-white rounded-lg shadow-lg border border-gray-100 z-50">
              <div className="p-3 border-b border-gray-100 flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Notifications</h3>
                {unreadCount > 0 && (
                  <button 
                    onClick={markAllRead}
                    className="text-xs text-[#0B5394] hover:underline"
                  >
                    Mark all read
                  </button>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-4 text-center text-gray-500 text-sm">
                    No notifications
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <div 
                      key={notification.id}
                      className={"p-3 border-b border-gray-50 hover:bg-gray-50 cursor-pointer " + (!notification.read ? 'bg-[#0B5394]/5' : '')}
                    >
                      <div className="flex gap-3">
                        <div className="mt-0.5">
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">{notification.title}</p>
                          <p className="text-xs text-gray-500 truncate">{notification.message}</p>
                          <p className="text-xs text-gray-400 mt-1">{notification.time}</p>
                        </div>
                        {!notification.read && (
                          <div className="w-2 h-2 rounded-full bg-[#0B5394] mt-2"></div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
              <div className="p-2 border-t border-gray-100">
                <button className="w-full text-center text-sm text-[#0B5394] hover:underline py-1">
                  View all activity
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
