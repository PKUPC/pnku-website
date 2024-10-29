import { TeamList } from '@/app/(general)/plaza/TeamList.tsx';
import NotFound from '@/app/NotFound.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';

export function PlazaPage() {
    const info = useSuccessGameInfo();
    const { data } = useWishData({ endpoint: 'game/get_team_list' });

    if (ARCHIVE_MODE || !info.user) return <NotFound />;
    if (!data) return <Loading />;
    if (data.status !== 'success') return <WishError res={data} />;

    return <TeamList teamList={data.team_list} />;
}
