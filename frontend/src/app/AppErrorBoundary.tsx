import React from 'react';
import { ErrorBoundaryContext, useErrorBoundary } from 'react-use-error-boundary';

import { GeneralError } from '@/components/GeneralError';
import { InfoError, NeverError } from '@/errors';

export function ErrorHandler({ children }: { children: React.ReactNode }) {
    const [error] = useErrorBoundary();

    if (error) {
        if (error instanceof InfoError) {
            return (
                <GeneralError
                    title={'游戏信息获取出错'}
                    subtitle={
                        <>
                            请稍后重试或者联系网站管理员。
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
    return children;
}

export function AppErrorBoundary({ children }: { children: React.ReactNode }) {
    return (
        <ErrorBoundaryContext>
            <ErrorHandler>{children}</ErrorHandler>
        </ErrorBoundaryContext>
    );
}
