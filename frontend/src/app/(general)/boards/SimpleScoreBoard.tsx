import { TeamInfo } from '@/app/(general)/boards/components/TeamInfo';
import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

import styles from './SimpleScoreBoard.module.css';

function PassedStatus({ team }: { team: Wish.Game.SimpleBoardItem }) {
    return (
        <div className={styles.scoreBoardPassedStatus}>
            解出 <b>{team.s}</b> 题
            <br />
            {team.s > 0 && format_ts(team.lts)}
        </div>
    );
}

// TODO: 参考 FullScoreBoard 进行优化。因为目前暂时用不上这个榜，所以就先没做。
export function SimpleScoreBoard({ data }: { data: Wish.Game.SimpleBoard }) {
    console.log(data);
    const columns: TableColumnsType<Wish.Game.SimpleBoardItem> = [
        {
            className: styles.largeRank,
            title: '排名',
            key: 'rank',
            dataIndex: 'rank',
        },
        {
            className: styles.smallRank,
            title: '#',
            key: 'small-rank',
            dataIndex: 'rank',
        },
        {
            className: styles.largeTeam,
            title: '队伍',
            key: 'name',
            render: (_text, record: Wish.Game.SimpleBoardItem) => <TeamInfo team={record} />,
        },
        {
            className: styles.smallTeam,
            title: '队伍',
            key: 'small-name',
            render: (_text, record: Wish.Game.SimpleBoardItem) => <TeamInfo team={record} maxLength={25} />,
        },
        {
            className: styles.passed,
            title: '解出题数',
            key: 'passed',
            render: (_text, record: Wish.Game.SimpleBoardItem) => <PassedStatus team={record} />,
        },
    ];

    return (
        <div>
            <Table<Wish.Game.SimpleBoardItem>
                className={styles.simpleScoreBoard}
                size="small"
                dataSource={data.list}
                pagination={{
                    defaultPageSize: 50,
                    showQuickJumper: true,
                }}
                rowKey="rank"
                columns={columns}
            />
        </div>
    );
}
