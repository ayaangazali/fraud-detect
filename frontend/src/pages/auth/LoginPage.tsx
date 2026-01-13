import React from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import { Shield, User, Lock, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export const LoginPage: React.FC = () => {
  const testAccounts = [
    { role: 'Screener', username: 'screener_test', password: 'Screener123', color: 'text-blue-600' },
    { role: 'Checker', username: 'checker_test', password: 'Checker123', color: 'text-green-600' },
    { role: 'Finalizer', username: 'finalizer_test', password: 'Finalizer123', color: 'text-purple-600' }
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="w-full max-w-4xl grid md:grid-cols-2 gap-6">
        {/* Left Side - Login Form */}
        <div className="space-y-6">
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

        {/* Right Side - Test Credentials */}
        <div className="space-y-4">
          <Alert className="bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800">
            <AlertCircle className="h-4 w-4 text-amber-600" />
            <AlertDescription className="text-amber-800 dark:text-amber-200">
              <strong>Demo/Test Environment</strong>
              <br />
              Use the credentials below to test the system
            </AlertDescription>
          </Alert>

          <Card className="border-2 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700">
              <CardTitle className="flex items-center gap-2 text-lg">
                <User className="h-5 w-5" />
                Test Accounts
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              {testAccounts.map((account, index) => (
                <div 
                  key={index}
                  className="p-4 rounded-lg border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className={`font-bold text-sm ${account.color}`}>
                      {account.role.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      Role: {account.role}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600 dark:text-gray-400">Username:</span>
                      <code className="px-2 py-1 bg-gray-100 dark:bg-gray-900 rounded text-gray-900 dark:text-gray-100 font-mono text-xs">
                        {account.username}
                      </code>
                    </div>
                    <div className="flex items-center gap-2">
                      <Lock className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600 dark:text-gray-400">Password:</span>
                      <code className="px-2 py-1 bg-gray-100 dark:bg-gray-900 rounded text-gray-900 dark:text-gray-100 font-mono text-xs">
                        {account.password}
                      </code>
                    </div>
                  </div>
                </div>
              ))}

              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  💡 Click on any credential to copy it
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
