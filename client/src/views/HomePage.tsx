import React from "react";
import * as MuiMaterial from "@mui/material";
import { useApp } from "../hooks/useApp";
import { useUser } from "../hooks/useUser";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { useGallery } from "../hooks/useGallery";
import { EventClient } from "../libs/event";
import type { DomainEvent } from "../libs/event/types";

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

    const handleButtonPress = () => {
        const socket = new WebSocket("ws://localhost:9092");
        const eventClient = new EventClient(socket);

        const sampleEvent: DomainEvent<unknown> = {
            id: "event-123",
            topic: "miraveja.member.fetch.v1",
            type: "miraveja.member.fetch",
            aggregateId: "aggregate-456",
            aggregateType: "image",
            version: 1,
            occurredAt: new Date().toISOString(),
            payload: {
            },
        };

        eventClient.publish(sampleEvent);
    };

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
            <MuiMaterial.Box sx={{ textAlign: 'center' }}>
                <MuiMaterial.Button variant="outlined" onClick={handleButtonPress}>
                    Send Sample Event
                </MuiMaterial.Button>
            </MuiMaterial.Box>
        </MuiMaterial.Container>
    );
}
