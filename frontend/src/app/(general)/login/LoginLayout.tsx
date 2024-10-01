import { useOutlet } from 'react-router-dom';

import NotFound from '@/app/NotFound.tsx';

export default function LoginLayout() {
    const outlet = useOutlet();
    if (import.meta.env.VITE_ARCHIVE_MODE === 'true') return <NotFound />;
    return outlet;
}
