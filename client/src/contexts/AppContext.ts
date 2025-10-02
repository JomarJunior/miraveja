import React, { createContext, use, useState, useEffect, type ReactNode } from 'react';

interface AppContextType {
    documentTitle: string;
    setDocumentTitle: (title: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

interface AppProviderProps {
    children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
    const [documentTitle, setDocumentTitle] = useState<string>('');

    useEffect(() => {
        if (documentTitle) {
            document.title = documentTitle + ' — MiraVeja';
        }
    }, [documentTitle]);

    const value: AppContextType = {
        documentTitle,
        setDocumentTitle,
    };

    return React.createElement(AppContext.Provider, { value }, children);
};

export const useApp = (): AppContextType => {
    const context = use(AppContext);
    if (context === undefined) {
        throw new Error('useApp must be used within an AppProvider');
    }
    return context;
};