import { useOutlet } from 'react-router-dom';

import NotFound from '@/app/NotFound.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';

export default function LoginLayout() {
    const outlet = useOutlet();
    if (ARCHIVE_MODE) return <NotFound />;
    return outlet;
}
