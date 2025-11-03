import React from "react";
import * as MuiMaterial from "@mui/material";
import type { ImageMetadata } from "../api/gallery-api";
import { getAvailableSpace, getAvailableSpaceNumber } from "../utils/layout-utils";

interface ScrollerGalleryProps {
    images: ImageMetadata[];
    onNextImage?: (currentIndex: number) => void;
    onPreviousImage?: (currentIndex: number) => void;
};

const defaultGalleryProps: ScrollerGalleryProps = {
    images: [],
    onNextImage: () => { /* empty */ },
    onPreviousImage: () => { /* empty */ },
};

const SCROLL_TIMEOUT_MS = 300;
const SCROLL_THRESHOLD_PX = 0;
const TOUCH_SCROLL_DEADZONE_PX = getAvailableSpaceNumber().height * 0.25;

export default function ScrollerGallery(props: ScrollerGalleryProps = defaultGalleryProps) {
    const { images, onNextImage, onPreviousImage } = props;
    const [currentImageIndex, setCurrentImageIndex] = React.useState(0);
    const [offsetY, setOffsetY] = React.useState(0);
    const [isTransitioning, setIsTransitioning] = React.useState(false);
    const wheelTimeoutRef = React.useRef<number | null>(null);
    const touchStartYRef = React.useRef<number | null>(null);

    // Handlers
    const handleNextImage = React.useCallback(() => {
        if (images.length === 0 || isTransitioning) return;
        setIsTransitioning(true);
        setOffsetY(-getAvailableSpaceNumber().height); // Animate current image out
        setTimeout(() => {
            const nextIndex = (currentImageIndex + 1) % images.length;
            setCurrentImageIndex(nextIndex);
            onNextImage?.(nextIndex);
            setOffsetY(0);
            setIsTransitioning(false);
        }, SCROLL_TIMEOUT_MS); // Match transition duration
    }, [images.length, onNextImage, isTransitioning, currentImageIndex]);

    const handlePreviousImage = React.useCallback(() => {
        if (images.length === 0 || isTransitioning) return;
        setIsTransitioning(true);
        setOffsetY(getAvailableSpaceNumber().height); // Animate current image out
        setTimeout(() => {
            const prevIndex = (currentImageIndex - 1 + images.length) % images.length;
            setCurrentImageIndex(prevIndex);
            onPreviousImage?.(prevIndex);
            setOffsetY(0);
            setIsTransitioning(false);
        }, SCROLL_TIMEOUT_MS); // Match transition duration
    }, [images.length, onPreviousImage, isTransitioning, currentImageIndex]);

    // Events Listeners
    React.useEffect(() => {
        const KEY_HANDLER_MAP = {
            ArrowDown: handleNextImage,
            ArrowUp: handlePreviousImage,
        };

        const handleKeyDown = (event: KeyboardEvent) => {
            const handler = KEY_HANDLER_MAP[event.key as keyof typeof KEY_HANDLER_MAP];
            if (handler) {
                handler();
            }
        };

        const handleWheel = (event: WheelEvent) => {
            if (isTransitioning) return;

            // Clear previous timeout
            if (wheelTimeoutRef.current) {
                clearTimeout(wheelTimeoutRef.current);
            }

            const newOffset = offsetY - event.deltaY;
            const scrollThreshold = SCROLL_THRESHOLD_PX; // When to trigger image change

            // Trigger image change if threshold is crossed
            if (newOffset >= scrollThreshold) {
                handlePreviousImage();
                return;
            }

            if (newOffset <= -scrollThreshold) {
                handleNextImage();
                return;
            }

            // Apply offset for smooth scrolling effect
            setOffsetY(newOffset);

            // Set a timeout to reset offset after scrolling stops
            wheelTimeoutRef.current = window.setTimeout(() => {
                setOffsetY(0);
            }, 100);
        };

        const handleTouchStart = (event: TouchEvent) => {
            if (isTransitioning) return;
            touchStartYRef.current = event.touches[0].clientY;
        }

        const handleTouchMove = (event: TouchEvent) => {
            if (isTransitioning) return;
            const deltaY = event.touches[0].clientY - (touchStartYRef.current ?? 0);
            setOffsetY(deltaY);
        }

        const handleTouchEnd = () => {
            if (isTransitioning) return;
            const scrollThreshold = TOUCH_SCROLL_DEADZONE_PX;

            if (offsetY >= scrollThreshold) {
                handlePreviousImage();
            } else if (offsetY <= -scrollThreshold) {
                handleNextImage();
            } else {
                // Reset offset if no image change
                setOffsetY(0);
            }
            touchStartYRef.current = null;
        }

        window.addEventListener("keydown", handleKeyDown);
        window.addEventListener("wheel", handleWheel);
        window.addEventListener("touchstart", handleTouchStart);
        window.addEventListener("touchmove", handleTouchMove);
        window.addEventListener("touchend", handleTouchEnd);
        return () => {
            window.removeEventListener("keydown", handleKeyDown);
            window.removeEventListener("wheel", handleWheel);
            window.removeEventListener("touchstart", handleTouchStart);
            window.removeEventListener("touchmove", handleTouchMove);
            window.removeEventListener("touchend", handleTouchEnd);
        };
    }, [handleNextImage, handlePreviousImage, isTransitioning, offsetY]);

    if (images.length === 0) {
        return (
            <MuiMaterial.Container>
                <MuiMaterial.Typography variant="h5" sx={{ mt: 5, textAlign: 'center' }}>
                    No images available.
                </MuiMaterial.Typography>
            </MuiMaterial.Container>
        );
    }

    const renderImage = (image: 'current' | 'next' | 'previous') => {
        const isCurrent = image === 'current';
        const isNext = image === 'next';
        const imageIndex = isCurrent
            ? currentImageIndex
            : isNext
                ? (currentImageIndex + 1) % images.length
                : (currentImageIndex - 1 + images.length) % images.length;


        const availableHeight = getAvailableSpace().height;

        const topOffset = isCurrent
            ? 0
            : isNext
                ? `calc(${availableHeight} )`
                : `calc(-1 * ${availableHeight} )`;

        return (<MuiMaterial.Box
            sx={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                top: topOffset,
                backgroundImage: `url(${images[imageIndex].uri})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                padding: 0,
                margin: 0,
                transform: `translateY(${offsetY}px)`, // Apply vertical offset
                transition: isTransitioning ? `transform ${SCROLL_TIMEOUT_MS}ms ease-in-out` : 'none',
            }}
        >
            <MuiMaterial.Box
                sx={{
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    backgroundColor: 'rgba(0, 0, 0, 0.3)',
                    backdropFilter: 'blur(15px)',
                    WebkitBackdropFilter: 'blur(15px)',
                    overflow: 'hidden',
                }}
            >
                <MuiMaterial.Box
                    component="img"
                    src={images[imageIndex].uri}
                    sx={{
                        maxWidth: '100%',
                        maxHeight: '80vh',
                        objectFit: 'contain',
                    }}
                />
            </MuiMaterial.Box>
        </MuiMaterial.Box>);
    };

    return (
        <MuiMaterial.Box
            component="div"
            sx={{
                minWidth: '0',
                height: '100%',
                width: '100%',
                overflow: 'hidden',
                position: 'relative',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
            }}
        >
            {renderImage('previous')}
            {renderImage('current')}
            {renderImage('next')}
        </MuiMaterial.Box>
    );
};