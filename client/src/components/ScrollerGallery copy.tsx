import React from "react";
import * as MuiMaterial from "@mui/material";
import type { ImageMetadata } from "../api/gallery-api";

interface ScrollerGalleryProps {
    images: ImageMetadata[];
    onNextImage?: () => void;
    onPreviousImage?: () => void;
};

const defaultGalleryProps: ScrollerGalleryProps = {
    images: [],
    onNextImage: () => { /* empty */ },
    onPreviousImage: () => { /* empty */ },
};

const SCROLL_TIMEOUT_MS = 300;

export default function ScrollerGallery(props: ScrollerGalleryProps = defaultGalleryProps) {
    const { images, onNextImage, onPreviousImage } = props;
    const [currentImageIndex, setCurrentImageIndex] = React.useState(0);
    const [offsetY, setOffsetY] = React.useState(0);
    const [isTransitioning, setIsTransitioning] = React.useState(false);
    const [preventTransitionAnimation, setPreventTransitionAnimation] = React.useState(false);
    const wheelTimeoutRef = React.useRef<number | null>(null);
    const touchStartYRef = React.useRef<number | null>(null);

    // Handlers
    const handleNextImage = React.useCallback(() => {
        if (images.length === 0 || isTransitioning) return;
        setIsTransitioning(true);
        setOffsetY(-window.innerHeight); // Animate current image out
        setTimeout(() => {
            setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
            onNextImage?.();
            setPreventTransitionAnimation(true);
            setOffsetY(window.innerHeight); // Prepare position for next image
            setTimeout(() => {
                setPreventTransitionAnimation(false);
                setIsTransitioning(true);
                setOffsetY(0); // Animate next image in
                setTimeout(() => {
                    setIsTransitioning(false);
                }, SCROLL_TIMEOUT_MS);
            }, 50); // Small delay to ensure position is set before animating in
        }, SCROLL_TIMEOUT_MS); // Match transition duration
    }, [images.length, onNextImage, isTransitioning]);

    const handlePreviousImage = React.useCallback(() => {
        if (images.length === 0 || isTransitioning) return;
        setIsTransitioning(true);
        setOffsetY(window.innerHeight); // Animate current image out
        setTimeout(() => {
            setCurrentImageIndex((prevIndex) => (prevIndex - 1 + images.length) % images.length);
            onPreviousImage?.();
            setPreventTransitionAnimation(true);
            setOffsetY(-window.innerHeight); // Prepare position for next image
            setTimeout(() => {
                setPreventTransitionAnimation(false);
                setIsTransitioning(true);
                setOffsetY(0); // Animate next image in
                setTimeout(() => {
                    setIsTransitioning(false);
                }, SCROLL_TIMEOUT_MS);
            }, 50); // Small delay to ensure position is set before animating in
        }, SCROLL_TIMEOUT_MS); // Match transition duration
    }, [images.length, onPreviousImage, isTransitioning]);

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

            const newOffset = offsetY + event.deltaY;
            const scrollThreshold = window.innerHeight / 5; // When to trigger image change

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
            const scrollThreshold = window.innerHeight / 5; // When to trigger image change

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

    return (
        <MuiMaterial.Box
            sx={{
                height: '100%',
                width: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                backgroundImage: `url(${images[currentImageIndex].uri})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                padding: 0,
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
                    backdropFilter: 'blur(8px)',
                    WebkitBackdropFilter: 'blur(8px)',
                    overflow: 'hidden',
                }}
            >
                <MuiMaterial.Box
                    component="img"
                    src={images[currentImageIndex].uri}
                    sx={{
                        maxWidth: '100%',
                        maxHeight: '80vh',
                        objectFit: 'contain',
                        transform: `translateY(${offsetY}px)`, // Apply vertical offset
                        transition: (!preventTransitionAnimation && isTransitioning) ? `transform ${SCROLL_TIMEOUT_MS}ms ease-in-out` : 'none',
                    }}
                />
            </MuiMaterial.Box>
        </MuiMaterial.Box>
    );
};