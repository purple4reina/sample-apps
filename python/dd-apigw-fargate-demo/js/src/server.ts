import 'dd-trace/init'; // Import and initialize Datadog APM before other imports.

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import tracer from 'dd-trace';
import util from "util";

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors()); // Enable CORS
app.use(express.json()); // Parse JSON bodies

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  console.log('Handling request to /health');
  res.status(200).json({ status: 'healthy' });
});

// Index endpoint
app.get('/', (req: Request, res: Response) => {
  console.log('Handling request to /');
  console.log('x-dd-apigw-request-time is', util.inspect(req.headers['x-dd-apigw-request-time']))
  res.status(200).json({
    message: 'Hello World!',
    query: req.query,
    path: req.path,
    endpoints: app._router.stack.map((r: any) => {
      return {
        name: r.name,
        path: r.route ? r.route.path : null,
        method: r.route ? Object.keys(r.route.methods).join(', ') : null,
      }
    }),
  });
});

app.get('/books', (req: Request, res: Response) => {
  console.log('Handling request to /books');
  console.log('x-dd-apigw-request-time is', util.inspect(req.headers['x-dd-apigw-request-time']))
  res.status(200).json([
    { id: 1, title: '1984', author: 'George Orwell' },
    { id: 2, title: 'Brave New World', author: 'Aldous Huxley' },
    { id: 3, title: 'Fahrenheit 451', author: 'Ray Bradbury' }
  ]);
});

app.get('/books/:id', (req: Request, res: Response) => {
  console.log('Handling request to /books/:id');
  console.log('x-dd-apigw-request-time is', util.inspect(req.headers['x-dd-apigw-request-time']))
  const bookId = req.params.id;
  res.status(200).json({ id: bookId, title: 'Sample Book', author: 'Sample Author' });
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Start server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});

export default app; 
