import React from 'react'
import { useApp } from '../hooks/useApp'
import { styled } from '@mui/material/styles';

const drawerWidth = import.meta.env.VITE_DRAWER_WIDTH as string ?? '300px';

interface MainAreaProps {
    children: React.ReactNode;
}

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })<{
    open?: boolean;
}>(({ theme }) => ({
    flexGrow: 1,
    transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: `${drawerWidth}`,
    width: `calc(100% - ${drawerWidth})`,
    variants: [
        {
            props: ({ open }) => !open,
            style: {
                transition: theme.transitions.create(['margin', 'width'], {
                    easing: theme.transitions.easing.sharp,
                    duration: theme.transitions.duration.leavingScreen,
                }),
                marginLeft: 0,
                width: '100%',
            },
        },
    ],
}));

const MainArea: React.FC<MainAreaProps> = ({
    children
}) => {
    const { isDrawerOpen } = useApp();

    return (
        <Main open={isDrawerOpen}>
            {children}
        </Main>
    );
};

export default MainArea;