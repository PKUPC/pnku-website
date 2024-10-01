import { Tag } from 'antd';

export function TeamStatusTag({ data }: { data: { color: string; text: string } }) {
    if (data.color === 'default') return <Tag>{data.text}</Tag>;
    return (
        // <Tag color={"blue"}>{data.text}</Tag>
        <Tag color={data.color}>{data.text}</Tag>
    );
}
