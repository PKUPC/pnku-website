import { useOutlet } from 'react-router-dom';

import { Footer } from '@/components/Footer.tsx';

export default function GeneralLayout() {
    const outlet = useOutlet();

    return (
        <div className="mt-12 p-2 max-w-[75rem] mx-auto">
            {outlet}
            <Footer />
        </div>
    );
}
