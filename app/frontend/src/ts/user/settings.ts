import { log_sending_to_page } from "../utils/other";
import {checkUpdateTokens, clearTokensAndRedirectLogin, securedApiCall} from "../utils/secured";

async function SettingsExit(user_id: number | string) {
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