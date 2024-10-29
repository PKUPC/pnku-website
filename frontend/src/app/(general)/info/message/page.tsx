import { MessageBox } from '@/app/(general)/info/message/MessageBox';
import NotFound from '@/app/NotFound.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function MessagePage() {
    const info = useSuccessGameInfo();
    if (ARCHIVE_MODE || !info.team || !info.game.isPrologueUnlock) return <NotFound />;

    return <MessageBox teamId={info.team!.id} />;
}
