import { BrowserRouter, Routes, Route } from "react-router-dom";
import NotFound from "../views/NotFound";
import HomePage from "../views/HomePage";

function AppRoutes() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    )
}

export default AppRoutes;
