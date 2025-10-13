import { FlagOutlined } from '@ant-design/icons';
import { Input, message } from 'antd';
import { useContext, useLayoutEffect, useMemo, useState } from 'react';
import { mutate } from 'swr';

import { WishConfirmModal } from '@/components/WishConfirmModal';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { NeverError } from '@/errors';
import { useCooldown } from '@/hooks/useCooldown';
import { GameInfoContext, GameStatusContext } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';
import { format_ts_to_HMS } from '@/utils.ts';

export function PuzzleAnswerInput({ puzzle, reload }: { puzzle: Wish.Puzzle.PuzzleDetailData; reload?: () => void }) {
    const [inputAnswer, setInputAnswer] = useState('');
    const [submitAnswer, setSubmitAnswer] = useState('');
    const [disableInput, setDisableInput] = useState(false);

    const [open, setOpen] = useState(false);
    const [messageApi, contextHolder] = message.useMessage();
    const { setNeedReloadArea } = useContext(GameStatusContext);
    const [cooling, countdown] = useCooldown(puzzle.cold_down_ts ?? 0);

    const wishArgs = useMemo(() => ({ puzzle_key: puzzle.key, content: submitAnswer }), [submitAnswer, puzzle.key]);
    const { info, reloadInfo } = useContext(GameInfoContext);

    if (info.status !== 'success') throw new NeverError();

    console.log('rendering PuzzleAnswerInput');

    useLayoutEffect(() => {
        console.log('PuzzleAnswerInput -> useLayoutEffect: Add window.puzzleApi');
        window.puzzleApi = {
            setDisableInput: (v: boolean) => setDisableInput(v),
            setSubmitAnswer: (v: string) => setSubmitAnswer(v),
            setInputAnswer: (v: string) => setInputAnswer(v),
            reloadPuzzleDetail: () => {
                mutate({
                    endpoint: 'puzzle/get_detail',
                    payload: { puzzle_key: puzzle.key },
                }).then();
            },
        };
        console.log('Add window.puzzleApi done!');
        return () => {
            console.log('remove window.puzzleApi');
            window.puzzleApi = undefined;
            setDisableInput(false);
            setSubmitAnswer('');
            setInputAnswer('');
        };
    }, [puzzle.key]);

    console.log(`input answer: ${inputAnswer}`);
    console.log(`submit answer: ${submitAnswer}`);

    const doSubmit = (ans: string) => {
        if (!ans) {
            messageApi.error({ content: '提交内容不能为空！', key: 'DO_SUBMIT', duration: 3 }).then();
            return;
        }
        setOpen(true);
    };

    let content;
    if (info.user && info.user.group === 'staff')
        content = <>你是工作人员，可以验证答案并看到提交记录，但是谜题不会变为通过状态。</>;
    else if (ARCHIVE_MODE)
        content = (
            <>
                目前处于归档模式，你可以在这里验证你的答案。
                <br />
                你填写的答案为：{inputAnswer}
            </>
        );
    else
        content = (
            <>
                你填写的答案为：{inputAnswer}
                <br />
                请确认无误后提交答案。
            </>
        );

    return (
        <div>
            {contextHolder}
            <Input.Search
                size="large"
                addonBefore={'答案：'}
                placeholder={cooling ? '冷却时间：' + format_ts_to_HMS(countdown) : '... ...'}
                enterButton={
                    <>
                        <FlagOutlined /> 提交
                    </>
                }
                onChange={(e) => {
                    if (disableInput) return;
                    setInputAnswer(e.target.value);
                    setSubmitAnswer(e.target.value);
                }}
                value={cooling ? '' : inputAnswer}
                onSearch={doSubmit}
                disabled={cooling}
                onPressEnter={() => {}}
            />
            <WishConfirmModal
                wishParam={{
                    endpoint: 'puzzle/submit_answer',
                    payload: wishArgs,
                }}
                open={open}
                setOpen={setOpen}
                confirmContent={content}
                onFinish={(res) => {
                    if (!disableInput) setInputAnswer('');
                    if (res.need_reload) {
                        reloadInfo();
                        setNeedReloadArea(true);
                        if (reload) reload();
                    }
                }}
            />
        </div>
    );
}
