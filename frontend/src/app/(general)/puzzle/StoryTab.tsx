import { TemplateFile } from '@/components/Template';
import { Wish } from '@/types/wish';

export function StoryTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    return (
        <div>
            {puzzleData.stories?.map((story, index) => (
                <TemplateFile name={story} key={index} />
            ))}
        </div>
    );
}
