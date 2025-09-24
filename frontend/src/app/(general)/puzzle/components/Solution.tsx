import { useState } from 'react';

import { SimpleTemplateFile } from '@/components/Template';

export function Solution({ puzzleKey }: { puzzleKey: string }) {
    const [clear, setClear] = useState(false);

    return (
        <div
            style={{
                filter: clear ? 'blur(0)' : 'blur(5px)',
                cursor: clear ? 'default' : 'pointer',
                transition: 'filter 0.3s',
            }}
            onClick={() => {
                if (!clear) setClear(true);
            }}
        >
            <SimpleTemplateFile name={`solutions/${puzzleKey}`} />
        </div>
    );
}
