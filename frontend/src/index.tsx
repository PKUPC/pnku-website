import React from 'react';
import ReactDOM from 'react-dom/client';

import { AppRouter } from '@/Router.tsx';
import { AppErrorBoundary } from '@/app/AppErrorBoundary.tsx';
import { ThemeContextProvider } from '@/logic/ThemeContext.tsx';

import App from './App.tsx';

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <AppErrorBoundary>
            <ThemeContextProvider>
                <App>
                    <AppRouter />
                </App>
            </ThemeContextProvider>
        </AppErrorBoundary>
    </React.StrictMode>,
);
