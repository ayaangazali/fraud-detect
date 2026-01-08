import React, { useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';

const RealTimeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { accessToken, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated || !accessToken) {
      console.log('WebSocket: Not authenticated, skipping connection');
      return;
    }
    
    console.log('WebSocket: Connection will be enabled when backend WebSocket endpoint is ready');
    
    // WebSocket features will be activated once backend supports it
    // For now, the app works without real-time updates
    
  }, [isAuthenticated, accessToken]);

  return <>{children}</>;
};

export default RealTimeProvider;
