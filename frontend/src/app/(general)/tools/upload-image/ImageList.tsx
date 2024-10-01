import { CheckOutlined, CopyOutlined } from '@ant-design/icons';
import { Button, Col, Image, Row } from 'antd';
import { useState } from 'react';
import { CopyToClipboard } from 'react-copy-to-clipboard';

import { Wish } from '@/types/wish.ts';

function CopyButton({ url }: { url: string }) {
    const [copied, setCopied] = useState(false);
    const copyIcon = copied ? <CheckOutlined /> : <CopyOutlined />;
    return (
        <CopyToClipboard
            text={`![](${url})`}
            options={{ format: 'text/plain' }}
            onCopy={() => {
                setCopied(true);
                setTimeout(() => {
                    setCopied(false);
                }, 3000);
            }}
        >
            <Button icon={copyIcon} size={'middle'} style={{ width: '100%' }}>
                复制 Markdown 链接
            </Button>
        </CopyToClipboard>
    );
}

export function ImageList({ data }: { data: Wish.Upload.UploadedImageItem[] }) {
    const { protocol, hostname, port } = window.location;
    const baseUrl = `${protocol}//${hostname}${port ? ':' + port : ''}`;
    return (
        <div>
            <Row>
                {data.map((item, index) => {
                    return (
                        <Col key={index} xl={8} sm={12} xs={24}>
                            <div className="w-60 m-auto rounded-box bordered border-[1px]">
                                <div className="w-full">
                                    <Image src={item.url} alt={'image'} height={'18.75rem'} width={'15rem'} />
                                </div>
                                <div className="m-auto w-48 pt-2 pb-4">
                                    <CopyButton url={baseUrl + item.url} />
                                </div>
                            </div>
                        </Col>
                    );
                })}
            </Row>
        </div>
    );
}
