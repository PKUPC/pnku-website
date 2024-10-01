import ApStatus from '@/app/(general)/puzzle/components/ApStatus';
import { HintList } from '@/app/(general)/puzzle/components/HintList';
import { Wish } from '@/types/wish.ts';

export function HintTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    return (
        <div>
            {import.meta.env.VITE_ARCHIVE_MODE !== 'true' && (
                <>
                    <ApStatus />
                    <br />
                </>
            )}
            <HintList puzzleKey={puzzleData.key} />
        </div>
    );
}
