import { HintList } from '@/app/(general)/puzzle/components/HintList';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { Wish } from '@/types/wish.ts';

import { CurrencyStatusList } from './components/CurrencyStatus';

export function HintTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    return (
        <div>
            {!ARCHIVE_MODE && (
                <>
                    <CurrencyStatusList />
                    <br />
                </>
            )}
            <HintList puzzleKey={puzzleData.key} />
        </div>
    );
}
