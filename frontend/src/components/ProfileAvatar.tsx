import { ImageWithSkeleton } from '@/components/ImageWithSkeleton.tsx';

interface Profile {
    src: string;
    alt: string;
    size: number | string;
}

export function ProfileAvatar({ src, alt, size }: Profile) {
    return (
        <>
            <div className="avatar">
                <div className="rounded-xl">
                    <ImageWithSkeleton src={src} alt={alt} width={size + ''} height={size + ''} />
                </div>
            </div>
        </>
    );
}
