import { Tag } from 'antd';
import React from 'react';

interface GeneralTag {
    children: React.ReactNode;
    color?: string;
    bordered?: boolean;
}

export function GeneralTag({ children, color, bordered }: GeneralTag) {
    return (
        <Tag bordered={bordered ?? true} color={color}>
            {children}
        </Tag>
    );
}
