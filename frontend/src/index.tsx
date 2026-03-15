import { StyleProvider } from '@ant-design/cssinjs';
import React from 'react';
import ReactDOM from 'react-dom/client';

import { AppRouter } from '@/Router.tsx';
import { AppErrorBoundary } from '@/app/AppErrorBoundary.tsx';
import { ThemeContextProvider } from '@/logic/ThemeContext.tsx';

import App from './App.tsx';
import './globals.css';
import { GameSettingContextProvider } from './logic/SiteSettingContext.tsx';

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <AppErrorBoundary>
            <StyleProvider layer>
                <GameSettingContextProvider>
                    <ThemeContextProvider>
                        <App>
                            <AppRouter />
                        </App>
                    </ThemeContextProvider>
                </GameSettingContextProvider>
            </StyleProvider>
        </AppErrorBoundary>
    </React.StrictMode>,
);
