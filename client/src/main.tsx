import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { CssBaseline, ThemeProvider } from '@mui/material'
import App from './App.tsx'
import defaultTheme from './themes/default.ts'
import { AuthProvider } from './contexts/AuthContext.tsx'
import { UserProvider } from './contexts/UserContext.tsx'
import { AppProvider } from './contexts/AppContext.tsx'
import { setupInterceptors } from './api/http-client.ts'

const keycloakConfig = {
  url: import.meta.env.VITE_KEYCLOAK_URL as string,
  realm: import.meta.env.VITE_KEYCLOAK_REALM as string,
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID as string,
}

const basename = (import.meta.env.VITE_FRONTEND_BASE_PATH as string) ?? "";

const initOptions = {
  onLoad: 'check-sso',
  silentCheckSsoRedirectUri: `${window.location.origin}${basename}/silent-check-sso.html`,
} as const;

const onTokensCallback = ({ token }: { token: string | null }) => {
  localStorage.setItem('token', token ?? '');

  setupInterceptors(
    () => localStorage.getItem('token'),
    async () => Promise.resolve(false), // Implement token refresh logic if needed
  );
}

createRoot(document.getElementById('root')!).render(
  <BrowserRouter basename={basename}>
    <AuthProvider
      keycloakConfig={keycloakConfig}
      initOptions={initOptions}
      onTokens={onTokensCallback}
    >
      <UserProvider>
        <StrictMode>
          <AppProvider>
            <ThemeProvider theme={defaultTheme}>
              <CssBaseline />
              <App />
            </ThemeProvider>
          </AppProvider>
        </StrictMode>
      </UserProvider>
    </AuthProvider>
  </BrowserRouter>
);
