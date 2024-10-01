import { Wish } from '@/types/wish.ts';

export function PuzzleAction({
    action,
}: {
    action: Wish.Puzzle.PuzzleActionData;
    puzzle: Wish.Puzzle.PuzzleDetailData;
}) {
    if (action.type === 'webpage') {
        if (action.noreferrer === true)
            return (
                <>
                    你可以{' '}
                    <a href={action.url} target="_blank" rel="noopener noreferrer">
                        访问{action.name}
                    </a>
                </>
            );
        return (
            <>
                你可以{' '}
                <a href={action.url} target="_blank" rel="noopener noreferrer">
                    访问{action.name}
                </a>
            </>
        );
    } else if (action.type === 'media')
        return (
            <>
                你可以{' '}
                <a href={`${action.media_url}`} target="_blank" rel="noopener noreferrer">
                    下载{action.name}
                </a>
            </>
        );
}
