import React, { useState, useEffect, type ReactNode, useMemo, useCallback } from 'react';
import Keycloak from 'keycloak-js';
import { AuthContext, type AuthContextProps } from '../hooks/useAuth.ts';

interface AuthProviderProps {
    children: ReactNode;
    keycloakConfig: Keycloak.KeycloakConfig;
    initOptions?: Keycloak.KeycloakInitOptions;
    onTokens?: (tokens: { token: string; refreshToken: string; }) => void;
}

const defaultInitOptions: Keycloak.KeycloakInitOptions = {
    onLoad: 'check-sso',
    silentCheckSsoRedirectUri: `${window.location.origin}/miraveja/public/silent-check-sso.html`,
};

export const AuthProvider: React.FC<AuthProviderProps> = ({
    children,
    keycloakConfig,
    initOptions = defaultInitOptions,
    onTokens,
}) => {
    const [keycloak, setKeycloak] = useState<Keycloak | null>(null);
    const [initialized, setInitialized] = useState<boolean>(false);
    const [authenticated, setAuthenticated] = useState<boolean>(false);
    const [token, setToken] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const initKeycloak = async () => {
            console.log('Starting Keycloak initialization');
            try {
                /** Initialize Keycloak */
                console.log('Creating Keycloak instance');
                const keycloakInstance = new Keycloak(keycloakConfig);
                console.log('Initializing Keycloak with config:', keycloakConfig, 'and options:', initOptions);

                const authenticated = await keycloakInstance.init(initOptions);
                console.log('Keycloak initialized. Authenticated:', authenticated);

                setKeycloak(keycloakInstance);
                setInitialized(true);
                setAuthenticated(authenticated);
                setToken(keycloakInstance.token ?? null);

                /** Check if tokens are received */
                const hasReceivedTokens = authenticated && keycloakInstance.token && keycloakInstance.refreshToken;
                if (hasReceivedTokens && onTokens) {
                    /** Provide tokens to the callback */
                    onTokens({
                        token: keycloakInstance.token!,
                        refreshToken: keycloakInstance.refreshToken!,
                    });
                }

                /** Set up token refresh interval */
                if (authenticated) {
                    setInterval(() => {
                        keycloakInstance.updateToken(70).then((refreshed) => {
                            const hasNewTokens = refreshed && keycloakInstance.token && keycloakInstance.refreshToken;
                            if (hasNewTokens && onTokens) {
                                /** Provide new tokens to the callback */
                                onTokens({
                                    token: keycloakInstance.token!,
                                    refreshToken: keycloakInstance.refreshToken!,
                                });
                                setToken(keycloakInstance.token!);
                            }
                        }).catch(async () => {
                            await keycloakInstance.login();
                        });
                    }, 60000); // Refresh every 60 seconds
                }
            } catch (error) {
                console.error('Error during Keycloak initialization:', error);
                setError(error instanceof Error ? error : new Error('Unknown error during Keycloak initialization'));
            } finally {
                setLoading(false);
            }
        };

        void initKeycloak(); // Void to ignore the returned promise
    }, [keycloakConfig, initOptions, onTokens]);

    const login = useCallback(async (): Promise<void> => {
        console.log('Login called');
        if (keycloak) {
            console.log('Keycloak instance exists, proceeding to login');
            try {
                await keycloak.login();
                setAuthenticated(true);
                setToken(keycloak.token ?? null);
            } catch (error) {
                setError(error instanceof Error ? error : new Error('Unknown error during login'));
            }
        }
        console.log('Login process completed');
    }, [keycloak]);

    const logout = useCallback(async (): Promise<void> => {
        if (keycloak) {
            try {
                await keycloak.logout();
                setAuthenticated(false);
                setToken(null);
            } catch (error) {
                setError(error instanceof Error ? error : new Error('Unknown error during logout'));
            }
        }
    }, [keycloak]);

    const updateToken = useCallback(async (minValidity: number | undefined): Promise<boolean> => {
        if (!keycloak) return false;

        try {
            const refreshed = await keycloak.updateToken(minValidity);
            setToken(keycloak.token ?? null);
            return refreshed;
        } catch (error) {
            setError(error instanceof Error ? error : new Error('Unknown error during token update'));
            return false;
        }
    }, [keycloak]);

    const hasRole = useCallback((role: string): boolean => {
        return keycloak?.hasRealmRole(role) ?? false;
    }, [keycloak]);

    const contextValue = useMemo<AuthContextProps>(() => ({
        keycloak,
        initialized,
        authenticated,
        token,
        loading,
        error,
        login,
        logout,
        updateToken,
        hasRole,
    }), [keycloak, initialized, authenticated, token, loading, error, login, logout, updateToken, hasRole]);

    return (
        <AuthContext value={contextValue}>
            {children}
        </AuthContext>
    );
};
