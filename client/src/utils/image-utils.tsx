import type { GenerationMetadata, ImageMetadata } from "../api/gallery-api";
import { civitaiApi } from "../api/civitai-api";

const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const JPEG_SIGNATURE = [0xff, 0xd8];

const getImageMetadata = async (file: File): Promise<Omit<ImageMetadata, 'id' | 'ownerId' | 'vectorId' | 'createdAt' | 'updatedAt'>> => {
    const generationMetadata = await getGenerationMetadata(file);

    // Get image dimensions
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);
    img.src = objectUrl;

    return new Promise((resolve) => {
        img.onload = () => {
            URL.revokeObjectURL(objectUrl);
            resolve(
                {
                    title: file.name,
                    subtitle: '',
                    description: '',
                    width: img.width,
                    height: img.height,
                    repositoryType: 'S3',
                    isAiGenerated: Object.keys(generationMetadata).length > 0,
                    generationMetadata: Object.keys(generationMetadata).length > 0 ? generationMetadata : null,
                }
            );
        };
    });
};

const getGenerationMetadata = async (file: File): Promise<Omit<GenerationMetadata, 'id' | 'imageId'>> => {
    try {
        const buffer = await file.arrayBuffer();
        const arr = new Uint8Array(buffer);

        let rawText: string | null = null;
        if (isPng(arr)) {
            rawText = parsePngForText(arr.buffer);
        } else if (isJpeg(arr)) {
            rawText = parseJpegForText(arr.buffer);
        } else {
            throw new Error("Unsupported image format");
        }

        const result = rawText ? await parseAutomatic1111Parameters(rawText) : null;

        return result ?? {} as GenerationMetadata;
    } catch (error) {
        console.error("Error extracting image metadata:", error);
        return {} as GenerationMetadata;
    }
};

const isPng = (arr: Uint8Array): boolean => {
    return arr.length > 8 && arr.slice(0, 8).every((byte, index) => byte === PNG_SIGNATURE[index]);
};

const isJpeg = (arr: Uint8Array): boolean => {
    return arr.length > 2 && arr.slice(0, 2).every((byte, index) => byte === JPEG_SIGNATURE[index]);
};

const parsePngForText = (buffer: ArrayBuffer): string | null => {
    const dv = new DataView(buffer);
    const decoder = new TextDecoder("utf-8");

    for (let i = 0; i < 8; i++) {
        if (dv.getUint8(i) !== PNG_SIGNATURE[i]) return null;
    }

    let offset = 8;
    const texts: string[] = [];

    const chunkParserMap: Record<string, (chunk: Uint8Array) => string | null> = {
        'tEXt': parsetEXtChunk,
        'iTXt': parseiTXtChunk,
    };

    while (offset + 8 <= dv.byteLength) {
        const length = dv.getUint32(offset); // Chunk data length
        const type = decoder.decode(new Uint8Array(buffer.slice(offset + 4, offset + 8)));
        const dataStart = offset + 8;
        const dataEnd = dataStart + length;
        if (dataEnd > dv.byteLength) break;

        if (type in chunkParserMap) {
            const chunkData = new Uint8Array(buffer.slice(dataStart, dataEnd));
            const text = chunkParserMap[type](chunkData);
            if (text) {
                texts.push(text);
            }
        }

        offset = dataEnd + 4; // Move to next chunk (skip CRC)
    }

    if (texts.length === 0) return null;

    return texts.join('\n');
}

const parsetEXtChunk = (chunk: Uint8Array): string => {
    const decoder = new TextDecoder("utf-8");
    const nulIndex = chunk.indexOf(0);

    if (nulIndex >= 0) {
        return decoder.decode(chunk.slice(nulIndex + 1));
    } else {
        return decoder.decode(chunk);
    }
};

const parseiTXtChunk = (chunk: Uint8Array): string | null => {
    const decoder = new TextDecoder("utf-8");
    const nulIndex = chunk.indexOf(0);

    if (nulIndex >= 0) {
        const lastNul = chunk.lastIndexOf(0);
        return decoder.decode(chunk.slice(lastNul + 1));
    }

    return decoder.decode(chunk);
};

const parseJpegForText = (buffer: ArrayBuffer): string | null => {
    const arr = new Uint8Array(buffer);
    const decoder = new TextDecoder("utf-8");
    let offset = 2; // Skip SOI
    const texts: string[] = [];

    while (offset + 4 < arr.length) {
        if (arr[offset] !== 0xFF) break; // Not a valid marker

        const marker = arr[offset + 1];
        offset += 2;

        // Meerkers 0xD0-0xD9 are standalone, no length; others have length
        if (marker === 0xd9) break; // EOI
        if (marker >= 0xd0 && marker <= 0xd9) continue;

        const len = (arr[offset] << 8) | arr[offset + 1];
        if (len < 2) break; // Invalid length

        const dataStart = offset + 2;
        const dataEnd = dataStart + len - 2;
        if (dataEnd > arr.length) break;

        // COM marker (0xFE) or APP1 marker (0xE1) can contain text/XMP
        if (marker === 0xfe /* COM */ || marker === 0xe1 /* APP1 */ || marker === 0xed /* APP13 */) {
            try {
                const seg = decoder.decode(arr.slice(dataStart, dataEnd));
                // XMP: usually contains "<x:xmpmeta" XML tag
                if (seg.includes('<x:xmpmeta') || seg.includes('parameters')) {
                    texts.push(seg);
                } else {
                    // also keep general ASCII text (comments)
                    // heuristic: if segment has many printable chars, include
                    const printableRatio = printableCharRatio(seg);
                    if (printableRatio > 0.6) texts.push(seg);
                }
            } catch (error) {
                console.error("Error decoding JPEG segment:", error);
            }
        }

        offset = dataEnd;
    }

    if (texts.length === 0) return null;

    return texts.join('\n');
};

