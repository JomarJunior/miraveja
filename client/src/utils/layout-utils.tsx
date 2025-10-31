const getAvailableSpace = () => {
    const appBarHeight = import.meta.env.VITE_APPBAR_HEIGHT as string ?? '64px';
    const height = `calc(100vh - ${appBarHeight})`;
    const width = '100vw';
    return { height, width };
};

const getAvailableSpaceNumber = () => {
    const appBarHeight = import.meta.env.VITE_APPBAR_HEIGHT as string ?? '64px';
    const appBarHeightNumber = parseInt(appBarHeight.replace('px', ''), 10);
    return {
        height: window.innerHeight - appBarHeightNumber,
        width: window.innerWidth,
    };
};

export { getAvailableSpace, getAvailableSpaceNumber };