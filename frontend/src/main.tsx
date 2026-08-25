import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { app } from './app';
import '../style/styles.css';

// Mount the single-page React application into the browser document.
createRoot(document.getElementById('root')!).render(<StrictMode>{app}</StrictMode>);
