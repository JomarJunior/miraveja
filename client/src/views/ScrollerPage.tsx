import React from "react";
import * as MuiMaterial from "@mui/material";
import { useApp } from "../hooks/useApp";
// import { useUser } from "../hooks/useUser";
import { useGallery } from "../hooks/useGallery";
import ScrollerGallery from "../components/ScrollerGallery";
import { getAvailableSpace } from "../utils/layout-utils";

export default function ScrollerPage() {
    // State
    const { setDocumentTitle, isBigScreen } = useApp();
    // const { firstName, lastName } = useUser();
    const { images, isLoading, fetchAllImagesMetadata } = useGallery();
    const [currentImageIndex, setCurrentImageIndex] = React.useState(0);
    const [showFullDescription, setShowFullDescription] = React.useState(false);


    // Hooks
    React.useEffect(() => {
        setDocumentTitle("Images");
    }, [setDocumentTitle]);

    React.useEffect(() => {
        void fetchAllImagesMetadata();
    }, [fetchAllImagesMetadata]);

    // Handlers
    const handleOnImageChange = (newIndex: number) => {
        setCurrentImageIndex(newIndex);
    };


    if (isLoading) {
        return (
            <MuiMaterial.Container>
                <MuiMaterial.Typography variant="h5" sx={{ mt: 5, textAlign: 'center' }}>
                    Loading images...
                </MuiMaterial.Typography>
            </MuiMaterial.Container>
        );
    }

    const renderImagePanel = () => {
        if (images.length === 0) {
            return null;
        }

        return (<MuiMaterial.Box
            sx={{
                position: 'absolute',
                top: 0,
                right: 0,
                width: '30%',
                height: '100%',
                maxWidth: '100%',
                marginRight: 2,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'flex-start',
                zIndex: 10,
            }}>
            <MuiMaterial.Card>
                <MuiMaterial.CardContent>
                    {/* 
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
                    */}
                    <MuiMaterial.Typography variant="h5" gutterBottom>
                        {images[currentImageIndex].title || 'Untitled'}
                    </MuiMaterial.Typography>
                    <MuiMaterial.Typography variant="body1" sx={{
                        fontStyle: 'italic',
                    }}>
                        {images[currentImageIndex].subtitle}
                    </MuiMaterial.Typography>

                    <MuiMaterial.Box sx={{ mt: 1 }}>
                        {images[currentImageIndex].isAiGenerated && (
                            <MuiMaterial.Tooltip title="This image was generated using AI">
                                <MuiMaterial.Icon>
                                    smart_toy
                                </MuiMaterial.Icon>
                            </MuiMaterial.Tooltip>
                        )}
                    </MuiMaterial.Box>

                    <MuiMaterial.Divider />
                    <MuiMaterial.Typography sx={{ mt: 1 }} variant="body2">
                        {images[currentImageIndex].description}
                    </MuiMaterial.Typography>
                </MuiMaterial.CardContent>
            </MuiMaterial.Card>
        </MuiMaterial.Box>
        );
    };

    const handleMobileImagePanel = () => {
        if (images.length === 0) {
            return null;
        }


        return (
            <MuiMaterial.Box
                sx={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    p: 2,
                }}>
                <MuiMaterial.Typography variant="h6">
                    {images[currentImageIndex].title || 'Untitled'}
                </MuiMaterial.Typography>
                <MuiMaterial.Icon sx={{ verticalAlign: 'middle', mr: 1, fontSize: 20 }}>
                    smart_toy
                </MuiMaterial.Icon>
                {images[currentImageIndex].description && (
                    <div
                        style={{
                            display: '-webkit-box',
                            WebkitLineClamp: showFullDescription ? 'none' : 2,
                            WebkitBoxOrient: 'vertical',
                            width: '100%',
                            textAlign: 'justify',
                            overflow: 'hidden',
                            height: showFullDescription ? 'auto' : '50px',
                            textOverflow: showFullDescription ? 'none' : 'ellipsis',
                            marginTop: 1,
                        }}
                        onClick={
                            () => {
                                setShowFullDescription(!showFullDescription);
                            }
                        }
                    >
                        {images[currentImageIndex].description}
                    </div>
                )}
            </MuiMaterial.Box >
        );
    }

    return (
        <MuiMaterial.Container maxWidth="xl" disableGutters
            sx={{
                height: getAvailableSpace().height,
                overflow: 'hidden',
                position: 'relative',
            }}>
            <ScrollerGallery
                images={images}
                onNextImage={handleOnImageChange}
                onPreviousImage={handleOnImageChange}
            />
            {isBigScreen && renderImagePanel()}
            {!isBigScreen && handleMobileImagePanel()}
        </MuiMaterial.Container>
    );
};