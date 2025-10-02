import React, { useState, useEffect, type ReactNode, useMemo } from 'react';
import { AppContext, type AppContextType } from '../hooks/useApp';

interface AppProviderProps {
    children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
    const [documentTitle, setDocumentTitle] = useState<string>('');
    const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);

    const toggleDrawer = () => {
        setIsDrawerOpen((prev) => !prev);
    };

    useEffect(() => {
        if (documentTitle) {
            document.title = documentTitle + ' — MiraVeja';
        } else {
            document.title = 'MiraVeja';
        }
    }, [documentTitle]);

    useEffect(() => {
        localStorage.setItem('isDrawerOpen', JSON.stringify(isDrawerOpen));
    }, [isDrawerOpen]);

    useEffect(() => {
        const storedState = localStorage.getItem('isDrawerOpen');
        if (storedState !== null) {
            setIsDrawerOpen(JSON.parse(storedState) as boolean);
        }
    }, []);

    const value = useMemo<AppContextType>(() => ({
        documentTitle,
        setDocumentTitle,
        isDrawerOpen,
        toggleDrawer,
    }), [documentTitle, isDrawerOpen]);

    return (
        <AppContext value={value}>
            {children}
        </AppContext>
    );
};