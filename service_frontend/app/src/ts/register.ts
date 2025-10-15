import { log_sending_to_page } from "./utils/other.js";
import { ACCESS_TOKEN_KEY, clearTokensAndRedirectLogin, REFRESH_TOKEN_KEY} from "./utils/secured.js";


(() => {
const form = document.getElementById('register-form') as HTMLFormElement;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = (document.getElementById('name') as HTMLInputElement).value;
    const login = (document.getElementById('login') as HTMLInputElement).value;
    const password = (document.getElementById('password') as HTMLInputElement).value;
    const email = (document.getElementById('email') as HTMLInputElement).value;

    const response = await fetch('/api/free/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name, 
            login, 
            password, 
            email, 
            "is_registered": true
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
        log_sending_to_page('Не удалось зарегистрироваться', "error");
        return;
    }
});
})();