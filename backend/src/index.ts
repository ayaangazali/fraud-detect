// src/index.ts
import express from 'express';
import cors from 'cors';
import uploadRoutes from './routes/upload';
import screeningRoutes from './routes/screening';
import exportRoutes from './routes/export';
import screeningRoutesV2 from './routes/screeningRoutesV2';
import reviewRoutes from './routes/reviewRoutes';

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Routes - Legacy (keep for backward compatibility)
app.use('/api/upload', uploadRoutes);
app.use('/api', screeningRoutes);
app.use('/api', exportRoutes);

// Routes - New workflow (3rd Excel vs 1st Excel)
app.use('/api', screeningRoutesV2);
app.use('/api/review', reviewRoutes);

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
  console.log(`   Legacy endpoints:`);
  console.log(`   POST http://localhost:${PORT}/api/upload/customers`);
  console.log(`   POST http://localhost:${PORT}/api/upload/blacklist`);
  console.log(`   POST http://localhost:${PORT}/api/screen`);
  console.log(`   POST http://localhost:${PORT}/api/export`);
  console.log(``);
  console.log(`   New workflow endpoints:`);
  console.log(`   POST http://localhost:${PORT}/api/upload/screening-list`);
  console.log(`   POST http://localhost:${PORT}/api/screen-list`);
  console.log(`   GET  http://localhost:${PORT}/api/kamco-clients`);
  console.log(`   POST http://localhost:${PORT}/api/review/flag`);
  console.log(`   POST http://localhost:${PORT}/api/review/safe`);
  console.log(`   GET  http://localhost:${PORT}/api/review/flagged-logbook`);
});

export default app;
