import React, { useState, useEffect, useMemo, type ReactNode } from 'react';
import { AppContext, type AppContextType } from '../hooks/useApp';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

interface AppProviderProps {
    children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
    const [documentTitle, setDocumentTitle] = useState<string>('');
    const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);

    const theme = useTheme();
    const isBigScreen = useMediaQuery(theme.breakpoints.up('sm')); // true if >= 'sm', false on smartphones

    const toggleDrawer = () => {
        setIsDrawerOpen((prev) => !prev);
    };

    // Update document title
    useEffect(() => {
        document.title = documentTitle ? `${documentTitle} — MiraVeja` : 'MiraVeja';
    }, [documentTitle]);

    // Persist drawer state
    useEffect(() => {
        localStorage.setItem('isDrawerOpen', JSON.stringify(isDrawerOpen));
    }, [isDrawerOpen]);

    useEffect(() => {
        const storedState = localStorage.getItem('isDrawerOpen');
        if (storedState !== null) {
            setIsDrawerOpen(JSON.parse(storedState) as boolean);
        }
    }, []);

    const value = useMemo<AppContextType & { isBigScreen: boolean }>(() => ({
        documentTitle,
        setDocumentTitle,
        isDrawerOpen,
        toggleDrawer,
        isBigScreen,
    }), [documentTitle, isDrawerOpen, isBigScreen]);

    return (
        <AppContext value={value}>
            {children}
        </AppContext>
    );
};
