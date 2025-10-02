import { createContext, use } from 'react';

export interface UserContextProps {
    id: string | null;
    username: string | null;
    firstName: string | null;
    lastName: string | null;
    email: string | null;
    loading: boolean;
}

export const UserContext = createContext<UserContextProps>({
    id: null,
    username: null,
    firstName: null,
    lastName: null,
    email: null,
    loading: true,
});

export const useUser = (): UserContextProps => {
    return use(UserContext);
};
