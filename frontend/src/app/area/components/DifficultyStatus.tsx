import { Progress } from 'antd';

import { detectZoom } from '@/utils.ts';

import styles from './DifficultyStatus.module.css';

export function DifficultyStatus({
    totalNum,
    greenNum,
    redNum,
}: {
    totalNum: number;
    greenNum: number;
    redNum: number;
}) {
    const greenColor = '#64c43b';
    const redColor = '#ff8080';

    const strokeColorList = [];
    for (let i = 0; i < greenNum; i++) strokeColorList.push(greenColor);
    for (let i = 0; i < redNum; i++) strokeColorList.push(redColor);

    let percent = 0;
    if (redNum + greenNum > 0) percent = ((redNum + greenNum - 0.0001) / totalNum) * 100;
    const alignedMargin = Math.round(detectZoom() * 3) / detectZoom();
    const alignedWidth = Math.round(detectZoom() * 4) / detectZoom();

    return (
        <Progress
            className={styles.difficultyStatus}
            strokeColor={strokeColorList}
            percent={percent}
            steps={totalNum}
            size="small"
            trailColor={'#d2d2d2'}
            format={() => null}
            style={{
                // @ts-ignore
                '--aligned-width': alignedWidth + 'px',
                '--aligned-margin': alignedMargin + 'px',
            }}
        />
    );
}
