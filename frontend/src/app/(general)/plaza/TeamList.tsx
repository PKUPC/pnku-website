import { FlagOutlined } from '@ant-design/icons';
import { Alert, Col, FloatButton, Modal, Row, Tooltip } from 'antd';
import { useCallback, useEffect, useRef, useState } from 'react';

import { EveryUserIcon } from '@/SvgIcons';
import styles from '@/app/(general)/plaza/TeamList.module.css';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import InfoBox from '@/components/InfoBox';
import { ProfileAvatar } from '@/components/ProfileAvatar.tsx';
import { useTheme } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';
import { mixColor, shuffleArray, stringToHue, truncateString } from '@/utils.ts';

function TeamCardModal({
    teamInfo,
    open,
    setOpen,
}: {
    teamInfo: Wish.Game.TeamInfo | null;
    open: boolean;
    setOpen: (param: boolean) => void;
}) {
    const { color } = useTheme();
    let content;
    if (!teamInfo) {
        content = <Loading />;
    } else {
        const hashHue = stringToHue(teamInfo.team_name + teamInfo.team_info);
        const bgColor = mixColor(`hsl({${hashHue}, 55%, 80%})`, color.base100, 0.03);

        const leaderIcon = (
            <Tooltip placement="top" title={'队长'}>
                <FlagOutlined />
            </Tooltip>
        );
        const users = teamInfo.team_members.map((memberObject) => (
            <Col span={12} key={`hoverCardTdUser${memberObject.avatar_url}`}>
                <div className="flex items-center gap-2 text-[#666]">
                    <ProfileAvatar src={memberObject.avatar_url} alt={memberObject.nickname} size={'2rem'} />
                    {memberObject.nickname}
                    {memberObject.type === 'leader' && leaderIcon}
                </div>
            </Col>
        ));

        content = (
            <div
                className={'teamCardModal'}
                style={{
                    background: bgColor,
                }}
            >
                <div className={styles.cardTeamName}>
                    {teamInfo.team_name}
                    <div className={'team-member-status'}>
                        <EveryUserIcon />
                        {teamInfo.team_members.length}
                    </div>
                </div>
                <div className="team-description">
                    {teamInfo.team_info === '' ? (
                        <div style={{ opacity: '0.4' }}>（队伍什么都没写）</div>
                    ) : (
                        teamInfo.team_info
                    )}
                </div>
                <br />
                <Row style={{ width: '100%' }} gutter={[8, 8]}>
                    {users}
                </Row>

                {teamInfo.recruiting && (
                    <>
                        <br />
                        <InfoBox title={'招募信息'} backgroundColor={bgColor}>
                            {teamInfo.recruiting_contact}
                        </InfoBox>
                    </>
                )}
            </div>
        );
    }

    return (
        <div>
            <Modal
                open={open}
                destroyOnHidden={true}
                footer={null}
                maskClosable={true}
                onCancel={() => setOpen(false)}
                className={styles.teamCardModalWrapper}
                centered
                getContainer={() => {
                    const target = document.getElementById('global-container');
                    if (target) return target;
                    return document.body;
                }}
            >
                {content}
            </Modal>
        </div>
    );
}

function TeamCard({ teamInfo, onClick }: { teamInfo: Wish.Game.TeamInfo; onClick: () => void }) {
    const { color } = useTheme();
    const hashHue = stringToHue(teamInfo.team_name + teamInfo.team_info);
    const bgColor = mixColor(`hsl({${hashHue}, 55%, 80%})`, color.base100, 0.03);

    return (
        <div
            className={styles.teamCard}
            style={{
                background: bgColor,
            }}
            onClick={onClick}
        >
            <div className={styles.cardTeamName}>
                {teamInfo.team_name}
                <div className={'team-member-status'}>
                    <EveryUserIcon />
                    {teamInfo.team_members.length}
                </div>
            </div>
            <div className="team-description">
                {teamInfo.team_info === '' ? (
                    <div style={{ opacity: '0.4' }}>（队伍什么都没写）</div>
                ) : (
                    truncateString(teamInfo.team_info, 80)
                )}
            </div>
            {teamInfo.recruiting && (
                <>
                    <div className={styles.recruitingTagWrapper}>
                        <div className={styles.recruitingTag}></div>
                    </div>
                    {/*<Tag color={"orange"}><CatPawIcon/> 招募中</Tag>*/}
                </>
            )}
        </div>
    );
}

export function TeamList({ teamList }: { teamList: Wish.Game.TeamInfo[] }) {
    const [teamInfoForModal, setTeamInfoForModal] = useState<Wish.Game.TeamInfo | null>(null);
    const [openModal, setOpenModal] = useState(false);
    const [showCount, setShowCount] = useState(teamList.length > 50 ? 50 : teamList.length);
    const bottomRef = useRef<HTMLDivElement | null>(null);

    const currentTimestamp = Date.now();
    const hours = Math.floor(currentTimestamp / (1000 * 60 * 60));

    const recruitingTeams = shuffleArray(
        teamList.filter((item) => item.recruiting),
        hours,
    );
    const nonRecruitingTeams = shuffleArray(
        teamList.filter((item) => !item.recruiting),
        hours,
    );

    const onScrolledToBottom = useCallback(
        (entries: IntersectionObserverEntry[]) => {
            const [entry] = entries;
            if (entry.isIntersecting) {
                setShowCount((pre) => (pre + 50 > teamList.length ? teamList.length : pre + 50));
            }
        },
        [teamList.length],
    );

    useEffect(() => {
        const observer = new IntersectionObserver(onScrolledToBottom, {
            root: null,
            rootMargin: '0px',
            threshold: 0.01,
        });
        const current = bottomRef.current;
        if (current) observer.observe(current);
        return () => {
            if (current) observer.unobserve(current);
        };
    }, [onScrolledToBottom]);

    return (
        <div>
            <Alert
                showIcon
                message={<b>注意事项</b>}
                description={
                    <>
                        <p>
                            <strong>
                                招募功能是方便玩家组队使用，请确定您有真实的招募需求后再开启。滥用此功能可能会有相应的惩罚。
                            </strong>
                        </p>
                    </>
                }
            />
            <br />
            <TeamCardModal teamInfo={teamInfoForModal} open={openModal} setOpen={setOpenModal} />

            {recruitingTeams.length > 0 && (
                <>
                    <div className={styles.plazaTitles}>
                        <h3>招募中的队伍</h3>
                    </div>
                    <br />
                    <div className={styles.teamList}>
                        {recruitingTeams.map((item) => (
                            <TeamCard
                                teamInfo={item}
                                key={item.team_id}
                                onClick={() => {
                                    setTeamInfoForModal(item);
                                    setOpenModal(true);
                                }}
                            />
                        ))}
                    </div>

                    <br />
                </>
            )}

            <div className={styles.plazaTitles}>
                <h3 className="text-2xl font-semibold">队伍列表</h3>
            </div>
            <br />
            <div className={styles.teamList}>
                {nonRecruitingTeams.slice(0, showCount).map((item) => (
                    <TeamCard
                        teamInfo={item}
                        key={item.team_id}
                        onClick={() => {
                            setTeamInfoForModal(item);
                            setOpenModal(true);
                        }}
                    />
                ))}
            </div>
            <div ref={bottomRef} className="w-full h-4"></div>
            <FloatButton.BackTop />
        </div>
    );
}
