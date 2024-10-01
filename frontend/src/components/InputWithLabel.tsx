import { Col, Row } from 'antd';
import { ReactNode } from 'react';

export function InputWithLabel({
    children,
    label,
    extra,
}: {
    children: ReactNode;
    label: ReactNode;
    extra?: ReactNode;
}) {
    return (
        <Row gutter={{ sm: 8, md: 16 }} align="top">
            <Col xs={24} sm={7} className="flex sm:justify-end mb-2 sm:mb-0 h-8 items-center">
                {label}
            </Col>
            <Col xs={24} sm={16}>
                {children}
                {extra && <div className="text-left text-opacity-70 text-base-content mt-1">{extra}</div>}
            </Col>
        </Row>
    );
}
