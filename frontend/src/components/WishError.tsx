import { GeneralError } from '@/components/GeneralError';
import { Wish } from '@/types/wish.ts';

export function WishError({ res, reload }: { res: Wish.ErrorRes; reload?: () => void }) {
    if (reload)
        return (
            <GeneralError
                title={`错误：${res.message}`}
                subtitle={
                    <>
                        如果你确信这是异常情况，请先尝试重试，如果仍出现问题，请及时联系网站管理员。
                        <br />
                    </>
                }
                reload={reload}
            />
        );
    return (
        <GeneralError title={`错误：${res.message}`} subtitle={<>如果你确信这是异常情况，请及时联系网站管理员。</>} />
    );
}
