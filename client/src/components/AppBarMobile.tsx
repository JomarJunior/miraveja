import * as MuiMaterial from '@mui/material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
// import { useApp } from '../hooks/useApp';

const appBarHeight = import.meta.env.VITE_APPBAR_HEIGHT as string ?? '64px';

export default function AppBarMobile() {
    const navigate = useNavigate();
    // const { isDrawerOpen, toggleDrawer } = useApp(); // optional if you want a menu icon
    const [value, setValue] = useState(0);

    const items = [
        { label: 'Home', icon: 'home', to: '/scroller' },
        { label: 'Search', icon: 'search', to: '/search' },
        { label: 'Post', icon: 'add_box', to: '/post' },
        { label: 'Notifications', icon: 'notifications', to: '/notifications' },
        { label: 'Profile', icon: 'person', to: '/profile' },
    ];

    const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
        void navigate(items[newValue].to);
    };

    return (
        <MuiMaterial.Paper
            sx={{
                position: 'fixed',
                bottom: 0,
                left: 0,
                right: 0,
                height: appBarHeight,
                elevation: 3,
                zIndex: (theme) => theme.zIndex.drawer + 2,
                borderTopLeftRadius: 16,
                borderTopRightRadius: 16,
                boxShadow: '0 -2px 10px rgba(0,0,0,0.1)',
                backgroundColor: 'background.paper',
            }}
            elevation={3}
        >
            <MuiMaterial.BottomNavigation
                showLabels={false} // icon-only
                value={value}
                onChange={handleChange}
                sx={{
                    height: '100%',
                    '.Mui-selected': {
                        color: 'primary.main',
                    },
                }}
            >
                {items.map((item) => (
                    <MuiMaterial.BottomNavigationAction
                        key={item.label}
                        label={item.label}
                        icon={<MuiMaterial.Icon>{item.icon}</MuiMaterial.Icon>}
                    />
                ))}
            </MuiMaterial.BottomNavigation>
        </MuiMaterial.Paper>
    );
}
