import { CheckOutlined, CopyOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import { useState } from 'react';
import { CopyToClipboard } from 'react-copy-to-clipboard';

import { Wish } from '@/types/wish.ts';

import styles from './CopyButton.module.css';

export default function CopyButton({ clipboardData }: { clipboardData: Wish.Puzzle.ClipboardData[] }) {
    const [copied, setCopied] = useState(false);
    const copyIcon = copied ? <CheckOutlined /> : <CopyOutlined />;
    return (
        <div>
            <div className={styles.copyButton}>
                {clipboardData.map((item) => (
                    <CopyToClipboard
                        key={item.type}
                        text={item.content}
                        options={{
                            format:
                                item.type === 'tencent-html' || item.type === 'google-html'
                                    ? 'text/html'
                                    : 'text/plain',
                        }}
                        onCopy={() => {
                            setCopied(true);
                            setTimeout(() => {
                                setCopied(false);
                            }, 5000);
                        }}
                    >
                        <Button icon={copyIcon}>
                            {item.type === 'tencent-html'
                                ? '复制到腾讯文档'
                                : item.type === 'google-html'
                                  ? '复制到 Google Spreadsheets'
                                  : '复制到剪切板'}
                        </Button>
                    </CopyToClipboard>
                ))}
            </div>
            <div style={{ color: '#838383', fontStyle: 'italic' }}>
                复制内容需要直接在腾讯文档粘贴，复制到 Google Spreadsheets 可能会丢失某些格式，需要手动更改
            </div>
        </div>
    );
}
