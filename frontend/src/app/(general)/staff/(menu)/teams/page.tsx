import { TeamTable } from '@/app/(general)/staff/(menu)/teams/TeamTable.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useWishData } from '@/logic/swrWrappers';

export function StaffTeamPage() {
    const { data, mutate } = useWishData({ endpoint: 'staff/get_team_list' });
    if (!data) return <Loading />;
    if (data.status !== 'success') return <WishError res={data} />;

    console.log(data);

    return <TeamTable teamIntoList={data.data} reload={() => mutate()} />;
}
