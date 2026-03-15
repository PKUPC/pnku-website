import { useState } from 'react';

import NotFound from '@/app/NotFound';
import { SimpleTemplateFile } from '@/components/Template';
import { ARCHIVE_MODE } from '@/constants';
import { Wish } from '@/types/wish.ts';

export function Solution({ templateKey }: { templateKey: string }) {
    // ARCHIVCE_MODE 下默认加一个模糊
    const [clear, setClear] = useState(!ARCHIVE_MODE);

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
            <SimpleTemplateFile name={templateKey} />
        </div>
    );
}

export function SolutionTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    if (!puzzleData.solution) return <NotFound />;
    return <Solution templateKey={puzzleData.solution} />;
}
