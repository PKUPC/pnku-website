import { FlagOutlined } from '@ant-design/icons';
import { Alert, Input, message } from 'antd';
import React, { useContext, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import NotFound from '@/app/NotFound.tsx';
import { FancySlimContainer } from '@/components/FancySlimContainer';
import { Footer } from '@/components/Footer.tsx';
import { TemplateFile } from '@/components/Template';
import { WishConfirmModal } from '@/components/WishConfirmModal';
import { GameInfoContext, GameStatusContext, useSuccessGameInfo } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';

const TARGET_CODE: string[] = [
    'ArrowUp',
    'ArrowUp',
    'ArrowDown',
    'ArrowDown',
    'ArrowLeft',
    'ArrowRight',
    'ArrowLeft',
    'ArrowRight',
    'KeyB',
    'KeyA',
];

const Toy = () => {
    const [keySequence, setKeySequence] = useState<string[]>([]);
    const [done, setDone] = useState(false);
    const [messageApi, contextHolder] = message.useMessage();

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (done) return;
            setKeySequence((prevKeys) => {
                const newKeys = [...prevKeys, event.code].slice(-TARGET_CODE.length);
                console.log(newKeys);
                return newKeys;
            });
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [done, messageApi]);

    useEffect(() => {
        if (keySequence.join('') === TARGET_CODE.join('')) {
            messageApi.success('↑↑↓↓←→←→BA!').then();
            setDone(true);
            setKeySequence([]);
        }
    }, [keySequence, messageApi]);

    return contextHolder;
};

function IntroAnswerInput() {
    const [messageApi, contextHolder] = message.useMessage();
    const [open, setOpen] = useState(false);
    const [inputAnswer, setInputAnswer] = useState('');
    const wishArgs = useMemo(() => ({ content: inputAnswer }), [inputAnswer]);
    const { reloadInfo } = useContext(GameInfoContext);
    const { setNeedReloadArea } = useContext(GameStatusContext);
    const navigate = useNavigate();

    const doSubmit = () => {
        if (!inputAnswer) {
            messageApi.error({ content: '提交内容不能为空！', key: 'DO_SUBMIT', duration: 4 }).then();
            return;
        }
        if (inputAnswer.toUpperCase() === 'MYGO') {
            messageApi.success({ content: 'MyGO!!!!!', key: 'MYGO' }).then();
            navigate('/area?dst=intro&mygo=run');
            return;
        }
        setOpen(true);
    };

    return (
        <div>
            {contextHolder}
            <Toy />
            <Input.Search
                size="large"
                addonBefore={'提交答案：'}
                placeholder={'... ...'}
                enterButton={
                    <>
                        <FlagOutlined /> 提交
                    </>
                }
                onChange={(e) => {
                    setInputAnswer(e.target.value);
                }}
                value={inputAnswer}
                onSearch={doSubmit}
                onPressEnter={() => {}}
            />
            <WishConfirmModal
                wishParam={{
                    endpoint: 'game/game_start',
                    payload: wishArgs,
                }}
                open={open}
                setOpen={setOpen}
                confirmContent={'确定提交吗？'}
                onFinish={(res) => {
                    setInputAnswer('');
                    if (res.need_reload_info) {
                        reloadInfo();
                        setNeedReloadArea(true);
                    }
                }}
            />
        </div>
    );
}

function IntroBody({ areaData }: { areaData: Wish.Game.IntroArea }) {
    const info = useSuccessGameInfo();

    const themeColors = {
        '--main-color': areaData.extra.mainColor,
        '--sub-color': areaData.extra.subColor,
    } as React.CSSProperties;

    const containerBgStyles: React.CSSProperties = {
        backgroundImage: `url(${areaData.extra.areaImage})`,
        backgroundPositionX: `${areaData.extra.bgFocusPositionX}%`,
        backgroundPositionY: `${areaData.extra.bgFocusPositionY}%`,
    };

    let component;
    if (import.meta.env.VITE_ARCHIVE_MODE === 'true') {
        component = <IntroAnswerInput />;
    } else {
        if (!info.team) component = <Alert type={'info'} showIcon={true} message={'您还不在任何队伍中，请先组队！'} />;
        else component = <IntroAnswerInput />;
    }

    return (
        <div className="relative w-full" style={themeColors}>
            <div
                className="relative w-full h-[80vh] z-0"
                style={{
                    ...containerBgStyles,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    pointerEvents: 'none',
                }}
            />
            <FancySlimContainer title={areaData.extra.areaTitle} extraClassName="relative -mt-[40vh] z-[1]">
                <FancySlimContainer.SubTitle subTitle={areaData.extra.areaSubtitle} />
                <TemplateFile name={areaData.template} />
                {component}
                {info.team?.gaming && <br />}
                {info.team?.gaming && <Alert type={'success'} showIcon={true} message={'你的队伍已开始游戏。'} />}
                <br />
            </FancySlimContainer>
            <Footer />
        </div>
    );
}

export function Intro({ areaData }: { areaData: Wish.Game.IntroArea }) {
    const info = useSuccessGameInfo();
    if (
        import.meta.env.VITE_ARCHIVE_MODE !== 'true' &&
        (!info.user || (info.user.group !== 'staff' && !info.game.isPrologueUnlock))
    )
        return <NotFound />;
    return <IntroBody areaData={areaData} />;
}
