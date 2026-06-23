import React from 'react';
import { NavLink } from 'react-router-dom';
import { Box, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Typography, AppBar, Drawer } from '@mui/material';
import { Home, TravelExplore, BarChart, Layers as HeatmapIcon } from "@mui/icons-material";

const drawerWidth = 240;

const navItems = [
    { text: 'Home', icon: <Home />, path: '/' },
    { text: 'Predict', icon: <TravelExplore />, path: '/predict' },
    { text: 'Analytics', icon: <BarChart />, path: '/analytics' },
    { text: 'Heatmap', icon: <HeatmapIcon />, path: '/heatmap' },
];

const Layout = ({ children }) => {
    return (
        <Box sx={{ display: 'flex' }}>
            <AppBar
                position="fixed"
                sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: '#1a1d2e' }}
            >
                <Toolbar>
                    <Typography variant="h6" noWrap component="div">
                        Incident Response Planner
                    </Typography>
                </Toolbar>
            </AppBar>
            <Drawer
                variant="permanent"
                sx={{
                    width: drawerWidth,
                    flexShrink: 0,
                    [`& .MuiDrawer-paper`]: {
                        width: drawerWidth,
                        boxSizing: 'border-box',
                        backgroundColor: '#1a1d2e',
                        color: '#e0e0e0'
                    },
                }}
            >
                <Toolbar />
                <Box sx={{ overflow: 'auto' }}>
                    <List>
                        {navItems.map((item) => (
                            <ListItem key={item.text} disablePadding>
                                <ListItemButton component={NavLink} to={item.path} sx={{
                                    '&.active': { backgroundColor: 'rgba(38, 124, 217, 0.3)' },
                                    '& .MuiListItemIcon-root': { color: '#e0e0e0' }
                                }}>
                                    <ListItemIcon>{item.icon}</ListItemIcon>
                                    <ListItemText primary={item.text} />
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </List>
                </Box>
            </Drawer>
            <Box component="main" sx={{ flexGrow: 1, p: 3, backgroundColor: '#0f101a', minHeight: '100vh' }}>
                <Toolbar />
                {children}
            </Box>
        </Box>
    );
};

export default Layout;