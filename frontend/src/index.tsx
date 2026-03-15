import { StyleProvider } from '@ant-design/cssinjs';
import React from 'react';
import ReactDOM from 'react-dom/client';

import { AppRouter } from '@/Router.tsx';
import { AppErrorBoundary } from '@/app/AppErrorBoundary.tsx';
import { ThemeContextProvider } from '@/logic/ThemeContext.tsx';

import App from './App.tsx';
import './globals.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <AppErrorBoundary>
            <StyleProvider layer>
                <ThemeContextProvider>
                    <App>
                        <AppRouter />
                    </App>
                </ThemeContextProvider>
            </StyleProvider>
        </AppErrorBoundary>
    </React.StrictMode>,
);
