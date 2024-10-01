import React from 'react';

import { Footer } from '@/components/Footer.tsx';

export default function PuzzleListLayout({ children }: { children: React.ReactNode }) {
    return (
        <>
            <div
                style={{
                    width: '100%',
                    marginTop: 48,
                    background: 'rgb(229, 229, 229)',
                    minHeight: 'calc(100vh - 48px)',
                }}
            >
                {children}
                <Footer />
            </div>
        </>
    );
}
