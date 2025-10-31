import React from 'react'
import { useApp } from '../hooks/useApp'
import { styled } from '@mui/material/styles';
import { getAvailableSpace } from '../utils/layout-utils';

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
    minHeight: getAvailableSpace().height,
    width: `calc(100% - ${drawerWidth})`,
    padding: 0,
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
    const { isDrawerOpen, isBigScreen } = useApp();

    const marginTop = () => {
        if (isBigScreen) {
            const appBarHeight = import.meta.env.VITE_APPBAR_HEIGHT as string ?? '64px';
            return appBarHeight;
        }
        return 0;
    };

    const marginBottom = () => {
        if (isBigScreen) {
            return 0;
        }

        const appBarHeight = import.meta.env.VITE_APPBAR_HEIGHT as string ?? '64px';
        return appBarHeight;
    };

    return (
        <Main open={isDrawerOpen} sx={{
            marginTop: marginTop(),
            paddingBottom: marginBottom(),
        }}>
            {children}
        </Main>
    );
};

export default MainArea;