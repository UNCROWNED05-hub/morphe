import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 5000;
const CLIENT_ORIGIN = process.env.CLIENT_ORIGIN || 'http://localhost:5173';

app.use(cors({
  origin: CLIENT_ORIGIN === '*' ? true : [CLIENT_ORIGIN, 'http://localhost:5173'],
  credentials: true
}));

app.use(express.json());

// Standard health check endpoint
app.get('/health', (_req: Request, res: Response) => {
  res.status(200).json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// Hello-world test endpoint
app.get('/api/hello', (_req: Request, res: Response) => {
  res.status(200).json({
    message: 'Hackathon API Server Online',
    timestamp: new Date().toISOString()
  });
});

// Global standard error handler
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  res.status(500).json({
    error: {
      code: 'INTERNAL_SERVER_ERROR',
      message: err.message || 'An unexpected error occurred'
    }
  });
});

const server = app.listen(PORT, () => {
  process.stdout.write(`Server listening on port ${PORT}\n`);
});

const gracefulShutdown = () => {
  server.close(() => {
    process.exit(0);
  });
};

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

export default app;
