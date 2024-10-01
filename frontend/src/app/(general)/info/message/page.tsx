import { MessageBox } from '@/app/(general)/info/message/MessageBox';
import NotFound from '@/app/NotFound.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function MessagePage() {
    const info = useSuccessGameInfo();
    if (import.meta.env.VITE_ARCHIVE_MODE === 'true' || !info.team || !info.game.isPrologueUnlock) return <NotFound />;

    return <MessageBox teamId={info.team!.id} />;
}
