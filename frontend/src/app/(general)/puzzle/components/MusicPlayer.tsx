import { useState } from 'react';
import AudioPlayer from 'react-h5-audio-player';
import 'react-h5-audio-player/lib/styles.css';

export function MusicPlayer({ playlist }: { playlist: string[] }) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const playlistLength = playlist.length;
    const handleClickPrevious = () => {
        setCurrentIndex((prev) => (prev - 1 + playlistLength) % playlistLength);
    };
    const handleClickNext = () => {
        setCurrentIndex((prev) => (prev + 1) % playlistLength);
    };
    const suffix = '.webm';

    return (
        <div>
            <AudioPlayer
                autoPlay={true}
                src={playlist[currentIndex] + suffix}
                onEnded={handleClickNext}
                volume={0.33}
                autoPlayAfterSrcChange={true}
                showSkipControls={true}
                showJumpControls={false}
                showDownloadProgress={true}
                onClickPrevious={handleClickPrevious}
                onClickNext={handleClickNext}
            />
        </div>
    );
}