const printableCharRatio = (text: string): number => {
    if (!text || text.length === 0) return 0;
    let printableCount = 0;
    for (let i = 0; i < text.length; i++) {
        const charCode = text.charCodeAt(i);
        if (charCode >= 32 && charCode <= 126) {
            printableCount++;
        }
    }
    return printableCount / text.length;
};

const parseAutomatic1111Parameters = async (text: string): Promise<Omit<GenerationMetadata, 'id' | 'imageId'> | null> => {
    /**
     * Automatic 1111 encodes parameters in the image comment or metadata in a specific format.
     * First it includes the prompt used to generate the image, 
     * then the negative prompt with the label "Negative prompt:",
     * followed by other parameters in "Key: Value, Key2: Value2, ..." format.
     *
     * Example:
     * "A beautiful landscape, high resolution, detailed, ...
     * Negative prompt: lowres, bad anatomy, ...
     * Steps: 20, ..."
     * 
     * Loras are part of the prompt in the format:
     * <lora:name:weight>
     */

    const result: Omit<GenerationMetadata, 'id' | 'imageId'> = {
        prompt: '',
        negativePrompt: '',
        steps: 0,
        model: '',
        sampler: '',
        scheduler: '',
        seed: '',
        cfgScale: 0,
        size: '',
        loras: []
    };

    const metaKeyAliases: Record<keyof Omit<GenerationMetadata, 'id' | 'imageId'>, string> = {
        scheduler: 'Schedule type',
        cfgScale: 'CFG Scale',
        steps: 'Steps',
        seed: 'Seed',
        model: 'Model',
        sampler: 'Sampler',
        size: 'Size',
        prompt: 'Prompt',
        negativePrompt: 'Negative prompt',
        loras: 'Loras'
    };

    // Extract prompt
    // Search for the first occurence of: newline followed by "Key: Value" where Key is non-space letters
    const parameterRegex = /\n([A-Za-z ]+):/;
    const match = parameterRegex.exec(text);
    const firstParameterIndex = match ? match.index : -1;
    if (firstParameterIndex === -1) {
        result.prompt = text.trim();
        return result;
    }

    result.prompt = text.slice(0, firstParameterIndex).replace(/Negative prompt:/i, '').trim();

    // Extract negative prompt if present
    const negativePromptMatch = /Negative prompt:(.*?)(\n|$)/i.exec(text);
    if (negativePromptMatch) {
        result.negativePrompt = negativePromptMatch[1].trim();
    }

    // If generated using CivitAI, things are easier to parse
    const civitaiResources = await parseCivitAiResources(text);

    const hasCivitaiData = civitaiResources.length > 0;
    if (hasCivitaiData) {
        // If CivitAI resources are found, we can use them to fill in some fields
        civitaiResources.forEach(resource => {
            if (resource.type === 'checkpoint') {
                result.model = resource.modelName;
            } else if (resource.type === 'lora') {
                result.loras.push(
                    {
                        id: resource.modelVersionId,
                        hash: resource.hash ?? '',
                        name: resource.modelName,
                    }
                );
            }
        });
    }

    // Extract other parameters
    const extractParameterByKey = <T,>(key: string, parser: (val: string) => T): T | null => {
        const regex = new RegExp(`${key}:\\s*([^,\\n]+)`, 'i');
        const match = regex.exec(text);
        if (match) {
            return parser(match[1].trim());
        }
        return null;
    };

    Object.keys(result).forEach((key) => {
        if (key === 'prompt' || key === 'negativePrompt' || key === 'loras') return;
        if (hasCivitaiData && (key === 'model')) return; // already filled from CivitAI data

        const alias = metaKeyAliases[key as keyof typeof metaKeyAliases];

        const value = extractParameterByKey(alias, (val) => {
            if (key === 'steps') return parseInt(val, 10);
            if (key === 'cfgScale') return parseFloat(val);
            return val;
        });

        if (value !== null) {
            (result as Record<string, unknown>)[key] = value;
        }
    });

    return result;
}

interface CivitaiResource {
    type: string;
    modelVersionId: number;
    modelName: string;
    weight?: number;
    hash?: string;
}

const parseCivitAiResources = async (text: string): Promise<CivitaiResource[]> => {
    /**
     * Images generated using CivitAI platform or extension include resource references.
     */
    const resources: CivitaiResource[] = [];
    const regex = /Civitai resources:\s*(\[[^\]]+\])/i;
    const match = regex.exec(text);
    if (match) {
        try {
            const jsonStr = match[1];
            const parsed = JSON.parse(jsonStr) as CivitaiResource[];
            resources.push(...parsed);
        } catch (error) {
            console.error('Error parsing CivitAI resources:', error);
        }
    }

    // For each resource, complete with data from CivitAI API if needed
    const updatedResources = await Promise.all(resources.map(async (resource) => {
        if (!resource.hash) {
            try {
                const versionData = await civitaiApi.getModelByVersionId(resource.modelVersionId);

                return {
                    ...resource,
                    hash: versionData.hash
                };
            } catch (error) {
                console.error(`Error fetching CivitAI model version ${resource.modelVersionId}:`, error);
            }
        }
        return resource;
    }));

    return updatedResources;
};

export { getImageMetadata, isPng, isJpeg };
