import React from "react";
import * as MuiMaterial from "@mui/material";
import { useApp } from "../contexts/AppContext";

interface NavigationItem {
    label: string;
    path: string;
    icon: string;
}

export default function HomePage() {
    const { setDocumentTitle } = useApp();
    const [navigationItems] = React.useState<NavigationItem[]>([
        { label: "Home", path: "./", icon: "home" },
        { label: "About", path: "./about", icon: "info" },
        { label: "Contact", path: "./contact", icon: "contact_mail" },
    ]);

    React.useEffect(() => {
        setDocumentTitle("Home");
    }, [setDocumentTitle]);

    return (
        <MuiMaterial.Container>
            <MuiMaterial.Typography variant="h1" sx={{ mt: 5, textAlign: 'center' }}>
                MiraVeja
            </MuiMaterial.Typography>
            <MuiMaterial.Typography variant="h5" sx={{ mt: 3, textAlign: 'center' }}>
                Welcome to the MiraVeja application!
            </MuiMaterial.Typography>
            <MuiMaterial.Divider sx={{ my: 4 }} />
            <MuiMaterial.Box sx={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap' }}>
                {navigationItems.map((item) => (
                    <MuiMaterial.Button
                        key={item.path}
                        href={item.path}
                        startIcon={<MuiMaterial.Icon>{item.icon}</MuiMaterial.Icon>}
                        variant="contained"
                        sx={{ m: 1 }}
                    >
                        {item.label}
                    </MuiMaterial.Button>
                ))}
            </MuiMaterial.Box>
        </MuiMaterial.Container>
    );
}
