import { useState } from 'react';

export function ImageWithSkeleton({
    src,
    alt,
    width,
    height,
}: {
    src: string;
    alt: string;
    width: string;
    height: string;
}) {
    const [loaded, setLoaded] = useState(false);
    return (
        <div style={{ width: width, height: height }}>
            {!loaded && <div className="skeleton w-full h-full"></div>}
            <img src={src} alt={alt} onLoad={() => setLoaded(true)} style={{ display: loaded ? 'block' : 'none' }} />
        </div>
    );
}
