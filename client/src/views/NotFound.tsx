import React from "react";
import * as MuiMaterial from "@mui/material";
import { useApp } from "../contexts/AppContext";

export default function NotFound() {
  const { setDocumentTitle } = useApp();

  React.useEffect(() => {
    setDocumentTitle("404");
  }, [setDocumentTitle]);

  return (
    <MuiMaterial.Container>
      <MuiMaterial.Card sx={{ mt: 5, p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <MuiMaterial.CardContent sx={{ textAlign: 'center' }}>
          <MuiMaterial.Typography variant="h1" sx={{ fontSize: 256, fontWeight: 'bold' }}>
            404
          </MuiMaterial.Typography>
          <MuiMaterial.Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <MuiMaterial.Icon sx={{ fontSize: 32, verticalAlign: 'middle', mr: 3, mt: 0.5 }}>error_outline</MuiMaterial.Icon>
            <MuiMaterial.Typography variant="h4" gutterBottom>
              Oops! Page not found.
            </MuiMaterial.Typography>
          </MuiMaterial.Box>
          <MuiMaterial.Divider sx={{ my: 2 }} />
          <MuiMaterial.Typography>
            The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
          </MuiMaterial.Typography>
          <MuiMaterial.Button variant="contained" color="primary" href="/" sx={{ mt: 3 }}>
            Go to Home
          </MuiMaterial.Button>
        </MuiMaterial.CardContent>
      </MuiMaterial.Card>
    </MuiMaterial.Container>
  );
}
