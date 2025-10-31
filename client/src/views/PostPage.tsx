import React from 'react';
import * as MuiMaterial from "@mui/material";
import { styled } from '@mui/material/styles';
import { type ImageMetadata, type GenerationMetadata } from '../api/gallery-api';
import { useGallery } from '../hooks/useGallery';
import { useApp } from '../hooks/useApp';
import type { MiraFormField } from '../components/MiraForm';
import MiraForm from '../components/MiraForm';
import { getImageMetadata } from '../utils/image-utils';
import { civitaiApi } from '../api/civitai-api';
import { useUser } from '../hooks/useUser';

const VisuallyHiddenInput = styled('input')({
    clip: 'rect(0 0 0 0)',
    clipPath: 'inset(50%)',
    height: 1,
    overflow: 'hidden',
    position: 'absolute',
    bottom: 0,
    left: 0,
    whiteSpace: 'nowrap',
    width: 1,
});

export default function PostPage() {
    const [imageFile, setImageFile] = React.useState<File | null>(null);
    const [imagePreview, setImagePreview] = React.useState<string | null>(null);
    const [imageMetadata, setImageMetadata] = React.useState<Omit<ImageMetadata, 'uri' | 'width' | 'height'> | null>(null);
    const [searchedLoras, setSearchedLoras] = React.useState<MiraFormField<GenerationMetadata>['items']>([]);
    const { id } = useUser();
    const { isBigScreen } = useApp();

    const globalStackDirection = isBigScreen ? 'row' : 'column';

    // Use the gallery context instead of direct API calls
    const { uploadStatus, uploadImage, resetUploadStatus } = useGallery();
    const { isUploading, progress, error, isComplete } = uploadStatus;

    /** Catch change on imageFile and call getImageMetadata */
    React.useEffect(() => {
        const fetchMetadata = async () => {
            if (imageFile) {
                try {
                    const metadata = await getImageMetadata(imageFile);
                    setImageMetadata(metadata);
                } catch (error) {
                    console.error("Error fetching image metadata:", error);
                }
            }
        };
        void fetchMetadata();
    }, [imageFile]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            const file = e.target.files[0];
            setImageFile(file);

            // Create preview
            const reader = new FileReader();
            reader.onload = (event) => {
                if (event.target && typeof event.target.result === 'string') {
                    setImagePreview(event.target.result);
                }
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = () => {
        if (!imageFile || !imageMetadata) return;
        if (!id) {
            console.error("User ID is not available");
            return;
        }

        uploadImage(imageFile, {
            ...imageMetadata,
            ownerId: id,
        }).catch((error) => {
            console.error("Error uploading image:", error);
        });
    };

    const resetForm = () => {
        setImageFile(null);
        setImagePreview(null);
        setImageMetadata(null);
        resetUploadStatus();
    };

    if (imagePreview === null) {
        // Display a big square at the center
        // This square is a button to upload an image
        return (
            <MuiMaterial.Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <MuiMaterial.Box sx={{ width: 300, height: 300, border: '2px dashed gray', borderRadius: 2, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <MuiMaterial.Button
                        component='label'
                        role={undefined}
                        variant='contained'
                        tabIndex={-1}
                        startIcon={<MuiMaterial.Icon>upload_file</MuiMaterial.Icon>}
                    >
                        Upload Image
                        <VisuallyHiddenInput
                            type='file'
                            accept='image/*'
                            onChange={(e) => { handleFileChange(e) }}
                        />
                    </MuiMaterial.Button>
                </MuiMaterial.Box>
            </MuiMaterial.Container>
        );
    }

    if (isComplete) {
        return (
            <MuiMaterial.Container sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <MuiMaterial.Typography variant='h4' gutterBottom>
                    Upload Complete!
                </MuiMaterial.Typography>
                <MuiMaterial.Typography variant='body1' gutterBottom>
                    Your image is being processed and will appear in the gallery shortly.
                </MuiMaterial.Typography>
                <MuiMaterial.Button variant='contained' onClick={resetForm} sx={{ mt: 2 }}>
                    Upload Another Image
                </MuiMaterial.Button>
            </MuiMaterial.Container>
        );
    }

    const handleMetadataChange = (field: string, value: unknown) => {
        setImageMetadata(prevMetadata => ({
            ...prevMetadata ?? {},
            [field]: value
        }) as Omit<ImageMetadata, 'uri' | 'width' | 'height'>);
    };

    const handleGenerationMetadataChange = (field: string, value: unknown) => {
        if (field === 'loras' && Array.isArray(value)) {
            interface LoraData {
                name: string;
                [key: string]: unknown;
            }

            value = value.map((v: { value: string }) => {
                try {
                    return JSON.parse(v.value) as LoraData;
                } catch {
                    return null;
                }
            }).filter((v) => v !== null);
        }

        if (field === 'seed' && typeof value !== 'string') {
            value = String(value);
        }

        setImageMetadata(prevMetadata => ({
            ...prevMetadata ?? {},
            generationMetadata: {
                ...prevMetadata?.generationMetadata,
                [field]: value
            }
        }) as Omit<ImageMetadata, 'uri' | 'width' | 'height'>);
    };

    const handleMiraFormInputChange = (field: string, value: unknown) => {
        // Currently only 'loras' field requires input change handling
        if (field === 'loras') {
            const query = typeof value === 'string' ? value : '';
            civitaiApi.searchLoras(query).then((models) => {
                setSearchedLoras(models.map((model) => ({ label: model.name, value: JSON.stringify(model) })));
            }).catch((error) => {
                console.error("Error searching loras:", error);
            });
        }
    };

    const renderImageMetadataFields = () => {
        return (<>
            <MuiMaterial.TextField
                variant='standard'
                fullWidth
                value={imageMetadata?.title ?? ''}
                placeholder='Title'
                multiline
                onChange={(e) => handleMetadataChange('title', e.target.value)}
                slotProps={{
                    input: {
                        disableUnderline: true,
                    },
                    htmlInput: {
                        style: {
                            textAlign: 'center',
                        }
                    },
                    root: {
                        style: {
                            borderBottom: 'none',
                        }
                    }
                }}
                sx={{
                    m: 0,
                    '& .MuiInputBase-input': {
                        typography: 'h3',
                        fontWeight: 'bold',
                    }
                }}
            />

            <MuiMaterial.TextField
                variant='standard'
                fullWidth
                value={imageMetadata?.subtitle ?? ''}
                placeholder='Subtitle'
                onChange={(e) => handleMetadataChange('subtitle', e.target.value)}
                slotProps={{
                    input: {
                        disableUnderline: true,
                    },
                    htmlInput: {
                        style: {
                            textAlign: 'center',
                        }
                    },
                    root: {
                        style: {
                            borderBottom: 'none',
                        }
                    }
                }}
                sx={{
                    m: 0,
                    '& .MuiInputBase-input': {
                        typography: 'h5',
                        fontStyle: 'italic',
                    },
                }}
            />

            <MuiMaterial.Divider />

            <MuiMaterial.TextField
                variant='outlined'
                fullWidth
                value={imageMetadata?.description ?? ''}
                placeholder='Describe your amazing image with astonishing details...'
                onChange={(e) => handleMetadataChange('description', e.target.value)}
                slotProps={{
                    htmlInput: {
                        style: {
                            textAlign: 'center',
                            height: '100px',
                        }
                    },
                }}
                sx={{
                    m: 0,
                    '& .MuiInputBase-input': {
                        typography: 'legend',
                    },
                }}
            />
        </>
        );
    }

    const renderGenerationMetadataFields = () => {
        const fields: MiraFormField<GenerationMetadata>[] = [
            {
                label: 'Model',
                field: 'model',
                type: 'text',
                placeholder: 'Stable Diffusion v1.5',
                icon: <MuiMaterial.Icon>memory</MuiMaterial.Icon>,
            },
            {
                label: 'Prompt',
                field: 'prompt',
                type: 'textarea',
                placeholder: 'masterpiece, best quality, a beautiful landscape, vibrant colors, detailed, 4k',
                icon: <MuiMaterial.Icon>lightbulb</MuiMaterial.Icon>,
            },
            {
                label: 'Negative Prompt',
                field: 'negativePrompt',
                type: 'textarea',
                placeholder: 'low quality, blurry, deformed, bad anatomy',
                icon: <MuiMaterial.Icon>block</MuiMaterial.Icon>,
            },
            {
                label: 'Loras',
                field: 'loras',
                type: 'loraselect',
                icon: <MuiMaterial.Icon>extension</MuiMaterial.Icon>,
                items: searchedLoras,
                defaultValue: imageMetadata?.generationMetadata?.loras?.map((lora) => ({ label: lora.name, value: JSON.stringify(lora) })) ?? [],
            },
            {
                label: 'CFG Scale',
                field: 'cfgScale',
                type: 'number',
                defaultValue: 5.0,
                icon: <MuiMaterial.Icon>tune</MuiMaterial.Icon>,
            },
            {
                label: 'Seed',
                field: 'seed',
                type: 'number',
                icon: <MuiMaterial.Icon>casino</MuiMaterial.Icon>,
            },
            {
                label: 'Sampler',
                field: 'sampler',
                type: 'text',
                placeholder: 'DPM++ 2M',
                icon: <MuiMaterial.Icon>shuffle</MuiMaterial.Icon>,
            },
            {
                label: 'Scheduler',
                field: 'scheduler',
                type: 'text',
                placeholder: 'Karras',
                icon: <MuiMaterial.Icon>schedule</MuiMaterial.Icon>,
            },
            {
                label: 'Steps',
                field: 'steps',
                type: 'number',
                defaultValue: 20,
                icon: <MuiMaterial.Icon>directions_walk</MuiMaterial.Icon>,
            },
            {
                label: 'Size',
                field: 'size',
                type: 'text',
                placeholder: '512x512',
                icon: <MuiMaterial.Icon>photo_size_select_large</MuiMaterial.Icon>,
            },
        ];

        return (
            <>
                <MuiMaterial.Typography variant='overline'>
                    <MuiMaterial.Icon sx={{ fontSize: 16, verticalAlign: 'middle', mr: 2 }}>auto_mode</MuiMaterial.Icon>
                    Generation Metadata
                </MuiMaterial.Typography>
                <MuiMaterial.Divider />
                <MiraForm
                    target={imageMetadata?.generationMetadata ?? {} as GenerationMetadata}
                    fields={fields}
                    onChange={(updatedMetadata, field) => {
                        handleGenerationMetadataChange(field, updatedMetadata[field]);
                    }}
                    onInputChange={(field, value) => {
                        handleMiraFormInputChange(field, value);
                    }}
                />
            </>
        );
    }

    return (
        <MuiMaterial.Container sx={{ width: '100%', px: 0 }} maxWidth='xl'>
            <MuiMaterial.Stack
                spacing={2}
                direction={globalStackDirection}
            >
                <MuiMaterial.Stack spacing={2} sx={{ flexGrow: 2 }}>
                    <MuiMaterial.Box sx={{
                        width: '100%',
                        height: { xs: '60vh', sm: '65vh' },
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        position: 'relative',
                        mb: 4,
                    }}>
                        <MuiMaterial.Box
                            component='img'
                            src={imagePreview}
                            alt='Image Preview'
                            sx={{
                                maxWidth: '100%',
                                maxHeight: '100%',
                                m: 0,
                                p: 0,
                            }}
                        />
                        <MuiMaterial.Button
                            component='label'
                            sx={{
                                display: 'flex', flexDirection: 'row-reverse', alignItems: 'end',
                                position: 'absolute',
                                top: 'auto',
                                bottom: 0,
                                right: 0,
                                pr: 1,
                                pb: 0.5,
                                width: '100%',
                                height: '100%',
                                textAlign: 'right',
                                borderRadius: 0,
                                border: 'none',
                                background: 'linear-gradient(to bottom, rgba(0, 0, 0, 0) 70%, rgba(0, 0, 0, 0.9)) 100%',
                            }}
                        >
                            <MuiMaterial.Typography variant='caption' color='inherit'>
                                <MuiMaterial.Icon sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }}>refresh</MuiMaterial.Icon>
                                Change Image
                            </MuiMaterial.Typography>
                            <VisuallyHiddenInput
                                type='file'
                                accept='image/*'
                                onChange={(e) => { handleFileChange(e) }}
                            />
                        </MuiMaterial.Button>
                    </MuiMaterial.Box>
                    <MuiMaterial.Box
                        sx={{
                            flexGrow: 1,
                            height: '100%',
                        }}
                    >
                        <MuiMaterial.Stack spacing={2}>
                            {renderImageMetadataFields()}
                        </MuiMaterial.Stack>
                    </MuiMaterial.Box>
                    {error && (
                        <MuiMaterial.Alert severity='error' sx={{ mb: 2 }}>
                            {error}
                        </MuiMaterial.Alert>
                    )}
                </MuiMaterial.Stack>


                <MuiMaterial.Box
                    sx={{
                        borderLeft: globalStackDirection === 'row' && imageMetadata?.isAiGenerated ? 1 : 0,
                        borderColor: 'primary.main',
                        px: 2,
                        width: {
                            xs: '100%',
                            sm: globalStackDirection === 'row' ? '300px' : '100%',
                            md: globalStackDirection === 'row' ? '15vw' : '100%',
                            lg: globalStackDirection === 'row' ? '15vw' : '100%',
                            xl: globalStackDirection === 'row' ? '12vw' : '100%',
                        },
                    }}
                >
                    <MuiMaterial.Stack spacing={1}>
                        <MuiMaterial.Button
                            fullWidth
                            variant='contained'
                            color='primary'
                            onClick={handleSubmit}
                            disabled={isUploading || !imageMetadata?.title}
                        >
                            <MuiMaterial.Icon sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }}>upload</MuiMaterial.Icon>
                            {isUploading ? `Uploading... (${progress}%)` : 'Submit'}
                        </MuiMaterial.Button>
                        <MuiMaterial.FormControlLabel
                            control={
                                <MuiMaterial.Checkbox
                                    checked={imageMetadata?.isAiGenerated ?? false}
                                    onChange={(e) => handleMetadataChange('isAiGenerated', e.target.checked ? true : false)}
                                />
                            }
                            label='AI Generated'
                        />

                        {imageMetadata?.isAiGenerated && renderGenerationMetadataFields()}
                    </MuiMaterial.Stack>
                </MuiMaterial.Box>
            </MuiMaterial.Stack>
        </MuiMaterial.Container>
    );
}
