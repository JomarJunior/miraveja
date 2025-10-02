import React, { useEffect } from 'react'
import { useAuth } from './hooks/useAuth'
import { setupInterceptors } from './api/http-client'
import { CircularProgress, Box } from '@mui/material'

import AppRoutes from './routes'
import AppBar from "./components/AppBar";
import AppDrawer from './components/AppDrawer'
import MainArea from './components/MainArea'

const App: React.FC = () => {
  const { loading, token, updateToken } = useAuth();

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
      label: "About",
      icon: "info",
      to: "/about",
    },
    {
      label: "Parent Test",
      icon: "folder",
      children: [
        {
          label: "Child 1",
          icon: "insert_drive_file",
          to: "/parent/child1",
        },
        {
          label: "Child 2",
          icon: "insert_drive_file",
          to: "/parent/child2",
        },
      ],
    }
  ];

  return (
    <div className="App">
      <Box>
        <AppDrawer items={drawerItems} />
      </Box>
      <Box>
        <AppBar
          title="MiraVeja"
        />
        <MainArea>
          <Box>
            <AppRoutes />
          </Box>
        </MainArea>
      </Box>
    </div>
  )
}

export default App;
