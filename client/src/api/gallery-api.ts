import { httpClient } from "./http-client";

interface PresigedUrlResponse {
    url: string;
    fields: Record<string, string>;
};

interface PresignedUrlRequest {
    filename: string;
    mimeType: string;
    size: number;
};

export interface Lora {
    id: number;
    hash: string;
    name: string;
};

export interface GenerationMetadata {
    id?: number;
    imageId?: number;
    prompt: string;
    negativePrompt: string;
    seed: string;
    model: string;
    sampler: string;
    scheduler: string;
    steps: number;
    cfgScale: number;
    size: string;
    loras: Lora[];
};

export interface ImageMetadata {
    id?: number;
    ownerId?: string;
    title: string;
    subtitle: string;
    description: string;
    width: number;
    height: number;
    repositoryType: 'S3' | 'DeviantArt';
    uri?: string;
    isAiGenerated: boolean;
    generationMetadata: GenerationMetadata | null;
    vectorId?: number;
    createdAt?: string;
    updatedAt?: string;
};

interface GetAllImagesResponse {
    items: ImageMetadata[];
    pagination: {
        total: number;
        limit: number;
        offset: number;
    };
};

const BASE_PATH = '/gallery';

export const galleryApi = {
    /**
     * Get a presigned URL for uploading an image
     */
    getPresignedUploadUrl: async (request: PresignedUrlRequest): Promise<PresigedUrlResponse> => {
        const response = await httpClient.post<PresigedUrlResponse>(`${BASE_PATH}/images/presign`, request);
        return response.data;
    },

    /**
     * Upload an image to S3 using a presigned URL
     */
    uploadToPresignedUrl: async (presignedUrl: PresigedUrlResponse, file: File, onProgress?: (progress: number) => void): Promise<void> => {
        const formData = new FormData();

        // Add all the fields from the presigned URL response
        Object.entries(presignedUrl.fields).forEach(([key, value]) => {
            formData.append(key, value);
        });


        // Add the file to upload
        formData.append('file', file);

        // Use XMLHttpRequest to track upload progress
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // Track progress if a callback is provided
            if (onProgress) {
                xhr.upload.addEventListener('progress', (event) => {
                    if (event.lengthComputable) {
                        const progress = Math.round((event.loaded / event.total) * 100);
                        onProgress(progress);
                    }
                });
            }

            xhr.open('POST', presignedUrl.url);

            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve();
                } else {
                    console.error('Upload failed for file:', file.name, 'Status:', xhr.status, 'Response:', xhr.responseText);
                    reject(new Error(`Upload failed with status ${xhr.status}`));
                }
            };

            xhr.onerror = () => reject(new Error('Network error during upload'));

            xhr.send(formData);
        });
    },

    /**
     * Tegister image metadata after upload
     */
    registerImageMetadata: async (metadata: ImageMetadata) => {
        const response = await httpClient.post<ImageMetadata>(`${BASE_PATH}/images/`, metadata);
        return response.data;
    },

    /**
     * Handle the complete upload process
     */
    uploadImage: async (
        file: File,
        metadata: Omit<ImageMetadata, 'uri' | 'width' | 'height'>,
        onProgress?: (progress: number) => void
    ): Promise<void> => {
        // 1. Get image dimensions if needed
        let width = 0;
        let height = 0;

        if (file.type.startsWith('image/')) {
            // Get image dimensions
            const dimensions = await new Promise<{ width: number; height: number }>((resolve) => {
                const img = new Image();
                img.onload = () => resolve({ width: img.width, height: img.height });
                img.src = URL.createObjectURL(file);
            });

            width = dimensions.width;
            height = dimensions.height;
        }

        // 2. Request presigned URL from the API
        const presignedData = await galleryApi.getPresignedUploadUrl({
            filename: file.name,
            mimeType: file.type,
            size: file.size
        });

        // 3. Upload the image to S3 using the presigned URL
        await galleryApi.uploadToPresignedUrl(presignedData, file, onProgress);

        // 4. Register the image metadata with the backend
        await galleryApi.registerImageMetadata({
            ...metadata,
            uri: `${presignedData.url}/${presignedData.fields.key}`,
            width,
            height
        });
    },

    /**
     * Fetch all images metadatas
     */
    getAllImagesMetadata: async (): Promise<ImageMetadata[]> => {
        const response = await httpClient.get<GetAllImagesResponse>(`${BASE_PATH}/images/`);
        return response.data.items;
    }
};
