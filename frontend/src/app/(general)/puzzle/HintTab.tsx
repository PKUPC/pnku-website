import { HintList } from '@/app/(general)/puzzle/components/HintList';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts';
import { Wish } from '@/types/wish.ts';

import { CurrencyStatusList } from './components/CurrencyStatus';

export function HintTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    const info = useSuccessGameInfo();
    return (
        <div>
            {!ARCHIVE_MODE && info.user?.group === 'player' && (
                <>
                    <CurrencyStatusList />
                    <br />
                </>
            )}
            <HintList puzzleKey={puzzleData.key} />
        </div>
    );
}
