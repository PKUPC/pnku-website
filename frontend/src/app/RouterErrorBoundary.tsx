import { useRouteError } from 'react-router';

import { GeneralError } from '@/components/GeneralError';
import { InfoError, NeverError } from '@/errors';

export function RouterErrorBoundary() {
    const error = useRouteError();
    if (error) {
        if (error instanceof InfoError) {
            return (
                <GeneralError
                    title={'游戏信息获取出错'}
                    subtitle={
                        <>
                            和服务器的连接出现了问题，请稍后重试。如果您一直遇到此问题，请联系工作人员。
                            <br />
                        </>
                    }
                />
            );
        }
        console.error(error);
        if (error instanceof NeverError) {
            return (
                <GeneralError
                    title={'不存在的错误！'}
                    subtitle={
                        <>
                            如果你看到这个界面，说明出现了原则上不可能出现的情况，请及时联系网站管理员。
                            <br />
                        </>
                    }
                />
            );
        }
        return (
            <GeneralError
                title={'意料之外的错误！'}
                subtitle={
                    <>
                        如果你看到这个界面，说明出现了意料之外的错误，请及时联系网站管理员。
                        <br />
                    </>
                }
            />
        );
    }
}
