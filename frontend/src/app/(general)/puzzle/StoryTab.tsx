import { TemplateFile } from '@/components/Template';
import { Wish } from '@/types/wish';

import { MusicPlayer } from './components/MusicPlayer';

export function StoryTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    return (
        <div>
            {puzzleData.bgm_list && puzzleData.bgm_list.length > 0 && (
                <>
                    <MusicPlayer playlist={puzzleData.bgm_list} />
                    <br />
                </>
            )}
            {puzzleData.stories?.map((story, index) => (
                <TemplateFile name={story} key={index} />
            ))}
        </div>
    );
}
