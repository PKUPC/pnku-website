import { CheckOutlined, CopyOutlined } from '@ant-design/icons';
import { Button, message } from 'antd';
import { useCallback, useEffect, useState } from 'react';

import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';

import styles from './CopyButton.module.css';

function SingleCopyButton({
    puzzleKey,
    clipboardData,
}: {
    puzzleKey: string;
    clipboardData: Wish.Puzzle.ClipboardData;
}) {
    const [messageApi, contextHolder] = message.useMessage();
    const [copied, setCopied] = useState(false);
    const [copyLoading, setCopyLoading] = useState(false);
    const copyIcon = copied ? <CheckOutlined /> : <CopyOutlined />;

    useEffect(() => {
        setCopied(false);
    }, [puzzleKey, clipboardData]);

    const handleCopy = useCallback(async () => {
        if (!navigator.clipboard || !navigator.clipboard.writeText) {
            messageApi
                .error({ content: '您的浏览器不支持复制到剪切板！', key: 'copy-button-error', duration: 3 })
                .then();
            return;
        }
        setCopyLoading(true);
        const res = await wish({
            endpoint: 'puzzle/get_clipboard',
            payload: {
                puzzle_key: puzzleKey,
                clipboard_idx: clipboardData.idx,
                clipboard_type: clipboardData.type,
            },
        });
        setCopyLoading(false);
        if (res.status === 'error') {
            messageApi.error({ content: res.message, key: 'copy-button-error', duration: 3 }).then();
            return;
        }
        if (res.status === 'success') {
            try {
                const clipboardItems: Record<string, Blob> = {};

                if (clipboardData.type === 'tencent-html' || clipboardData.type === 'google-html') {
                    clipboardItems['text/html'] = new Blob([res.data], { type: 'text/html' });
                } else {
                    clipboardItems['text/plain'] = new Blob([res.data], { type: 'text/plain' });
                }
                const clipboardItem = new ClipboardItem(clipboardItems);
                await navigator.clipboard.write([clipboardItem]);
                setCopied(true);
                return;
            } catch (err) {
                console.error(err);
                messageApi.error({ content: '复制失败！', key: 'copy-button-error', duration: 3 }).then();
                return;
            }
        }
        setCopyLoading(false);
    }, [clipboardData, messageApi, puzzleKey]);

    return (
        <div>
            {contextHolder}
            <Button icon={copyIcon} loading={copyLoading} onClick={handleCopy}>
                {clipboardData.type === 'tencent-html'
                    ? '复制到腾讯文档'
                    : clipboardData.type === 'google-html'
                      ? '复制到 Google Spreadsheets'
                      : '复制到剪切板'}
            </Button>
        </div>
    );
}

export default function CopyButton({
    puzzleKey,
    clipboardData,
}: {
    puzzleKey: string;
    clipboardData: Wish.Puzzle.ClipboardData[];
}) {
    return (
        <div>
            <div className={styles.copyButton}>
                {clipboardData.map((item) => (
                    <SingleCopyButton key={item.idx} puzzleKey={puzzleKey} clipboardData={item} />
                ))}
            </div>
            {/* TODO: 目前只用到了复制到腾讯文档，如果用到其它类型的复制，需要修改这里的提示 */}
            <div style={{ color: '#838383', fontStyle: 'italic' }}>
                复制内容需要直接在腾讯文档粘贴，复制到 Google Spreadsheets 可能会丢失某些格式，需要手动更改
            </div>
        </div>
    );
}
