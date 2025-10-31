import axios from 'axios';

interface Model {
    id: number;
    name: string;
    type: "checkpoint" | "lora";
    air: string;
    hash: string;
};

interface Hash {
    AutoV1: string;
    AutoV2: string;
    AutoV3: string;
    BLAKE3: string;
    CRC32: string;
    SHA256: string;
}

interface CivitaiModelVersionResponse {
    modelId: number;
    name: string;
    air: string;
    model: {
        type: string;
    };
    files: {
        hashes: Hash;
    }[];
};

interface CivitaiModelResponse {
    id: number;
    name: string;
    type: string;
    modelVersions: CivitaiModelVersionResponse[];
};

const BASE_URL = import.meta.env.VITE_CIVITAI_API_BASE_URL as string || 'https://civitai.com/api/v1';

const HASH_VERSION_TO_USE = import.meta.env.VITE_CIVITAI_HASH_VERSION_TO_USE as keyof Hash || 'CRC32';

const civitaiAxios = axios.create({
    baseURL: BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const civitaiApi = {
    getModelByVersionId: async (versionId: number): Promise<Model> => {
        /**
         * This assumes the first file is the one we want.
         */
        const response = await civitaiAxios.get<CivitaiModelVersionResponse>(`/model-versions/${versionId}`);
        const data = response.data;

        const model: Model = {
            id: data.modelId,
            name: data.name,
            type: data.model.type.toLowerCase() === 'lora' ? 'lora' : 'checkpoint',
            air: data.air,
            hash: data.files[0].hashes[HASH_VERSION_TO_USE],
        };
        return model;
    },
    getModelById: async (modelId: number): Promise<Model> => {
        /**
         * This assumes the first model version and first file are the ones we want.
         */
        const response = await civitaiAxios.get<CivitaiModelResponse>(`/models/${modelId}`);
        const data = response.data;

        const model: Model = {
            id: data.id,
            name: data.name,
            type: data.type.toLowerCase() === 'lora' ? 'lora' : 'checkpoint',
            air: data.modelVersions[0].air,
            hash: data.modelVersions[0].files[0].hashes[HASH_VERSION_TO_USE]
        };
        return model;
    },
    getModelByHash: async (hash: string): Promise<Model | null> => {
        const response = await civitaiAxios.get<CivitaiModelVersionResponse>(`/model-versions/by-hash/${hash}`);
        const data = response.data;

        if (!data) {
            return null;
        }

        const model: Model = {
            id: data.modelId,
            name: data.name,
            type: data.model.type.toLowerCase() === 'lora' ? 'lora' : 'checkpoint',
            air: data.air,
            hash: data.files[0].hashes[HASH_VERSION_TO_USE]
        };
        return model;
    },
    searchLoras: async (query: string): Promise<Model[]> => {
        const response = await civitaiAxios.get<{ items: CivitaiModelResponse[] }>(`/models`, {
            params: {
                query: `'${query}'`,
                types: 'LORA',
                limit: 30,
                sort: 'Highest Rated',
                period: 'AllTime',
                nsfw: true,
            },
        });
        const data = response.data;
        const models: Model[] = data.items.map((item) => ({
            id: item.id,
            name: item.name,
            type: 'lora',
            air: item.modelVersions[0].air,
            hash: item.modelVersions[0].files[0].hashes[HASH_VERSION_TO_USE],
        }));
        return models;
    },
};
