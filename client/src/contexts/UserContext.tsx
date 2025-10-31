import React, { useState, useEffect, type ReactNode, useMemo, useCallback } from 'react';
import { UserContext, type UserContextProps } from '../hooks/useUser.ts';
import { useAuth } from '../hooks/useAuth.ts';

interface UserProviderProps {
    children: ReactNode;
};

export const UserProvider: React.FC<UserProviderProps> = ({
    children,
}) => {
    const [id, setId] = useState<string | null>(null);
    const [username, setUsername] = useState<string | null>(null);
    const [firstName, setFirstName] = useState<string | null>(null);
    const [lastName, setLastName] = useState<string | null>(null);
    const [email, setEmail] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    const { keycloak, authenticated, token } = useAuth();

    const resetUserData = useCallback(() => {
        setId(null);
        setUsername(null);
        setFirstName(null);
        setLastName(null);
        setEmail(null);
    }, []);

    useEffect(() => {
        const fetchUserProfile = async () => {
            if (keycloak && authenticated) {
                try {
                    setLoading(true);
                    const profile = await keycloak.loadUserProfile();

                    setId(profile.id ?? null);
                    setUsername(profile.username ?? null);
                    setFirstName(profile.firstName ?? null);
                    setLastName(profile.lastName ?? null);
                    setEmail(profile.email ?? null);

                    /** Here we could also fetch extended data from our api */

                } catch (error) {
                    console.error('Failed to load user profile:', error);
                    resetUserData();
                } finally {
                    setLoading(false);
                }
            } else {
                resetUserData();
                setLoading(false);
            }
        };

        void fetchUserProfile(); // Void to ignore the returned promise
    }, [keycloak, authenticated, token, resetUserData]);

    const userContextValue: UserContextProps = useMemo(() => ({
        id,
        username,
        firstName,
        lastName,
        email,
        loading,
    }), [id, username, firstName, lastName, email, loading]);

    return (
        <UserContext value={userContextValue}>
            {children}
        </UserContext>
    );
};