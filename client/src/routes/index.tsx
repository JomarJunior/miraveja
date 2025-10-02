import { Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "../components/ProtectedRoute";
import NotFound from "../views/NotFound";
import LoginPage from "../views/LoginPage";
import UnauthorizedPage from "../views/UnauthorizedPage";
import HomePage from "../views/HomePage";


function AppRoutes() {
    return (
        <Routes>
            <Route index path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="/test-protected" element={
                <ProtectedRoute>
                    <div>Protected Content</div>
                </ProtectedRoute>
            } />
            <Route path="/test-protected-admin" element={
                <ProtectedRoute requiredRoles={['admin']}>
                    <div>Protected Admin Content</div>
                </ProtectedRoute>
            } />
            <Route path="*" element={<NotFound />} />
        </Routes>
    )
}

export default AppRoutes;
