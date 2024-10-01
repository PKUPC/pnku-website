import { SubmissionList } from '@/app/(general)/puzzle/components/SubmissionList';
import { Wish } from '@/types/wish.ts';

export function SubmissionTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    return <SubmissionList puzzleKey={puzzleData.key} />;
}
