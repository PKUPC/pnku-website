import { Solution } from '@/app/(general)/puzzle/components/Solution';
import { Wish } from '@/types/wish.ts';

export function SolutionTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    return <Solution puzzleKey={puzzleData.key} />;
}
