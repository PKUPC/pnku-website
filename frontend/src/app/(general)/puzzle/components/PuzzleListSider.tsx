import { Empty, Tooltip } from 'antd';
import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';

import { DifficultyStatus } from '@/app/area/components/DifficultyStatus';
import { PuzzleIcon } from '@/components/DynamicIcons';
import { Wish } from '@/types/wish.ts';

import styles from './PuzzleListSider.module.css';

export function PuzzleListSider({
    puzzleList,
    currentKey,
    rowStyle,
}: {
    puzzleList: Wish.Game.PuzzleInfo[];
    currentKey?: string;
    rowStyle?: React.CSSProperties;
}) {
    return (
        <div className={styles.puzzleList}>
            {puzzleList.map((puzzle) => {
                const isDisabled = puzzle.puzzle_key.length == 0;
                const isSelect = currentKey === puzzle.puzzle_key;

                let puzzleTitleElement = (
                    <div className={'puzzle-title'}>
                        <PuzzleIcon status={puzzle.status} />{' '}
                        <span className={'puzzle-title-text'}>{puzzle.title}</span>
                    </div>
                );
                if (isDisabled) {
                    puzzleTitleElement = (
                        <Tooltip title={'这道题暂时无法访问，请先挑战其他题目。'} placement={'left'}>
                            {puzzleTitleElement}
                        </Tooltip>
                    );
                }
                return (
                    <Fragment key={puzzle.puzzle_key !== '' ? puzzle.puzzle_key : puzzle.title}>
                        <Link
                            to={`/puzzle?key=${puzzle.puzzle_key}`}
                            className={
                                (isDisabled ? 'puzzle-row-disabled' : 'puzzle-row') +
                                (isSelect ? ' puzzle-row-select' : '')
                            }
                            style={{ display: 'flex', ...rowStyle }}
                            // replace={true}
                            onClick={(event) => {
                                if (isDisabled || isSelect) {
                                    event.preventDefault();
                                    return;
                                }
                            }}
                        >
                            {puzzleTitleElement}
                            <Tooltip
                                title={
                                    puzzle.total_attempted + ' 支队伍尝试，其中 ' + puzzle.total_passed + ' 支队伍通过'
                                }
                                placement={'right'}
                            >
                                <div className="portal-puzzle-col-progress">
                                    {/*<div className={"text-rate"}>*/}
                                    {/*    {puzzle.total_passed} / {puzzle.total_attempted}*/}
                                    {/*</div>*/}
                                    <DifficultyStatus
                                        totalNum={puzzle.difficulty_status.total_num}
                                        greenNum={puzzle.difficulty_status.green_num}
                                        redNum={puzzle.difficulty_status.red_num}
                                    />
                                </div>
                            </Tooltip>
                        </Link>
                    </Fragment>
                );
            })}

            {puzzleList.length === 0 && <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无题目" />}
        </div>
    );
}
