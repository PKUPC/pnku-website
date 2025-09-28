import { useSearchParams } from 'react-router-dom';
import { Fragment } from 'react/jsx-runtime';

import { TeamBanListCard } from '@/app/(general)/staff/(detail)/team-detail/TeamBanListCard.tsx';
import { TeamInfoCard } from '@/app/(general)/staff/(detail)/team-detail/TeamInfoCard.tsx';
import { TeamPassedPuzzleTable } from '@/app/(general)/staff/(detail)/team-detail/TeamPassedPuzzleTable.tsx';
import { TeamSubmissionsTable } from '@/app/(general)/staff/(detail)/team-detail/TeamSubmissionsTable.tsx';
import NotFound from '@/app/NotFound.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useWishData } from '@/logic/swrWrappers';

import { TeamCurrencyCard } from './TeamCurrencyCard';
import { TeamCurrencyHistoryTable } from './TeamCurrencyHistoryTable';

function TeamDetailBody({ tid }: { tid: number }) {
    const { data, mutate } = useWishData({
        endpoint: 'staff/get_team_detail',
        payload: { team_id: tid },
    });

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;
    return (
        <div>
            <TeamInfoCard data={data} reloadData={mutate} />
            <br />
            <TeamBanListCard data={data} reloadData={mutate} />
            <br />
            <TeamSubmissionsTable data={data.submissions} />
            {data.currency_status.map((currency) => (
                <Fragment key={currency.type}>
                    <br />
                    <TeamCurrencyCard team_id={tid} data={currency} reloadData={mutate} />
                    <br />
                    <TeamCurrencyHistoryTable currencyDetail={currency} />
                </Fragment>
            ))}
            <br />
            <TeamPassedPuzzleTable data={data.passed_puzzles} />
        </div>
    );
}

export function StaffTeamDetailPage() {
    const [searchParams] = useSearchParams();
    const tid = searchParams.get('tid');
    if (!tid || isNaN(+tid)) {
        return <NotFound />;
    }
    return <TeamDetailBody tid={parseInt(tid)} />;
}
