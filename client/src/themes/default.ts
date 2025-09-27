import { createTheme } from "@mui/material";

const defaultTheme = createTheme({
    palette: {
        mode: "dark",
        background: {
            default: "#1b1b1e",
            paper: "#373F51",
        },
        primary: {
            main: "#58a4b0",
        },
        secondary: {
            main: "#a9bcd0",
        },
        text: {
            primary: "#D8DBE2",
        },
    },
    typography: {
        fontFamily: "'Roboto', 'Helvetica', 'Arial', sans-serif",
    },
});

export default defaultTheme;
