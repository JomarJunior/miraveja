import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { CircularProgress, Box } from "@mui/material";

interface ProtectedRouteProps {
    children: React.ReactNode;
    requiredRoles?: string[];
    redirectTo?: string;
};

const defaultRequiredRoles: string[] = [];

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    requiredRoles = defaultRequiredRoles,
    redirectTo = "/unauthorized",
}) => {
    const { authenticated, loading, hasRole } = useAuth();
    const location = useLocation();

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
                <CircularProgress />
            </Box>
        );
    }

    if (!authenticated) {
        /** Save the location the user was trying to access */
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    /** Check if the user has all required roles */
    const hasRequiredRoles = requiredRoles.length === 0 || requiredRoles.every(role => hasRole(role));

    if (!hasRequiredRoles) {
        return <Navigate to={redirectTo} replace />;
    }

    return <>{children}</>;
};
