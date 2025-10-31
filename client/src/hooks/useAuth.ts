import Keycloak from 'keycloak-js';
import { createContext, use } from 'react';

export interface AuthContextProps {
    keycloak: Keycloak | null;
    initialized: boolean;
    authenticated: boolean;
    token: string | null;
    loading: boolean;
    error: Error | null;
    login: () => Promise<void>;
    logout: () => Promise<void>;
    updateToken: (minValidity?: number) => Promise<boolean>;
    hasRole: (role: string) => boolean;
};

export const AuthContext = createContext<AuthContextProps>({
    keycloak: null,
    initialized: false,
    authenticated: false,
    token: null,
    loading: true,
    error: null,
    login: () => Promise.resolve(),
    logout: () => Promise.resolve(),
    updateToken: () => Promise.resolve(false),
    hasRole: () => false,
});

export const useAuth = (): AuthContextProps => {
    return use(AuthContext);
};
