import * as MuiMaterial from '@mui/material';

import { useApp } from '../hooks/useApp';
import { useNavigate } from 'react-router-dom';
import ProfileDropdown from './ProfileDropdown';
import { useUser } from '../hooks/useUser';

const appBarHeight = import.meta.env.VITE_APPBAR_HEIGHT as string ?? '64px';

export default function AppBar({
    title = 'MiraVeja',
    icon = 'remove_red_eye',
}) {
    const { toggleDrawer } = useApp();
    const { id } = useUser();
    const navigate = useNavigate();

    const handleDrawerToggle = () => {
        toggleDrawer();
    };

    const handleGoHome = () => {
        void navigate('/');
    }

    const isAuthenticated = Boolean(id);

    const searchLabel = (
        <div style={{ display: 'flex', alignItems: 'center' }}>
            <MuiMaterial.Icon sx={{ fontSize: '1rem', verticalAlign: 'middle' }}>search</MuiMaterial.Icon>
            <span style={{ marginLeft: 8 }}>Search</span>
        </div>
    );

    return (
        <MuiMaterial.AppBar
            sx={{
                height: appBarHeight,
                justifyContent: 'center',
                position: 'fixed',
                zIndex: (theme) => theme.zIndex.drawer + 1,
            }}
        >
            <MuiMaterial.Toolbar>
                <div style={{ display: 'flex', alignItems: 'center', marginRight: '16px', justifyContent: 'space-between', width: '100%' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <MuiMaterial.IconButton
                            size="large"
                            edge="start"
                            aria-label="menu"
                            sx={{ mr: 2 }}
                            onClick={handleDrawerToggle}
                        >
                            <MuiMaterial.Icon>menu</MuiMaterial.Icon>
                        </MuiMaterial.IconButton>
                        <MuiMaterial.Typography variant="h4" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
                            <MuiMaterial.Link onClick={handleGoHome} style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>
                                <MuiMaterial.Icon sx={{ mr: 2, fontSize: 'inherit', verticalAlign: 'middle' }}>{icon}</MuiMaterial.Icon>
                                {title}
                            </MuiMaterial.Link>
                        </MuiMaterial.Typography>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <MuiMaterial.Autocomplete
                            sx={{ width: 300, display: { xs: 'none', sm: 'block' }, mr: 2 }}
                            options={[]}
                            renderInput={(params) => <MuiMaterial.TextField {...params} label={searchLabel} variant="outlined" />}
                            popupIcon={null}
                        />
                    </div>

                    <div>
                        {isAuthenticated &&
                            <MuiMaterial.Button
                                sx={{
                                    borderRadius: '20px',
                                    textTransform: 'none',
                                    mr: 2,
                                    paddingLeft: 2,
                                    paddingRight: 2,
                                }}
                                size="large"
                                color="inherit"
                                variant='text'
                                onClick={() => void navigate('/post')}
                            >
                                <MuiMaterial.Icon
                                    sx={{ mr: 1 }}
                                >
                                    add
                                </MuiMaterial.Icon>
                                <MuiMaterial.Typography variant="body2">Post Image</MuiMaterial.Typography>
                            </MuiMaterial.Button>
                        }
                        <ProfileDropdown />
                    </div>
                </div>

            </MuiMaterial.Toolbar>
        </MuiMaterial.AppBar>
    );
}
