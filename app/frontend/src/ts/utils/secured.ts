const REFRESH_TOKEN_KEY = 'refreshToken';
const ACCESS_TOKEN_KEY = 'accessToken';
const SERVER_ERR = 'Server error'

async function updateTokens(currentRefreshToken: string): Promise<{accessToken: string; refreshToken: string}> {
    try {
        const response = await fetch('/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({refresh_token: currentRefreshToken}),
        });

        if (!response.ok) {
            const errorData = await response.json();
            if (response.status === 401 && typeof errorData.detail === 'string' && errorData.detail.includes("Refresh token")) {
                console.error("Refresh token истек. Перенаправление на страницу входа.");
                clearTokensAndRedirectLogin();
            } else {
                console.error("Ошибка при обновлении токенов:", errorData.detail || response.statusText);
                throw new Error(errorData.detail || `${SERVER_ERR}`);
            }
        }

        const data = await response.json();
        return {
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
        };
    } catch (error) {
        console.error("Ошибка в функции refreshTokens:\n", error);
        throw new Error(SERVER_ERR);
    }
}

function clearTokensAndRedirectLogin() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    window.location.href = '/login';
}

function getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
}

async function updateAccess(currentRefreshToken: string): Promise<{accessToken: string}> {
    const response = await fetch("/access", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({refresh_token: currentRefreshToken})
    })

    if (response.status === 500 || !response.ok) {
        throw new Error(SERVER_ERR);
    }

    const data = await response.json();
    return {
        accessToken: data.access_token
    }
}

async function securedApiCall(url_api: string, options: RequestInit = {}) {
    let accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
    let refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

    if (!refreshToken) {
        clearTokensAndRedirectLogin();
        return;
    }

    let response = await fetch(url_api, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`,
        },
    });

    if (response.status === 401) {
        try {
            const newAccess = await updateAccess(refreshToken);
            localStorage.setItem(ACCESS_TOKEN_KEY, newAccess.accessToken);

            response = await fetch(url_api, {
                ...options,
                headers: {
                    ...options.headers,
                    'Authorization': `Bearer ${newAccess.accessToken}`,
                },
            });
        } catch (accessError) {
            console.error("Не удалось обновить токен:", accessError);
            clearTokensAndRedirectLogin();
            return;
        }
    }

    if (!response.ok) {
        console.error("API вызов завершился неудачей после попытки обновления токена.", response);
        clearTokensAndRedirectLogin();
        return;
    }

    return response;
}

async function checkUpdateTokens() {
    try {
        const response = await securedApiCall("/check_update_tokens",{
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (response && response.ok) {
            const data = await response.json();
            console.log("Токены успешно проверены");
            return data;
        }
    } catch (error) {
        console.error('Ошибка проверки токенов:', error);
        return;
    }
}

export {
    securedApiCall, 
    updateTokens, 
    clearTokensAndRedirectLogin, 
    updateAccess, 
    getAccessToken, 
    checkUpdateTokens
};   