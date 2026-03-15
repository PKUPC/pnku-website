import { type YClient } from '@/logic/YClient';

import './index.css';
import styles from './index.module.css';

// @ts-ignore
const { React } = window.exports;

const { useYClient, useParams, useYText, useSuccessGameInfo } = window.websiteUtils;
const { Loading, SyncTextarea } = window.components;

function SyncTextareaContainer({ client }: { client: YClient }) {
    const { yText } = useYText({ client, name: 'text' });
    const gameInfo = useSuccessGameInfo();

    return (
        <div className={styles.container}>
            <div className={styles.title}>共享记事本</div>
            <SyncTextarea
                client={client}
                yText={yText}
                textareaId={`shared-textarea-${gameInfo.team?.id ?? '-1'}`}
                username={gameInfo.user?.profile.nickname}
            />
        </div>
    );
}

export default function Index() {
    const params = useParams();
    const puzzleKey = params.puzzleKey;
    const { client } = useYClient({ roomId: `puzzle/${puzzleKey}` });

    if (!puzzleKey) throw new Error('Wrong Url!');
    if (!client) return <Loading />;

    return <SyncTextareaContainer client={client} />;
}
