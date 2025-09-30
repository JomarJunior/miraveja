import { BrowserRouter, Routes, Route } from "react-router-dom";
import NotFound from "../views/NotFound";
import HomePage from "../views/HomePage";

const basename = (import.meta.env.VITE_FRONTEND_BASE_PATH as string) ?? "";

function AppRoutes() {
    return (
        <BrowserRouter basename={basename}>
            <Routes>
                <Route index path="/" element={<HomePage />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    )
}

export default AppRoutes;
