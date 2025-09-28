import { useNavigate, useOutlet } from 'react-router-dom';

import { LeftCircleIcon } from '@/SvgIcons';
import { ClickTitle } from '@/components/LinkTitle';

export function StaffDetailLayout() {
    const outlet = useOutlet();
    const navigate = useNavigate();
    return (
        <div className={'slim-container'}>
            <ClickTitle icon={<LeftCircleIcon />} title={'返回'} onClick={() => navigate(-1)} />
            <br />
            {outlet}
        </div>
    );
}
