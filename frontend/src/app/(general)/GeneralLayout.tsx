import { useOutlet } from 'react-router';

import { Footer } from '@/components/Footer.tsx';

export default function GeneralLayout() {
    const outlet = useOutlet();

    return (
        <div className="mt-12 p-2 max-w-300 mx-auto">
            {outlet}
            <Footer />
        </div>
    );
}
