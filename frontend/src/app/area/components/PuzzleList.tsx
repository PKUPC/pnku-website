import { Empty, Tooltip } from 'antd';
import React, { Fragment, useLayoutEffect, useRef } from 'react';
import { Link } from 'react-router-dom';

import { DifficultyStatus } from '@/app/area/components/DifficultyStatus';
import { PuzzleIcon } from '@/components/DynamicIcons';
import { Wish } from '@/types/wish.ts';

import styles from './PuzzleList.module.css';

export function PuzzleList({
    puzzleList,
    currentKey,
    rowStyle,
}: {
    puzzleList: Wish.Game.PuzzleInfo[];
    currentKey?: string;
    rowStyle?: React.CSSProperties;
}) {
    const puzzleListRef = useRef<HTMLDivElement>(null);
    useLayoutEffect(() => {
        if (puzzleListRef.current) {
            const subColor = getComputedStyle(puzzleListRef.current).getPropertyValue('--sub-color').trim();
            const hslParts = subColor.match(/[\d.]+/g);
            if (!hslParts || hslParts.length !== 3) {
                return;
            }

            const h = parseFloat(hslParts[0]);
            const s = parseFloat(hslParts[1]);
            let l = parseFloat(hslParts[2]);

            // Calculate the new lightness value
            l = Math.max(0, l - l * 0.05);

            const darkerHSL = `hsl(${h}, ${s}%, ${l}%)`;

            puzzleListRef.current.style.setProperty('--sub-color-dark', darkerHSL);
        }
    }, []);
    return (
        <div ref={puzzleListRef} className={styles.puzzleList}>
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
