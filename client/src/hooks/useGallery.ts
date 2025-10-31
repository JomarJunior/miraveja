import { createContext, use } from 'react';
import type { ImageMetadata } from '../api/gallery-api';

// Types for image upload
export interface UploadStatus {
    isUploading: boolean;
    progress: number; // 0 to 100
    error: string | null;
    isComplete: boolean;
};

// Context interface
export interface GalleryContextProps {
    // State
    uploadStatus: UploadStatus;
    images: ImageMetadata[];
    isLoading: boolean;

    // Actions
    uploadImage: (file: File, metadata: Omit<ImageMetadata, 'uri' | 'width' | 'height'>) => Promise<void>;
    resetUploadStatus: () => void;
    fetchAllImagesMetadata: () => Promise<ImageMetadata[]>;
};

// Default context values
export const defaultContext: GalleryContextProps = {
    uploadStatus: {
        isUploading: false,
        progress: 0,
        error: null,
        isComplete: false
    },
    images: [],
    isLoading: false,
    uploadImage: () => { throw new Error("GalleryContext not initialized"); },
    resetUploadStatus: () => { /* empty */ },
    fetchAllImagesMetadata: () => { throw new Error("GalleryContext not initialized"); },
};

// Create context
export const GalleryContext = createContext<GalleryContextProps>(defaultContext);

export const useGallery = () => use(GalleryContext);