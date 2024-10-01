import { useState } from 'react';

import { SimpleTemplateFile } from '@/components/Template';

import styles from './Solution.module.scss';

export function Solution({ puzzleKey }: { puzzleKey: string }) {
    const [clear, setClear] = useState(false);

    return (
        <div
            className={styles.solutionContent}
            style={{
                filter: clear ? 'blur(0)' : 'blur(5px)',
                cursor: clear ? 'default' : 'pointer',
            }}
            onClick={() => {
                if (!clear) setClear(true);
            }}
        >
            <SimpleTemplateFile name={`solutions/${puzzleKey}`} />
        </div>
    );
}
