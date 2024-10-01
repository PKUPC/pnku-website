import { TicketTable } from '@/app/(general)/staff/(menu)/tickets/TicketTable';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useWishData } from '@/logic/swrWrappers';

export function StaffTicketPage() {
    const { data: staffGameInfo, mutate: reloadStaffGameInfo } = useWishData({
        endpoint: 'staff/get_game_info',
    });
    if (!staffGameInfo) return <Loading />;
    if (staffGameInfo.status === 'error') return <WishError res={staffGameInfo} reload={reloadStaffGameInfo} />;

    console.log(staffGameInfo);

    return (
        <TicketTable
            status_filters={staffGameInfo.data.ticket_status.map((item) => ({ text: item, value: item }))}
            team_filters={staffGameInfo.data.teams.map((item) => ({
                text: `[${item.team_id}]${item.team_name}`,
                value: item.team_id,
            }))}
        />
    );
}
