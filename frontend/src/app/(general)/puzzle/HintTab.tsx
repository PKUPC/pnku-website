import ApStatus from '@/app/(general)/puzzle/components/ApStatus';
import { HintList } from '@/app/(general)/puzzle/components/HintList';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { Wish } from '@/types/wish.ts';

export function HintTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    return (
        <div>
            {!ARCHIVE_MODE && (
                <>
                    <ApStatus />
                    <br />
                </>
            )}
            <HintList puzzleKey={puzzleData.key} />
        </div>
    );
}
