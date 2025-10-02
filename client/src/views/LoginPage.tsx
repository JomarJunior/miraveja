import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Box, Typography, Container, Paper } from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import { useApp } from '../contexts/AppContext';

interface LocationState {
    from?: {
        pathname: string;
    };
};

const LoginPage: React.FC = () => {
    const { setDocumentTitle } = useApp();
    const { login, authenticated } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const state = location.state as LocationState;
    const from = state?.from?.pathname ?? '/';

    useEffect(() => {
        setDocumentTitle("Login");
    }, [setDocumentTitle]);

    useEffect(() => {
        const redirect = async () => {
            if (authenticated) {
                await navigate(from, { replace: true });
            }
        };
        void redirect();
    }, [authenticated, navigate, from]);

    const handleLogin = async () => {
        await login();
        await navigate(from, { replace: true });
    };

    return (
        <Container component="main" maxWidth="xs">
            <Box
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
                    <Typography component="h1" variant="h5" align="center">
                        Welcome to MiraVeja
                    </Typography>
                    <Box sx={{ mt: 3 }}>
                        <Button
                            fullWidth
                            variant='contained'
                            color='primary'
                            size='large'
                            onClick={() => { void handleLogin(); }}
                            sx={{ mt: 3, mb: 2 }}
                        >
                            LogIn
                        </Button>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default LoginPage;