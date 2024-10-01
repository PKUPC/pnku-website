import { type GetProp, type TablePaginationConfig, type TableProps } from 'antd';
import { SorterResult } from 'antd/es/table/interface';

export interface TableParams {
    pagination?: TablePaginationConfig;
    sortField?: SorterResult<never>['field'];
    sortOrder?: SorterResult<never>['order'];
    filters?: Parameters<GetProp<TableProps, 'onChange'>>[1];
}

export function saveToSessionStorage(name: string, data: TableParams) {
    console.log(`save ${name} to sessionStorage`);
    sessionStorage.setItem(name, JSON.stringify(data));
}

export function getFromSessionStorage(name: string): TableParams {
    console.log(`get ${name} from sessionStorage`);
    const data = sessionStorage.getItem(name);
    if (data) {
        const parsedData = JSON.parse(data);
        console.log(data);
        return {
            pagination: parsedData.pagination !== undefined ? parsedData.pagination : undefined,
            sortField: parsedData.sortField !== undefined ? parsedData.sortField : undefined,
            sortOrder: parsedData.sortOrder !== undefined ? parsedData.sortOrder : undefined,
            filters: parsedData.filters !== undefined ? parsedData.filters : undefined,
        };
    }
    return {
        pagination: undefined,
        sortField: undefined,
        sortOrder: undefined,
        filters: undefined,
    };
}
