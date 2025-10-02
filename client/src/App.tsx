import React, { useEffect } from 'react'
import { useAuth } from './hooks/useAuth'
import { setupInterceptors } from './api/http-client'
import { CircularProgress, Box } from '@mui/material'

import AppRoutes from './routes'
import { AppProvider } from './contexts/AppContext'
import AppBar from './components/AppBar'

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

  return (<div className="App">
    <AppProvider>
      <AppBar
        title="MiraVeja"
      />
      <AppRoutes />
    </AppProvider>
  </div>
  )
}

export default App;
