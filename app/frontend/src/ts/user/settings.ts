import { log_sending_to_page } from "../utils/other.js";
import { checkUpdateTokens, securedApiCall, clearTokensAndRedirectLogin } from "../utils/secured.js";

async function SettingsExit(user_id: number | string) {
    const response = await securedApiCall("/settings/data")
    if (!response || !response.ok) {
        log_sending_to_page('Не удалось загрузить данные для настроек', "error");
        return;
    }

    const data_elem = await response.json()

    const name = document.querySelector("#user_name h4") as HTMLElement;
    const surname = document.querySelector("#user_surname h4") as HTMLElement;
    const login = document.querySelector("#user_login h4") as HTMLElement;
    const bio_content = document.querySelector("#bio_content h4") as HTMLElement;
    
    name.textContent = data_elem.name
    surname.textContent = data_elem.surname
    login.textContent = data_elem.login
    bio_content.textContent = data_elem.bio

    const button = document.getElementById("submit_exit") as HTMLButtonElement;
    if (!button) {
        log_sending_to_page("Не нашлась кнопка submit_exit", "error");
        return;
    }

    button.addEventListener('click', async () => {
        const response = await securedApiCall('/logout', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id
            })
        });
        if (response && response.ok) {
            const data = await response.json();
            if (data.success) {
                clearTokensAndRedirectLogin();
            }

        } else {
            log_sending_to_page('Не удалось выйти из профиля', "error");
            return;
        }
    })
}

document.addEventListener('DOMContentLoaded', async () => {
    const data = await checkUpdateTokens();

    let user_id;
    if (data && data.success) {
        user_id = data.user_id;
    } else {
        log_sending_to_page(`Не вернулось значение функции checkUpdateTokens: ${data}`, "error");
        return;
    }

    await SettingsExit(user_id);
});