import { Empty } from 'antd';
import React from 'react';
import { Link } from 'react-router';

import { FancySlimContainer } from '@/components/FancySlimContainer';
import { Wish } from '@/types/wish.ts';

import styles from './StoryList.module.css';

function GroupList({ storyGroup }: { storyGroup: Wish.Game.StoryGroup }) {
    return (
        <div>
            <FancySlimContainer.SubTitle subTitle={storyGroup.subtitle} />
            <div>
                {storyGroup.list.length === 0 ? (
                    <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无情报" />
                ) : (
                    storyGroup.list.map((item) => (
                        <Link
                            to={`/story?key=${item.template}`}
                            style={{ display: 'flex' }}
                            key={item.template}
                            className={styles.storyItem}
                        >
                            <div className={styles.storyTitleText}>{item.title}</div>
                        </Link>
                    ))
                )}
            </div>
        </div>
    );
}

export function StoryList({ storyGroups }: { storyGroups: Wish.Game.StoryGroup[] }) {
    const containerStyles = {
        '--main-color': 'hsl(220.85, 85.45%, 67.65%)',
        '--sub-color': 'hsl(220.85, 85.45%, 67.65%)',
        width: '100%',
    } as React.CSSProperties;

    return (
        <div
            style={{
                maxWidth: 850,
                margin: 'auto',
            }}
        >
            <FancySlimContainer title={'情报一览'} style={containerStyles}>
                <div className={styles.storyList}>
                    {storyGroups.map((item) => (
                        <GroupList storyGroup={item} key={item.subtitle} />
                    ))}
                </div>
            </FancySlimContainer>
        </div>
    );
}
