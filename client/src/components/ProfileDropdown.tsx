import React, { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { useUser } from "../hooks/useUser";
import * as MuiMaterial from "@mui/material";

interface ProfileDropdownItem {
    label: string;
    icon: string;
    onClick: () => void;
}

interface ProfileDropdownProps {
    items?: ProfileDropdownItem[];
    minMenuWidth?: number | string;
    displayAvatar?: boolean;
    displayUsername?: boolean;
    triggerOnHover?: boolean;
}

const ProfileDropdown: React.FC<ProfileDropdownProps> = ({
    items,
    minMenuWidth = '25vw',
    displayAvatar = true,
    displayUsername = true,
    triggerOnHover = true,
}) => {
    const { authenticated, login, logout } = useAuth();
    const { username, firstName, lastName } = useUser();
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);

    const handleDisplay = () => {
        const profileButton = document.getElementById('profile-button');
        setAnchorEl(profileButton);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleLogin = async () => {
        await login();
        handleClose();
    }

    const handleLogout = async () => {
        await logout();
        handleClose();
    }

    items = items ?? [
        { label: 'Logout', icon: 'logout', onClick: () => void handleLogout() }
    ];

    if (!authenticated) {
        return (
            <MuiMaterial.Button
                color="inherit"
                onClick={() => void handleLogin()}
            >
                <MuiMaterial.Icon sx={{ mr: 1, fontSize: '1.2rem', verticalAlign: 'middle' }}>login</MuiMaterial.Icon>
                Login
            </MuiMaterial.Button>
        );
    }

    const avatar = displayAvatar && (
        <MuiMaterial.Avatar
            sx={{ width: 32, height: 32, bgcolor: 'secondary.main', fontSize: '1.2rem' }}
        >
            <MuiMaterial.Icon>
                account_circle
            </MuiMaterial.Icon>
        </MuiMaterial.Avatar>
    );

    const displayName = displayUsername ? username : `${firstName} ${lastName}`;

    return (
        <>
            <MuiMaterial.Button
                id="profile-button"
                color="inherit"
                variant="text"
                startIcon={avatar}
                aria-controls={open ? 'profile-menu' : undefined}
                aria-haspopup="true"
                aria-expanded={open ? 'true' : undefined}
                onClick={handleDisplay}
                onMouseEnter={triggerOnHover ? handleDisplay : undefined}
                onMouseLeave={triggerOnHover ? handleClose : undefined}
                sx={{ zIndex: 99 }}
            >
                {displayName}
            </MuiMaterial.Button>
            <MuiMaterial.Menu
                id="profile-menu"
                anchorEl={anchorEl}
                open={open}
                slotProps={{
                    root: {
                        sx: { zIndex: 98 },
                    },
                    list: {
                        'aria-labelledby': 'profile-button',
                        onMouseLeave: triggerOnHover ? handleClose : undefined,
                        onMouseEnter: triggerOnHover ? handleDisplay : undefined,
                    },
                    paper: {
                        sx: {
                            overflow: 'visible',
                            filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                            minWidth: minMenuWidth,
                            mt: 1.5,
                        },
                    },
                }}
                onClose={handleClose}
            >
                <MuiMaterial.Typography
                    variant="h4"
                    sx={{ px: 2, pt: 1 }}
                    color="text.primary"
                >
                    {firstName} {lastName}
                </MuiMaterial.Typography>
                <MuiMaterial.Typography
                    variant="overline"
                    sx={{ px: 2, pb: 1 }}
                >
                    @{username}
                </MuiMaterial.Typography>
                <MuiMaterial.Divider
                    sx={{ my: 1 }}
                />

                {items.map((item) => (
                    <MuiMaterial.MenuItem
                        key={item.label}
                        onClick={() => {
                            item.onClick();
                            handleClose();
                        }}
                    >
                        <MuiMaterial.ListItemIcon>
                            <MuiMaterial.Icon fontSize="small">{item.icon}</MuiMaterial.Icon>
                        </MuiMaterial.ListItemIcon>
                        <MuiMaterial.ListItemText>{item.label}</MuiMaterial.ListItemText>
                    </MuiMaterial.MenuItem>
                ))}
            </MuiMaterial.Menu>
        </>
    );
};

export default ProfileDropdown;