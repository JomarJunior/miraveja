import React from "react";
import * as MuiMaterial from "@mui/material";
import { useApp } from "../hooks/useApp";
import { useUser } from "../hooks/useUser";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { useGallery } from "../hooks/useGallery";

interface NavigationItem {
    label: string;
    path: string;
    icon: string;
}

export default function HomePage() {
    const { setDocumentTitle } = useApp();
    const [navigationItems] = React.useState<NavigationItem[]>([
        { label: "Image Scroller", path: "/scroller", icon: "image" },
    ]);
    const { authenticated } = useAuth();
    const { firstName, lastName } = useUser();
    const navigate = useNavigate();
    const { images, isLoading, fetchAllImagesMetadata } = useGallery();

    const handleNavigation = (path: string) => {
        void navigate(path);
    }

    React.useEffect(() => {
        setDocumentTitle("Home");
    }, [setDocumentTitle]);

    React.useEffect(() => {
        void fetchAllImagesMetadata();
    }, [fetchAllImagesMetadata]);

    React.useEffect(() => {
        console.log("isLoading changed:", isLoading);
    }, [isLoading]);

    React.useEffect(() => {
        console.log("images changed:", images);
        console.log("Number of images:", images.length);
    }, [images]);

    return (
        <MuiMaterial.Container>
            <MuiMaterial.Typography variant="h1" sx={{ mt: 5, textAlign: 'center' }}>
                MiraVeja
            </MuiMaterial.Typography>
            <MuiMaterial.Typography variant="h5" sx={{ mt: 3, textAlign: 'center' }}>
                {authenticated ? "Welcome back, " + firstName + " " + lastName + "!" : "Welcome to MiraVeja!"}
            </MuiMaterial.Typography>
            <MuiMaterial.Divider sx={{ my: 4 }} />
            <MuiMaterial.Box sx={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap' }}>
                {navigationItems.map((item) => (
                    <MuiMaterial.Button
                        key={item.path}
                        onClick={() => handleNavigation(item.path)}
                        startIcon={<MuiMaterial.Icon>{item.icon}</MuiMaterial.Icon>}
                        variant="contained"
                        sx={{ m: 1 }}
                    >
                        {item.label}
                    </MuiMaterial.Button>
                ))}
            </MuiMaterial.Box>
            <MuiMaterial.Divider sx={{ my: 4 }} />
            {!(Array.isArray(images) && images.length) && isLoading ? (
                <MuiMaterial.CircularProgress />
            ) : (
                <MuiMaterial.Grid container spacing={2} justifyContent="center">
                    {images.length > 0 && images.map((image) => (
                        <MuiMaterial.Grid key={image.uri}>
                            <MuiMaterial.Card>
                                <MuiMaterial.CardMedia
                                    component="img"
                                    image={image.uri}
                                    alt={image.title}
                                    sx={{
                                        maxWidth: 800,
                                        maxHeight: 800,
                                        objectFit: 'cover'
                                    }}
                                />
                                <MuiMaterial.CardContent>
                                    <MuiMaterial.Typography variant="h6">
                                        {image.title}
                                    </MuiMaterial.Typography>
                                    <MuiMaterial.Typography variant="body2" color="text.secondary">
                                        {image.description}
                                    </MuiMaterial.Typography>
                                    <MuiMaterial.Typography variant="body2" color="text.secondary">
                                        {image.ownerId}
                                    </MuiMaterial.Typography>
                                </MuiMaterial.CardContent>
                            </MuiMaterial.Card>
                        </MuiMaterial.Grid>
                    ))}
                </MuiMaterial.Grid>
            )}
        </MuiMaterial.Container>
    );
}
