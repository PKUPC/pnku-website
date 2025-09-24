import { CheckCircleFilled, CloseCircleFilled, InfoCircleFilled, QuestionCircleFilled } from '@ant-design/icons';
import { Button, Modal } from 'antd';
import React, { useEffect, useState } from 'react';

import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';

import styles from './WishComfirmModal.module.css';

export function WishConfirmModal<T extends Wish.WishConfirmParams>({
    wishParam,
    open,
    setOpen,
    confirmTitle,
    confirmContent,
    onError,
    onErrorContentRender,
    onErrorTitleRender,
    onSuccess,
    onSuccessContentRender,
    onSuccessTitleRender,
    onInfo,
    onInfoContentRender,
    onInfoTitleRender,
    onFinish,
}: {
    wishParam: T;
    open: boolean;
    setOpen: (param: boolean) => void;
    confirmTitle?: string;
    confirmContent?: string | React.ReactNode;
    onError?: (res: Wish.ResponseMapping[T['endpoint']]) => void;
    onErrorContentRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
    onErrorTitleRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
    onSuccess?: (res: Wish.ResponseMapping[T['endpoint']]) => void;
    onSuccessContentRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
    onSuccessTitleRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
    onInfo?: (res: Wish.ResponseMapping[T['endpoint']]) => void;
    onInfoContentRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
    onInfoTitleRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
    onFinish?: (res: Wish.ResponseMapping[T['endpoint']]) => void;
}) {
    const defaultConfirmTitle = '提交确认';

    const defaultConfirmContent = '确认要提交吗？';

    const defaultConfirmIcon = <QuestionCircleFilled style={{ color: '#faad14' }} />;
    const defauleSuccessIcon = <CheckCircleFilled style={{ color: '#52c41a' }} />;
    const defaultErrorIcon = <CloseCircleFilled style={{ color: '#ff4d4f' }} />;
    const defaultInfoIcon = <InfoCircleFilled style={{ color: '#1890ff' }} />;

    const defaultSuccessTitleRender = (res: Wish.ResponseMapping[T['endpoint']]) => {
        if (!res.title) return '成功';
        return res.title;
    };

    const defaultErrorTitleRender = (res: Wish.ResponseMapping[T['endpoint']]) => {
        if (!res.title) return '出错';
        return res.title;
    };

    const defaultInfoTitleRender = (res: Wish.ResponseMapping[T['endpoint']]) => {
        if (!res.title) return '获得信息';
        return res.title;
    };

    const defaultErrorContentRender = (res: Wish.ResponseMapping[T['endpoint']]) => {
        if (!res.message) return '出错！';
        return <div style={{ whiteSpace: 'pre-line' }}>{res.message}</div>;
    };

    const defaultSuccessContentRender = (res: Wish.ResponseMapping[T['endpoint']]) => {
        if (!res.message) return '成功';
        return <div style={{ whiteSpace: 'pre-line' }}>{res.message}</div>;
    };

    const defaultInfoContentRender = (res: Wish.ResponseMapping[T['endpoint']]) => {
        if (!res.message) return '获得未知信息，或许出错了。';
        return <div style={{ whiteSpace: 'pre-line' }}>{res.message}</div>;
    };

    const [status, setStatus] = useState('confirm');
    const [confirmLoading, setConfirmLoading] = useState(false);
    const [response, setResponse] = useState<Wish.ResponseMapping[T['endpoint']] | undefined>(undefined);

    useEffect(() => {
        if (!open) {
            // console.log("resetting WishConfirmModal state");
            setStatus('confirm');
            setConfirmLoading(false);
            setResponse(undefined);
        }
    }, [open]);

    const onSubmit = () => {
        setConfirmLoading(true);
        wish(wishParam).then((res) => {
            // 新版本直接加一个 status 标记
            // status 就是 success info error
            if (res.status) setStatus(res.status);
            else setStatus('error');
            setResponse(res);
        });
    };

    const onCancel = () => {
        setOpen(false);
    };

    const onFinishConfirm = () => {
        setOpen(false);
        if (status === 'success' && !!onSuccess && !!response) onSuccess(response);
        if (status === 'error' && !!onError && !!response) onError(response);
        if (status === 'info' && !!onInfo && !!response) onInfo(response);
        if (!!onFinish && !!response) onFinish(response);
    };

    let title: React.ReactNode = '加载中...'; // 按理来说不应该显示这个
    if (status === 'confirm') {
        if (confirmLoading) title = '提交中...';
        else title = confirmTitle ? confirmTitle : defaultConfirmTitle;
        title = (
            <>
                {defaultConfirmIcon}&nbsp;&nbsp;{title}
            </>
        );
    } else if (status === 'success' && !!response) {
        title = onSuccessTitleRender ? onSuccessTitleRender(response) : defaultSuccessTitleRender(response);
        title = (
            <>
                {defauleSuccessIcon}&nbsp;&nbsp;{title}
            </>
        );
    } else if (status === 'error' && !!response) {
        title = onErrorTitleRender ? onErrorTitleRender(response) : defaultErrorTitleRender(response);
        title = (
            <>
                {defaultErrorIcon}&nbsp;&nbsp;{title}
            </>
        );
    } else if (status === 'info' && !!response) {
        title = onInfoTitleRender ? onInfoTitleRender(response) : defaultInfoTitleRender(response);
        title = (
            <>
                {defaultInfoIcon}&nbsp;&nbsp;{title}
            </>
        );
    }

    let content: React.ReactNode = <></>;
    if (status === 'confirm') {
        content = confirmContent ? confirmContent : defaultConfirmContent;
        content = <div style={{ whiteSpace: 'pre-line' }}>{content}</div>;
    } else if (status === 'success' && !!response)
        content = onSuccessContentRender ? onSuccessContentRender(response) : defaultSuccessContentRender(response);
    else if (status === 'error' && !!response)
        content = onErrorContentRender ? onErrorContentRender(response) : defaultErrorContentRender(response);
    else if (status === 'info' && !!response)
        content = onInfoContentRender ? onInfoContentRender(response) : defaultInfoContentRender(response);

    let footer;
    if (status === 'confirm') {
        footer = [
            <Button key={'cancel'} onClick={onCancel} disabled={confirmLoading}>
                取消
            </Button>,
            <Button type="primary" loading={confirmLoading} key={'submit'} onClick={onSubmit}>
                确认
            </Button>,
        ];
    } else {
        footer = [
            <Button type="primary" key={'cancel'} onClick={onFinishConfirm}>
                确认
            </Button>,
        ];
    }

    return (
        <div>
            <Modal
                open={open}
                title={<>{title}</>}
                footer={footer}
                destroyOnHidden={true}
                closable={false}
                wrapClassName={styles.wishConfirmModal}
            >
                {content}
            </Modal>
        </div>
    );
}
