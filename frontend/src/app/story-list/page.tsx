import NotFound from '@/app/NotFound.tsx';
import { StoryList } from '@/app/story-list/StoryList';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { Footer } from '@/components/Footer.tsx';
import { WishError } from '@/components/WishError';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';

function StoryListBody() {
    const { data } = useWishData({ endpoint: 'game/get_story_list' });

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;

    console.log(data);

    return <StoryList storyGroups={data.data} />;
}

export function StoryListPage() {
    const gameInfo = useSuccessGameInfo();

    if (ARCHIVE_MODE) {
        /* empty */
    } else if (!gameInfo.user) return <NotFound />;
    else if (gameInfo.user.group !== 'staff' && (!gameInfo.game.isGameBegin || !gameInfo.team?.gaming))
        return <NotFound />;

    return (
        <div className="mt-12 bg-base-300 w-full" style={{ minHeight: 'calc(100vh - 3rem)' }}>
            <StoryListBody />
            <Footer />
        </div>
    );
}
