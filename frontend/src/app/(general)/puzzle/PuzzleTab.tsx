import { RightCircleOutlined } from '@ant-design/icons';
import { Alert } from 'antd';
import { useSWRConfig } from 'swr';

import CopyButton from '@/app/(general)/puzzle/components/CopyButton';
import { PuzzleAction } from '@/app/(general)/puzzle/components/PuzzleAction';
import { PuzzleAnswerInput } from '@/app/(general)/puzzle/components/PuzzleAnswerInput';
import { TemplateStr } from '@/components/Template';
import { Wish } from '@/types/wish.ts';

import styles from './PuzzleTab.module.scss';

export function PuzzleBody({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    const puzzleBody = <TemplateStr name={'puzzle-desc'}>{puzzleData.desc}</TemplateStr>;
    const { mutate } = useSWRConfig();

    return (
        <>
            <div className={styles.puzzleBody}>{puzzleBody}</div>

            {puzzleData.actions.map((action, idx) => (
                <p key={idx} className={styles.puzzleAction}>
                    <RightCircleOutlined /> <PuzzleAction puzzle={puzzleData} action={action} />
                </p>
            ))}

            {puzzleData.clipboard && <CopyButton clipboardData={puzzleData.clipboard} />}

            <br />

            {puzzleData.status === 'passed' && (
                <>
                    <Alert
                        type={'success'}
                        showIcon={true}
                        message={
                            <>
                                你的队伍已通过此题
                                {/*{puzzleData.pass_ts && <span style={{*/}
                                {/*    fontStyle: "italic",*/}
                                {/*    color: "#838383"*/}
                                {/*}}>({format_ts(puzzleData.pass_ts)})</span>}*/}
                                {puzzleData.answer_display && (
                                    <span>，这道题的正确答案是：{puzzleData.answer_display}</span>
                                )}
                            </>
                        }
                    />
                    <br />
                </>
            )}

            <PuzzleAnswerInput
                puzzle={puzzleData}
                reload={() => {
                    mutate({
                        endpoint: 'puzzle/get_detail',
                        payload: { puzzle_key: puzzleData.key },
                    }).then();
                    mutate({
                        endpoint: 'puzzle/get_submissions',
                        payload: { puzzle_key: puzzleData.key },
                    }).then();
                }}
            />
        </>
    );
}

export function PuzzleTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    return <PuzzleBody puzzleData={puzzleData} />;
}
