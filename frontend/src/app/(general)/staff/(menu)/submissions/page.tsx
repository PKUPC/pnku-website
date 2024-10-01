import { SubmissionTable } from '@/app/(general)/staff/(menu)/submissions/SubmissionTable.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useWishData } from '@/logic/swrWrappers';

export function StaffSubmissionPage() {
    const { data: staffGameInfo, mutate: reloadStaffGameInfo } = useWishData({
        endpoint: 'staff/get_game_info',
    });
    if (!staffGameInfo) return <Loading />;
    if (staffGameInfo.status === 'error') return <WishError res={staffGameInfo} reload={reloadStaffGameInfo} />;

    console.log(staffGameInfo);

    return (
        <SubmissionTable
            puzzle_filters={staffGameInfo.data.puzzles.map((item) => ({
                text: item.title,
                value: item.key,
            }))}
            team_filters={staffGameInfo.data.teams.map((item) => ({
                text: `[${item.team_id}]${item.team_name}`,
                value: item.team_id,
            }))}
            status_filters={staffGameInfo.data.puzzle_status.map((item) => ({ text: item, value: item }))}
        />
    );
}
