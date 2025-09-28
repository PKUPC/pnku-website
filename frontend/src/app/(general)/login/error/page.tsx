import { Button } from 'antd';
import { useNavigate, useSearchParams } from 'react-router-dom';

import NotFound from '@/app/NotFound.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { NeverError } from '@/errors';
import { useGameInfo } from '@/logic/contexts.ts';

export function LoginErrorPage() {
    const nav = useNavigate();
    const [searchParam] = useSearchParams();
    const errorMsg = searchParam.get('msg');
    console.log(errorMsg);
    const info = useGameInfo();
    if (info.status === 'error') throw new NeverError();
    if (ARCHIVE_MODE) return <NotFound />;

    return (
        <div className={'slim-container'}>
            <br />
            登录出错：{errorMsg}
            <br />
            <br />
            <Button danger onClick={() => nav('/login')}>
                返回登录页面
            </Button>
        </div>
    );
}
