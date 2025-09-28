import { useSearchParams } from 'react-router-dom';

import { MessageBox } from '@/app/(general)/info/message/MessageBox';
import NotFound from '@/app/NotFound.tsx';

export function StaffMessagePage() {
    const [searchParams] = useSearchParams();
    const tid = searchParams.get('tid');
    if (!tid || isNaN(+tid)) {
        return <NotFound />;
    }

    return <MessageBox teamId={+tid} />;
}
