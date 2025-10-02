import * as MuiMaterial from '@mui/material';

import ProfileDropdown from './ProfileDropdown';

export default function AppBar({
    title = 'MiraVeja',
    icon = 'remove_red_eye'
}) {
    const searchLabel = (
        <div style={{ display: 'flex', alignItems: 'center' }}>
            <MuiMaterial.Icon sx={{ fontSize: '1rem', verticalAlign: 'middle' }}>search</MuiMaterial.Icon>
            <span style={{ marginLeft: 8 }}>Search</span>
        </div>
    );

    return (
        <MuiMaterial.AppBar position="static">
            <MuiMaterial.Toolbar>

                <div style={{ display: 'flex', alignItems: 'center', marginRight: '16px', justifyContent: 'space-between', width: '100%' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <MuiMaterial.IconButton
                            size="large"
                            edge="start"
                            aria-label="menu"
                            sx={{ mr: 2 }}
                        >
                            <MuiMaterial.Icon>menu</MuiMaterial.Icon>
                        </MuiMaterial.IconButton>
                        <MuiMaterial.Typography variant="h4" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
                            <MuiMaterial.Link href="./" style={{ textDecoration: 'none', color: 'inherit' }}>
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
                        <ProfileDropdown />
                    </div>
                </div>

            </MuiMaterial.Toolbar>
        </MuiMaterial.AppBar>
    );
}
