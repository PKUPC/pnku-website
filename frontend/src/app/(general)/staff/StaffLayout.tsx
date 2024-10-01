import { useOutlet } from 'react-router-dom';

import NotFound from '@/app/NotFound.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

import { StaffDetailLayout } from './(detail)/layout';
import { StaffMessagePage } from './(detail)/message/page';
import { StaffTeamDetailPage } from './(detail)/team-detail/page';
import { StaffMenuLayout } from './(menu)/layout';
import { StaffSubmissionPage } from './(menu)/submissions/page';
import { StaffTeamPage } from './(menu)/teams/page';
import { StaffTicketPage } from './(menu)/tickets/page';

function StaffLayout() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    if (import.meta.env.VITE_ARCHIVE_MODE === 'true') return <NotFound />;
    if (!info.user || info.user.group !== 'staff') return <NotFound />;

    return outlet;
}

export {
    StaffLayout,
    StaffMenuLayout,
    StaffTeamPage,
    StaffTicketPage,
    StaffDetailLayout,
    StaffSubmissionPage,
    StaffMessagePage,
    StaffTeamDetailPage,
};
