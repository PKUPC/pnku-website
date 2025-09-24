import { InboxOutlined } from '@ant-design/icons';
import { Button, GetProp, Upload, UploadFile, UploadProps, message } from 'antd';
import { useState } from 'react';
import { mutate } from 'swr';

import { WISH_ROOT } from '@/constants';
import { WISH_VER } from '@/logic/wish';

import styles from './UploadBox.module.css';

type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

function scaleImage(img: HTMLImageElement, maxPixels: number): { width: number; height: number } {
    const { width, height } = img;
    const totalPixels = width * height;
    if (totalPixels <= maxPixels) {
        return { width, height };
    }
    const scaleFactor = Math.sqrt(maxPixels / totalPixels);
    return {
        width: Math.floor(width * scaleFactor),
        height: Math.floor(height * scaleFactor),
    };
}

function checkWebPSupport(): Promise<boolean> {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        canvas.toBlob((blob) => {
            if (blob && blob.type === 'image/webp') {
                resolve(true);
            } else {
                resolve(false);
            }
        }, 'image/webp');
    });
}

export function UploadBox() {
    const [imageFile, setImageFile] = useState<UploadFile | null>(null);
    const [messageApi, contextHolder] = message.useMessage();
    const [uploading, setUploading] = useState(false);
    const [percentage, setPercentage] = useState(0);

    const props: UploadProps = {
        name: 'image',
        listType: 'picture',
        onRemove: () => {
            setImageFile(null);
        },
        onPreview: () => false,
        beforeUpload: async (file) => {
            const isTypeAllowed =
                file.type === 'image/png' ||
                file.type === 'image/jpg' ||
                file.type === 'image/jpeg' ||
                file.type === 'image/webp';
            if (!isTypeAllowed) {
                messageApi.error('不支持的文件类型！').then();
                return false;
            }
            const supportWebp = await checkWebPSupport();
            const fileType = supportWebp ? 'webp' : 'jpeg';
            let newBlob;
            try {
                newBlob = await new Promise<Blob>((resolve, reject) => {
                    const reader = new FileReader();
                    reader.readAsDataURL(file);
                    reader.onerror = () => reject('文件读取失败！');
                    reader.onload = () => {
                        const dataUrl = reader.result as string;
                        const img = new Image();
                        img.src = dataUrl;
                        img.onerror = () => reject('图片加载失败！');
                        img.onload = () => {
                            const canvas = document.createElement('canvas');
                            const ctx = canvas.getContext('2d');

                            if (!ctx) {
                                reject('浏览器不支持 Canvas！');
                                return;
                            }

                            const { width, height } = scaleImage(img, 1920 * 1080);
                            canvas.width = width;
                            canvas.height = height;
                            ctx.drawImage(img, 0, 0, width, height);

                            canvas.toBlob(
                                (blob) => {
                                    if (blob) {
                                        resolve(blob);
                                    } else {
                                        reject('图片压缩失败！');
                                    }
                                },
                                'image/' + fileType,
                                0.75,
                            );
                        };
                    };
                });
            } catch (error) {
                messageApi.error({ content: error as string });
                return false;
            }
            console.log(newBlob.size);
            if (newBlob.size > 512 * 1024) {
                messageApi.error('图片过大！');
                return false;
            }
            const newFile = new File([newBlob], file.name, { type: newBlob.type });
            const dataUrl = await new Promise<string>((resolve, reject) => {
                const reader = new FileReader();
                reader.readAsDataURL(newBlob);
                reader.onload = () => resolve(reader.result as string);
                reader.onerror = () => reject('文件处理失败！');
            });
            console.log(newFile);

            setImageFile({
                status: 'done',
                name: 'image.' + fileType,
                uid: file.uid,
                size: newFile.size,
                thumbUrl: dataUrl,
                originFileObj: newFile as FileType,
            });
            return false;
        },
        fileList: imageFile
            ? [
                  {
                      ...imageFile,
                      status: uploading ? 'uploading' : 'done',
                      percent: uploading ? percentage : undefined,
                  },
              ]
            : [],
    };

    const uploadFile = () => {
        const form = new FormData();
        console.log(imageFile);
        if (imageFile?.originFileObj) form.append('file', imageFile?.originFileObj);
        setUploading(true);
        const xhr = new XMLHttpRequest();
        xhr.open('POST', WISH_ROOT + 'upload/upload_image');
        xhr.setRequestHeader('X-Wish-Version', WISH_VER);
        xhr.withCredentials = true;
        xhr.responseType = 'json';
        xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable) {
                setPercentage((100 * event.loaded) / event.total);
            }
        });
        xhr.addEventListener('loadend', () => {
            if (xhr.readyState !== 4) {
                messageApi
                    .error({
                        content: `网络错误 state=${xhr.readyState}`,
                        key: 'Upload.Submit',
                        duration: 3,
                    })
                    .then();
            } else if (xhr.status !== 200) {
                messageApi.error({ content: `HTTP 错误 ${xhr.status}`, key: 'Upload.Submit', duration: 3 }).then();
            } else if (xhr.response.status === 'error') {
                messageApi.error({ content: xhr.response.message, key: 'Upload.Submit', duration: 3 }).then();
            } else {
                messageApi.success({ content: '提交成功', key: 'Upload.Submit', duration: 2 }).then();
                setImageFile(null);
                mutate({ endpoint: 'upload/get_uploaded_images' }).then();
            }
            setUploading(false);
        });

        xhr.send(form);
    };

    return (
        <div className={styles.uploadBox}>
            {contextHolder}
            <Upload.Dragger {...props}>
                <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或将图片拖拽到此区域以上传图片。</p>
                <p className="ant-upload-hint">
                    图片格式可以为 jpg、png、webp。上传时会尝试压缩图片，压缩后的大小不能超过 512 KB。
                </p>
            </Upload.Dragger>
            <br />
            <Button
                type={'primary'}
                size={'large'}
                style={{ width: '100%' }}
                loading={uploading}
                disabled={!imageFile}
                onClick={uploadFile}
            >
                确认上传
            </Button>
        </div>
    );
}
