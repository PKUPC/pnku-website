import { Carousel, ConfigProvider } from 'antd';
import React, { useLayoutEffect, useRef, useState } from 'react';
import { Link } from 'react-router';

import { FooterContent } from '@/components/FooterContent.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';

import styles from './SimpleHome.module.css';

function CarouselTemplate({ heroData }: { heroData: Wish.Game.HomeAreaData }) {
    const fadeContainerRef = useRef<HTMLDivElement>(null);
    const [gradient, setGradient] = useState('');

    useLayoutEffect(() => {
        const updateGradient = () => {
            const width = fadeContainerRef.current!.clientWidth;
            const height = fadeContainerRef.current!.clientHeight;
            const ratio = width / height;

            const maxRatio = 1.8;
            const minRatio = 1 / 2.5;
            const maxPercentage = 90;
            const minPercentage = 30;

            let topPercentage;
            if (ratio <= minRatio) {
                topPercentage = minPercentage;
            } else if (ratio >= maxRatio) {
                topPercentage = maxPercentage;
            } else {
                const ratioRange = maxRatio - minRatio;
                const topRange = maxPercentage - minPercentage;
                topPercentage = maxPercentage - (maxRatio - ratio) * (topRange / ratioRange);
            }

            console.log(ratio);

            setGradient(
                `linear-gradient(to bottom, rgba(0, 0, 0, 0) ${topPercentage - 10}%, rgba(0, 0, 0, 0.4) ${topPercentage}%, rgba(0, 0, 0, 0.8) 100%)`,
            );
        };

        updateGradient();
        window.addEventListener('resize', updateGradient);

        return () => window.removeEventListener('resize', updateGradient);
    }, []);

    const containerBgStyles: React.CSSProperties = {
        backgroundImage: `url(${heroData.bgUrl})`,
        backgroundPositionX: `${heroData.bgFocusPositionX}%`,
        backgroundPositionY: `${heroData.bgFocusPositionY}%`,
    };
    const titleContainerPositionStyles: React.CSSProperties = {
        top: heroData.topPercentage && `${heroData.topPercentage}%`,
        left: heroData.leftPercentage && `${heroData.leftPercentage}%`,
        right: heroData.rightPercentage && `${heroData.rightPercentage}%`,
        bottom: heroData.bottomPercentage && `${heroData.bottomPercentage}%`,
        textAlign: heroData.align,
    };
    const alignStyle = heroData.align == 'right' ? styles.rightAlign : styles.leftAlign;

    const textColorStyle: React.CSSProperties = {
        background: `linear-gradient(45deg, ${heroData.subColor}, ${heroData.mainColor})`,
        backgroundClip: 'text',
    };
    const buttonBorderStyle: React.CSSProperties = {
        borderImage: `linear-gradient(45deg, ${heroData.subColor}, ${heroData.mainColor}) 1`,
    };

    const heroTitleStyle = `${styles.heroTitle} ${styles.heroText} ${alignStyle}`;
    const heroSubtitleStyle = `${styles.heroSubtitle} ${styles.heroText} ${alignStyle}`;
    return (
        <div className={styles.heroContainer} style={containerBgStyles} ref={fadeContainerRef}>
            <div className={styles.heroTitleContainer} style={titleContainerPositionStyles}>
                <h1>
                    <span className={heroTitleStyle} style={textColorStyle} data-text={heroData.title}>
                        {heroData.title}
                    </span>
                </h1>
                <h2>
                    <span className={heroSubtitleStyle} data-text={heroData.subtitle}>
                        {heroData.subtitle}
                    </span>
                </h2>
                <Link to={heroData.buttonLink}>
                    <div className={styles.heroButton} style={buttonBorderStyle}>
                        {heroData.buttonText}
                    </div>
                </Link>
            </div>
            <div className={styles.heroFade} style={{ background: gradient }} />
        </div>
    );
}

export function SimpleHome() {
    const info = useSuccessGameInfo();

    const carouselContent = info.areas.map((heroData) => (
        <CarouselTemplate heroData={heroData} key={heroData.buttonText} />
    ));
    const draggable = info.areas.length > 1;

    return (
        <>
            {/*<Header/>*/}
            <div className={styles.simpleHomeContainer}>
                <ConfigProvider
                    theme={{
                        components: {
                            Carousel: {
                                arrowOffset: 24,
                                arrowSize: 48,
                            },
                        },
                    }}
                >
                    <Carousel arrows infinite={false} draggable={draggable}>
                        {carouselContent}
                    </Carousel>
                </ConfigProvider>
            </div>
            <div className="text-[0.8rem] pt-8 pb-8 bg-neutral text-neutral-content/60 text-center">
                <FooterContent />
            </div>
        </>
    );
}
