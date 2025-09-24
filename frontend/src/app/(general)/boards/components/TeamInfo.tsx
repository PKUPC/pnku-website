import { Tooltip } from 'antd';
import { Fragment } from 'react';
import { useNavigate } from 'react-router-dom';

import { PeopleIcon } from '@/SvgIcons';
import { TeamStatusTag } from '@/components/TeamStatusTag';
import { Wish } from '@/types/wish.ts';

import styles from './TeamInfo.module.css';

export function TeamInfo({ team, maxLength }: { team: Wish.Game.SimpleBoardItem; maxLength?: number }) {
    const fullShowInfo = team.in;
    let showInfo = fullShowInfo;
    if (!!maxLength && fullShowInfo.length > maxLength) {
        showInfo = fullShowInfo.substring(0, maxLength) + '......';
    }
    const navigate = useNavigate();

    let teamName;
    if (team.detail_url !== null && team.detail_url !== undefined)
        teamName = (
            <div onClick={() => navigate(team.detail_url ?? '')} style={{ display: 'inline', cursor: 'pointer' }}>
                {team.n + ' '}
            </div>
        );
    else teamName = <>{team.n + ' '}</>;

    return (
        <div className={styles.scoreBoardTeamInfo}>
            <Tooltip
                placement={'right'}
                title={team.ms.map((name, idx) => {
                    if (idx === 0)
                        return (
                            <Fragment key={idx}>
                                {name}（队长）
                                <br />
                            </Fragment>
                        );
                    else
                        return (
                            <Fragment key={idx}>
                                {name} <br />
                            </Fragment>
                        );
                })}
            >
                <div className="font-bold text-[0.9375rem] inline">
                    {teamName}
                    {team.bs.length > 0 && team.bs.map((v) => <TeamStatusTag key={v.text} data={v} />)}
                    <div className="inline opacity-36">
                        <PeopleIcon />
                    </div>
                </div>
            </Tooltip>
            <br />
            {!!maxLength && showInfo.length > maxLength ? (
                <Tooltip title={fullShowInfo}>
                    <div className="opacity-70">{showInfo}</div>
                </Tooltip>
            ) : (
                <div className="opacity-70">{showInfo}</div>
            )}
        </div>
    );
}
