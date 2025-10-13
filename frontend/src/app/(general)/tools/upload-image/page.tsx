import { Alert } from 'antd';

import { ImageList } from '@/app/(general)/tools/upload-image/ImageList';
import { UploadBox } from '@/app/(general)/tools/upload-image/UploadBox';
import NotFound from '@/app/NotFound.tsx';
import { Loading } from '@/components/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';

function UploadImageBody() {
    const { data, mutate } = useWishData({ endpoint: 'upload/get_uploaded_images' });

    if (!data) return <Loading />;
    if (data.status !== 'success') return <WishError res={data} reload={mutate} />;

    console.log(data);
    return (
        <>
            <Alert
                message="提示："
                description={
                    <>
                        本功能仅能用于通过站内信或神谕系统发送图片，请保证您上传的图片合法合规，如滥用此功能或上传包含不适宜内容的图片可能会被禁用此功能或封禁帐号。
                        <br />
                        每个队伍的默认上传数量限制为 10 张，如果限额用完了需要继续使用，请通过站内信联系工作人员。
                    </>
                }
                className="message-info"
                type="info"
            />
            <br />
            {data.data.disabled ? (
                <Alert type={'error'} description={data.data.disable_reason ?? '已禁用。'} />
            ) : (
                <UploadBox />
            )}
            {data.data.list.length > 0 && (
                <>
                    <br />
                    <ImageList data={data.data.list} />
                </>
            )}
        </>
    );
}

export function UploadImagePage() {
    const gameInfo = useSuccessGameInfo();
    if (!gameInfo.user) return <NotFound />;
    else if (gameInfo.user.group !== 'staff' && (!gameInfo.game.isGameBegin || !gameInfo.team?.gaming))
        return <NotFound />;

    return <UploadImageBody />;
}
