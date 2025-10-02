import React from "react";
import { Button, Box, Typography, Container, Paper } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useApp } from "../hooks/useApp";

const UnauthorizedPage: React.FC = () => {
    const navigate = useNavigate();
    const { logout } = useAuth();
    const { setDocumentTitle } = useApp();

    React.useEffect(() => {
        setDocumentTitle("Unauthorized");
    }, [setDocumentTitle]);

    const handleGoHome = () => {
        void navigate("/");
    };

    const handleLogout = async () => {
        await logout();
        void navigate("/login");
    };

    return (
        <Container component="main" maxWidth="sm">
            <Box
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
                    <Typography component="h1" variant="h5" align="center" gutterBottom>
                        Unauthorized Access
                    </Typography>
                    <Typography align="center" paragraph>
                        You don't have permission to access this resource.
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
                        <Button
                            variant="outlined"
                            onClick={handleGoHome}
                        >
                            Go to Home
                        </Button>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={() => void handleLogout()}
                        >
                            Sign Out
                        </Button>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default UnauthorizedPage;