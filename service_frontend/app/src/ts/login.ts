import {log_sending_to_page} from "./utils/other.js";
import {updateAccess, checkUpdateTokens, clearTokensAndRedirectLogin, ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY} from "./utils/secured.js";

(async () => {
    
    if (localStorage.getItem(REFRESH_TOKEN_KEY)) {
        const data = await checkUpdateTokens();
        
        if (data) {
            window.location.href = "/profile";
            return;

        } else {
            console.error("Вернулась функция с ошибкой checkUpdateTokens");
            return;
        }
    }


    const form = document.getElementById('login-form') as HTMLFormElement;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const login = (document.getElementById('login') as HTMLInputElement).value;
        const password = (document.getElementById('password') as HTMLInputElement).value;
        const email = (document.getElementById('email') as HTMLInputElement).value;

        const response = await fetch('/api/free/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                login,
                password,
                email
            }),
        });
        const data = await response.json();
        if (response && response.ok) {
            if (data.success) {
                localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
                localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
                window.location.href = `/profile`;
            } else {
                alert(data.message);
            }
        } else {
            log_sending_to_page('Не удалось войти', "error");
            return;
        }
    });
})();