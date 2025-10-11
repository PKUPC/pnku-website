import { useParams } from 'react-router';

import { MessageBox } from '@/app/(general)/info/message/MessageBox';
import NotFound from '@/app/NotFound.tsx';

export function StaffMessagePage() {
    const params = useParams();
    const tid = params.teamId;
    if (!tid || isNaN(+tid)) {
        return <NotFound />;
    }

    return <MessageBox teamId={+tid} />;
}
