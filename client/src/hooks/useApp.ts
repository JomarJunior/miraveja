import { createContext, use } from 'react';

export interface AppContextType {
    documentTitle: string;
    setDocumentTitle: (title: string) => void;
    isDrawerOpen: boolean;
    isBigScreen: boolean;
    toggleDrawer: () => void;
}

export const AppContext = createContext<AppContextType | undefined>(undefined);

export const useApp = (): AppContextType => {
    const context = use(AppContext);
    if (context === undefined) {
        throw new Error('useApp must be used within an AppProvider');
    }
    return context;
};
