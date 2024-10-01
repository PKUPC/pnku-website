import { Tag } from 'antd';
import { useContext } from 'react';

import { EyeIcon } from '@/SvgIcons';
import { GameStatusContext } from '@/logic/contexts.ts';

export default function ApStatus() {
    const { currentAp, currentApIncrease } = useContext(GameStatusContext);
    return (
        <div>
            <Tag>
                <span>
                    当前注意力 : {currentAp}{' '}
                    <EyeIcon style={{ color: 'transparent', transform: 'translateY(0.1em)' }} />
                </span>
                <span>
                    {' '}
                    (+{currentApIncrease} <EyeIcon style={{ color: 'transparent', transform: 'translateY(0.1em)' }} /> /
                    min)
                </span>
            </Tag>
        </div>
    );
}
