import type { TableColumnsType, TableProps } from 'antd';
import { ComponentType, Suspense, lazy } from 'react';

import { AppErrorBoundary } from '@/app/AppErrorBoundary.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';

type AnyObject = Record<PropertyKey, any>;

function TableLoader<RecordType extends AnyObject>(props: TableProps<RecordType>) {
    const Table = lazy<ComponentType<TableProps<RecordType>>>(() => import('@/components/lazy/Table'));
    return (
        <AppErrorBoundary>
            <Suspense fallback={<Loading />}>
                <Table {...props} />
            </Suspense>
        </AppErrorBoundary>
    );
}

export { TableLoader };
export type { TableProps, TableColumnsType };
