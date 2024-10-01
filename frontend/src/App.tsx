import { ConfigProvider, message } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import React, { ReactNode, useContext, useEffect } from 'react';
import { SWRConfig } from 'swr';

import { WishError } from '@/components/WishError.tsx';
import { GameInfoContextProvider } from '@/logic/GameInfoContext';
import { GameStatusContextProvider } from '@/logic/GameStatusContext';
import { GameSettingContextProvider } from '@/logic/SiteSettingContext.tsx';
import { WindowInfoContextProvider } from '@/logic/WindowInfoContext.tsx';
import { PushDaemonWrapper } from '@/logic/WsDaemon';
import { GameInfoContext, useTheme } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish.ts';
import { setup } from '@/setup.ts';
import { mixColor } from '@/utils.ts';

import './globals.scss';

setup();

function InnerLayout({ children }: { children: React.ReactNode }) {
    const { info, reloadInfo } = useContext(GameInfoContext);

    console.log(info);
    if (info.status === 'error') return <WishError res={info} reload={reloadInfo} />;
    return children;
}

function App({ children }: { children: ReactNode }) {
    const [messageApi, contextHolder] = message.useMessage();
    const { color, style } = useTheme();

    console.log(style);

    useEffect(() => {
        window.recaptchaOptions = {
            useRecaptchaNet: true,
        };
        window.wish = wish;
        window.messageApi = messageApi;
        console.log(window.rem);
        console.log(window.ram);
    }, [messageApi]);

    return (
        <ConfigProvider
            locale={zhCN}
            theme={{
                cssVar: true,
                hashed: false,
                token: {
                    colorBgBase: color.base100,
                    colorBgContainer: color.base100,
                    colorTextBase: color.baseContent,
                    colorPrimary: color.primary,
                    colorPrimaryBg: mixColor(color.base100, color.primary, 0.1),
                    colorPrimaryBorder: mixColor(color.base300, color.primary, 0.7),
                    colorInfo: color.info,
                    colorInfoBg: mixColor(color.base100, color.info, 0.1),
                    colorInfoBorder: mixColor(color.base300, color.info, 0.7),
                    colorError: color.error,
                    colorErrorBg: mixColor(color.base100, color.error, 0.1),
                    colorErrorBorder: mixColor(color.base300, color.error, 0.7),
                    colorSuccess: color.success,
                    colorSuccessBg: mixColor(color.base100, color.success, 0.1),
                    colorSuccessBorder: mixColor(color.base300, color.success, 0.7),
                    colorWarning: color.warning,
                    colorWarningBg: mixColor(color.base100, color.warning, 0.1),
                    colorWarningBorder: mixColor(color.base300, color.warning, 0.7),
                    borderRadius: style.roundedBtnPx,
                    borderRadiusLG: style.roundedBoxPx,
                    borderRadiusSM: style.roundedBtnPx,
                },
            }}
        >
            <SWRConfig
                value={{
                    refreshInterval: 10 * 60 * 1000, // 自动刷新时间间隔
                    keepPreviousData: true, // 自动返回之前的结果
                    dedupingInterval: 10 * 1000, // 合并 5s 内的请求
                    errorRetryCount: 1, // 最大重试次数
                }}
            >
                <GameInfoContextProvider>
                    <GameSettingContextProvider>
                        <GameStatusContextProvider>
                            <WindowInfoContextProvider>
                                <PushDaemonWrapper>
                                    <InnerLayout>
                                        <div className={'global-container'} id={'global-container'}>
                                            {contextHolder}
                                            {children}
                                        </div>
                                    </InnerLayout>
                                </PushDaemonWrapper>
                            </WindowInfoContextProvider>
                        </GameStatusContextProvider>
                    </GameSettingContextProvider>
                </GameInfoContextProvider>
            </SWRConfig>
        </ConfigProvider>
    );
}

export default App;
