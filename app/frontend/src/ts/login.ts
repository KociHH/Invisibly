import {updateAccess} from "./utils/secured";
import {log_sending_to_page} from "./utils/other";

(() => {
    // если есть уже с токеном
    document.addEventListener('DOMContentLoaded', async () => {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
            try {
                const newAccess = await updateAccess(refreshToken);
                if (newAccess.accessToken) {
                    window.location.href = '/profile';
                }
            } catch (error) {
                log_sending_to_page(`Ошибка при проверке refresh токена при загрузке страницы:\n ${error}`, "error");
            }
        }
    });

const form = document.getElementById('login-form') as HTMLFormElement;

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const login = (document.getElementById('login') as HTMLInputElement).value;
    const password = (document.getElementById('password') as HTMLInputElement).value;
    const email = (document.getElementById('email') as HTMLInputElement).value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            login, 
            password, 
            email
        }),
    });
    const data = await response.json();
    if (data.success) {
        localStorage.setItem('accessToken', data.access_token);
        localStorage.setItem('refreshToken', data.refresh_token);
        
        window.location.href = `/home`;
    } else {
        alert(data.msg);
    }
});
})();