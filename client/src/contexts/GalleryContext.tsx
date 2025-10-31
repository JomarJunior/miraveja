import { useState, type ReactNode, useMemo, useCallback } from "react";
import { galleryApi, type ImageMetadata } from "../api/gallery-api";
import { defaultContext, GalleryContext, type GalleryContextProps, type UploadStatus } from "../hooks/useGallery";

// Provider component
export function GalleryProvider({ children }: { children: ReactNode }) {
    const [uploadStatus, setUploadStatus] = useState<UploadStatus>(defaultContext.uploadStatus);
    const [images, setImages] = useState<ImageMetadata[]>(defaultContext.images);
    const [isLoading, setIsLoading] = useState<boolean>(defaultContext.isLoading);

    // Reset upload status
    const resetUploadStatus = () => {
        setUploadStatus(defaultContext.uploadStatus);
    };

    // Upload image action
    const uploadImage = async (file: File, metadata: Omit<ImageMetadata, 'uri' | 'width' | 'height'>) => {
        try {
            setUploadStatus({ isUploading: true, progress: 0, error: null, isComplete: false });

            await galleryApi.uploadImage(file, metadata, (progress) => {
                setUploadStatus((prev) => ({ ...prev, progress }));
            });

            setUploadStatus({ isUploading: false, progress: 100, error: null, isComplete: true });
        } catch (error: unknown) {
            setUploadStatus(prev => ({ ...prev, isUploading: false, error: (error instanceof Error) ? error.message : 'Unknown error', isComplete: false }));
            throw error;
        }
    };

    // Fetch all images metadata
    const fetchAllImagesMetadata = useCallback(async () => {
        setIsLoading(true);
        try {
            const data = await galleryApi.getAllImagesMetadata();
            setImages(data);
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Provide context values
    const contextValue: GalleryContextProps = useMemo(() => ({
        uploadStatus,
        uploadImage,
        images,
        isLoading,
        fetchAllImagesMetadata,
        resetUploadStatus
    }), [uploadStatus, images, isLoading, fetchAllImagesMetadata]);

    return (
        <GalleryContext value={contextValue}>
            {children}
        </GalleryContext>
    );
};

