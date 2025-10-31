import React, { useEffect } from 'react'
import { useAuth } from './hooks/useAuth'
import { setupInterceptors } from './api/http-client'
import { CircularProgress, Box, Container } from '@mui/material'

import AppRoutes from './routes'
import AppBar from "./components/AppBar";
import AppBarMobile from "./components/AppBarMobile";
import AppDrawer from './components/AppDrawer'
import MainArea from './components/MainArea'
import { useApp } from './hooks/useApp'

const App: React.FC = () => {
  const { loading, token, updateToken } = useAuth();
  const { isBigScreen } = useApp();

  useEffect(() => {
    if (token) {
      setupInterceptors(
        () => token,
        async () => updateToken(60),
      );
    }
  }, [token, updateToken]);

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  const drawerItems = [
    {
      label: "Home",
      icon: "home",
      to: "/",
    },
    {
      label: "Image Scroller",
      icon: "image",
      to: "/scroller",
    },
  ];

  return (
    <div className="App">
      <Box>
        <AppDrawer items={drawerItems} />
      </Box>
      {
        isBigScreen
          ? <AppBar title="MiraVeja" icon="remove_red_eye" />
          : <AppBarMobile />
      }
      <Container maxWidth="xl" disableGutters sx={{
      }}>
        <MainArea>
          <AppRoutes />
        </MainArea>
      </Container>
    </div >
  )
}

export default App;
