import { useNavigate, useParams } from 'react-router';

import { LeftCircleIcon } from '@/SvgIcons';
import NotFound from '@/app/NotFound.tsx';
import { ClickTitle } from '@/components/LinkTitle';
import { SimpleTemplateFile } from '@/components/Template';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function StoryPage() {
    const info = useSuccessGameInfo();
    const { '*': storyKey } = useParams();
    const navigate = useNavigate();

    if (ARCHIVE_MODE) {
        /* empty */
    } else if (!info.user) return <NotFound />;
    else if (info.user?.group !== 'staff' && (!info.team?.gaming || !info.game.isGameBegin)) return <NotFound />;

    if (!storyKey || storyKey.length === 0) return <NotFound />;

    return (
        <div className={'slim-container'}>
            <ClickTitle icon={<LeftCircleIcon />} title={'返回'} onClick={() => navigate(-1)} />
            <br />
            <SimpleTemplateFile name={storyKey} />
        </div>
    );
}
