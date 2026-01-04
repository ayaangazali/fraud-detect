// src/index.ts
import express from 'express';
import cors from 'cors';
import uploadRoutes from './routes/upload';
import screeningRoutes from './routes/screening';
import exportRoutes from './routes/export';

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Routes
app.use('/api/upload', uploadRoutes);
app.use('/api', screeningRoutes);
app.use('/api/export', exportRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: err.message || 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📊 API endpoints:`);
  console.log(`   POST http://localhost:${PORT}/api/upload/customers`);
  console.log(`   POST http://localhost:${PORT}/api/upload/blacklist`);
  console.log(`   POST http://localhost:${PORT}/api/screen`);
  console.log(`   POST http://localhost:${PORT}/api/export`);
});

export default app;
