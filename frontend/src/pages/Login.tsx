import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Loader2, LogIn } from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/stores/authStore';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

const Login: React.FC = () => {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      const response = await authService.login(data);
      setAuth(response);
      toast.success(`Welcome back, ${response.user.username}!`);
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Login error:', error);
      // Handle different error formats
      let errorMessage = 'Login failed. Please check your credentials.';
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map((e: any) => e.msg || e).join(', ');
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white p-4">
      <Card className="w-full max-w-md shadow-lg border-0">
        <CardHeader className="space-y-1 pb-6">
          <div className="flex items-center justify-center mb-4">
            {/* KAMCO Invest Logo */}
            <img 
              src="/kamco-logo.svg" 
              alt="KAMCO Invest" 
              className="h-16 w-auto"
            />
          </div>
          <CardDescription className="text-center text-base text-gray-600">
            AML/KYC Compliance Screening System
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username" className="text-gray-700">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                {...register('username')}
                disabled={isLoading}
                className="h-11 border-gray-200 focus:border-[#0B5394] focus:ring-[#0B5394]/20"
              />
              {errors.username && (
                <p className="text-sm text-red-500">{errors.username.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-gray-700">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                {...register('password')}
                disabled={isLoading}
                className="h-11 border-gray-200 focus:border-[#0B5394] focus:ring-[#0B5394]/20"
              />
              {errors.password && (
                <p className="text-sm text-red-500">{errors.password.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full h-11 text-base bg-[#0B5394] hover:bg-[#094478]" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <LogIn className="mr-2 h-5 w-5" />
                  Sign In
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-100">
            <p className="text-sm font-medium text-center mb-3 text-gray-700">Demo Credentials</p>
            <div className="grid grid-cols-1 gap-2 text-xs">
              <div className="p-2 bg-white rounded border border-gray-100">
                <p className="font-semibold text-[#0B5394]">Screener</p>
                <p className="text-gray-500">screener_test / ScreenerPass123!</p>
              </div>
              <div className="p-2 bg-white rounded border border-gray-100">
                <p className="font-semibold text-[#0B5394]">Checker</p>
                <p className="text-gray-500">checker_test / CheckerPass123!</p>
              </div>
              <div className="p-2 bg-white rounded border border-gray-100">
                <p className="font-semibold text-[#0B5394]">Finalizer</p>
                <p className="text-gray-500">finalizer_test / FinalizerPass123!</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
