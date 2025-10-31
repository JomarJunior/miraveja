import { Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "../components/ProtectedRoute";
import NotFound from "../views/NotFound";
import LoginPage from "../views/LoginPage";
import UnauthorizedPage from "../views/UnauthorizedPage";
import HomePage from "../views/HomePage";
import PostPage from "../views/PostPage";
import ScrollerPage from "../views/ScrollerPage";


function AppRoutes() {
    return (
        <Routes>
            <Route index path="/" element={<HomePage />} />
            <Route path="/post" element={
                <ProtectedRoute>
                    <PostPage />
                </ProtectedRoute>
            } />
            <Route path="/scroller" element={<ScrollerPage />} />
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
