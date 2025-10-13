import type { TableColumnsType, TablePaginationConfig, TableProps } from 'antd';
import { ComponentType, Suspense, lazy, memo } from 'react';

import { AppErrorBoundary } from '@/app/AppErrorBoundary.tsx';
import { Loading } from '@/components/Loading.tsx';

type AnyObject = Record<PropertyKey, any>;

const LazyTable = lazy<ComponentType<TableProps<AnyObject>>>(() => import('@/components/lazy/Table'));

function TableLoaderComponent<RecordType extends AnyObject>(props: TableProps<RecordType>) {
    return (
        <AppErrorBoundary>
            <Suspense fallback={<Loading />}>
                <LazyTable {...props} />
            </Suspense>
        </AppErrorBoundary>
    );
}
const TableLoader = memo(TableLoaderComponent) as typeof TableLoaderComponent;

export { TableLoader };
export type { TableProps, TableColumnsType, TablePaginationConfig };
