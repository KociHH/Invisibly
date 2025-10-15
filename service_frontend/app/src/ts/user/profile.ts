import { log_sending_to_page } from "../utils/other.js";
import { checkUpdateTokens, securedApiCall } from "../utils/secured.js";

async function loadUserProfile() {
    const response = await securedApiCall('/api/profile/profile/data');
    if (!response || !response.ok) {
        log_sending_to_page('Не удалось загрузить данные профиля', "error");
        return;
    }

    const userData = await response.json();

    const fullNameElement = document.querySelector('#user_full_name h4') as HTMLElement;
    const loginElement = document.querySelector('#user_login h4') as HTMLElement;
    const bioContentElement = document.querySelector('#user_bio') as HTMLElement;

    if (fullNameElement) {
        fullNameElement.textContent = `${userData.full_name}`.trim();
    }
    if (loginElement) {
        loginElement.textContent = userData.login;
    }
    if (bioContentElement) {
        if (userData.bio && userData.bio.trim() !== "") {
            bioContentElement.innerHTML = `
            <p>Био</p>
            <h4>${userData.bio}</h4>
            `;
        } else {
            bioContentElement.innerHTML = `<a href="/edit_profile">Добавить био</a>`;
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const data = await checkUpdateTokens();

    if (!data || !data.success) {
        console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
        return;
    }

    await loadUserProfile();
});