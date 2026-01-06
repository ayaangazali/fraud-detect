// src/pages/Login.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // TODO: Replace with actual API call
      // Simulate login delay
      await new Promise(resolve => setTimeout(resolve, 500));

      // Hardcoded credentials for now (will be replaced)
      const validUsers = {
        'screener': { password: 'screener123', role: 'screener' },
        'checker': { password: 'checker123', role: 'checker' },
        'finalizer': { password: 'finalizer123', role: 'finalizer' },
      };

      const user = validUsers[username.toLowerCase() as keyof typeof validUsers];
      
      if (user && user.password === password) {
        // Store auth data in localStorage (temporary)
        localStorage.setItem('auth', JSON.stringify({
          username,
          role: user.role,
          token: 'fake-jwt-token-' + Date.now()
        }));

        // Redirect to dashboard
        navigate('/dashboard');
      } else {
        setError('Invalid username or password');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo">
            <svg width="50" height="50" viewBox="0 0 50 50" fill="none">
              <rect width="50" height="50" rx="10" fill="#0B5394"/>
              <path d="M15 25L22 32L35 18" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h1>KAMCO</h1>
          <p className="subtitle">Compliance Screening System</p>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          {error && (
            <div className="error-message">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              autoComplete="username"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="login-footer">
          <div className="demo-credentials">
            <p className="demo-title">Demo Credentials:</p>
            <div className="demo-users">
              <div className="demo-user">
                <strong>Screener:</strong> screener / screener123
              </div>
              <div className="demo-user">
                <strong>Checker:</strong> checker / checker123
              </div>
              <div className="demo-user">
                <strong>Finalizer:</strong> finalizer / finalizer123
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="login-background">
        <div className="bg-shape shape-1"></div>
        <div className="bg-shape shape-2"></div>
        <div className="bg-shape shape-3"></div>
      </div>
    </div>
  );
};

export default Login;
