import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';

const httpClient = axios.create({
    baseURL: (import.meta.env.VITE_API_BASE_URL as string) ?? 'http://localhost:4000/api',
});

const setupInterceptors = (getToken: () => string | null, refreshToken: () => Promise<boolean>) => {
    httpClient.interceptors.request.use(
        async (config) => {
            let token = getToken();

            if (!token) {
                const refreshed = await refreshToken();
                if (refreshed) {
                    token = getToken();
                }
            }

            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }

            return config;
        },
        (error) => Promise.reject(new Error(String(error)))
    );

    httpClient.interceptors.response.use(
        (response) => response,
        async (error: AxiosError) => {
            const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

            if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
                originalRequest._retry = true;

                try {
                    const refreshed = await refreshToken();
                    if (refreshed) {
                        originalRequest.headers.Authorization = `Bearer ${getToken()}`;
                        return httpClient(originalRequest);
                    }
                } catch (refreshError) {
                    return Promise.reject(new Error(String(refreshError)));
                }
            }

            return Promise.reject(error);
        }
    );
};

export {
    httpClient,
    setupInterceptors,
};
