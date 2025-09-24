import { HistoryOutlined, SyncOutlined } from '@ant-design/icons';
import { Button, message } from 'antd';

import TimestampAgo from '@/components/TimestampAgo';
import { useReloadButton } from '@/hooks/useReloadButton';

export function BoardReloader({ reload }: { reload: () => void }) {
    const [lastReload, markReload, reloadButtonRef] = useReloadButton(3);
    const [messageApi, messageContext] = message.useMessage();
    // TODO: 修复响应式问题
    console.log(lastReload);
    return (
        <div className="flex flex-row justify-between items-center mb-3 h-9 pl-1">
            {messageContext}
            <div>
                <HistoryOutlined />{' '}
                {lastReload !== 0 && (
                    <>
                        <TimestampAgo ts={lastReload} />
                        更新
                    </>
                )}
            </div>
            <div>
                <Button
                    type="link"
                    ref={reloadButtonRef}
                    onClick={() => {
                        messageApi
                            .success({ content: '已刷新排行榜', key: 'Board.ManualLoadData', duration: 2 })
                            .then();
                        markReload();
                        reload();
                    }}
                >
                    <SyncOutlined /> 刷新排行榜
                </Button>
            </div>
        </div>
    );
}
