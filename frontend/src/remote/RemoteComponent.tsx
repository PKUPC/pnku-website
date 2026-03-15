import { Alert } from 'antd';
import React, { Suspense, lazy, useCallback, useEffect, useState } from 'react';
import { ErrorBoundaryContext, useErrorBoundary } from 'react-use-error-boundary';

import { Loading } from '@/components/Loading';

type RemoteComponentProps = {
    componentName: string;
    componentUrl: string;
    fallback?: React.ComponentType;
    [key: string]: any;
};

// 动态导入远程组件
const loadRemoteComponent = async (url: string) => {
    const module = await import(/* @vite-ignore */ url);
    return module.default;
};

function ErrorComponent({ message }: { message: string }) {
    return <Alert type="error" message="组件加载错误" description={message} />;
}

function RemoteComponentErrorHandler({ children }: { children: React.ReactNode }) {
    const [error] = useErrorBoundary();
    if (error) {
        console.error(error);
        return <ErrorComponent message={`组件加载遇到错误，如果您一直遇到此问题，请联系工作人员处理！`} />;
    }
    return children;
}

function RemoteComponentErrorBoundary({ children }: { children: React.ReactNode }) {
    return (
        <ErrorBoundaryContext>
            <RemoteComponentErrorHandler>{children}</RemoteComponentErrorHandler>
        </ErrorBoundaryContext>
    );
}

export function RemoteComponent({ componentName, componentUrl, fallback: Fallback, ...props }: RemoteComponentProps) {
    const [RemoteComp, setRemoteComp] = useState<React.ComponentType<any> | null>(null);
    const [loading, setLoading] = useState(true);
    console.log('RemoteComp');
    console.log({
        componentName,
        componentUrl,
        props,
    });

    const loadComponent = useCallback(async () => {
        try {
            setLoading(true);

            // 编译时会自动消除这部分代码，VITE_REMOTE_COMPONENT_DEV_MODE 不为 true 时不会打包 devComponents
            if (import.meta.env.VITE_REMOTE_COMPONENT_DEV_MODE === 'true') {
                // 开发环境的组件映射
                console.log('loading remote component in dev mode');

                const NotFoundComponent = () => (
                    <ErrorComponent message="组件不存在，请检查组件名称是否正确以及是否在开发环境中注册了此组件。" />
                );

                const DevComponent = lazy(() => import(`../remote/${componentName}/index.tsx`));

                if (DevComponent) {
                    setRemoteComp(DevComponent);
                } else {
                    setRemoteComp(() => NotFoundComponent);
                }
            } else {
                const component = await loadRemoteComponent(componentUrl);
                setRemoteComp(() => component);
            }
        } catch (err) {
            console.error('Failed to load remote component:', err);
            const ErrorComp = () => (
                <ErrorComponent message={`组件加载遇到错误，如果您一直遇到此问题，请联系工作人员处理！`} />
            );
            setRemoteComp(() => ErrorComp);
        } finally {
            setLoading(false);
        }
    }, [componentName, componentUrl]);

    useEffect(() => {
        loadComponent();
    }, [loadComponent]);

    if (loading) {
        return <Loading />;
    }

    if (!RemoteComp) {
        return Fallback ? (
            <Fallback />
        ) : (
            <ErrorComponent message={`组件加载遇到错误，如果您一直遇到此问题，请联系工作人员处理！`} />
        );
    }

    console.log(RemoteComp);

    return (
        <RemoteComponentErrorBoundary>
            <Suspense fallback={<Loading />}>
                <RemoteComp {...props} />
            </Suspense>
        </RemoteComponentErrorBoundary>
    );
}
