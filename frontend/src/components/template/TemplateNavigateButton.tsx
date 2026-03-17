import { Button } from 'antd';
import { CSSProperties } from 'react';
import { useNavigate } from 'react-router';

export function TemplateNavigateButton({
    url,
    text,
    style,
    className,
    type,
    size,
}: {
    url: string;
    text: string;
    style?: CSSProperties;
    className?: string;
    type: 'primary' | 'default' | 'link' | 'text' | 'dashed';
    size?: 'large' | 'middle' | 'small';
}) {
    const navigate = useNavigate();
    return (
        <Button className={className} style={style} type={type} onClick={() => navigate(url)} size={size}>
            {text}
        </Button>
    );
}
