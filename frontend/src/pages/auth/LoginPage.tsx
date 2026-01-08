import React from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import { Shield } from 'lucide-react';

export const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="w-full max-w-md space-y-8">
        {/* Logo & Branding */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary text-primary-foreground mb-4">
            <Shield size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">KAMCO AML/KYC</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Screening & Compliance Management System
          </p>
        </div>

        {/* Login Form */}
        <LoginForm />

        {/* Footer */}
        <div className="text-center text-sm text-gray-600 dark:text-gray-400">
          <p>© 2026 KAMCO. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
