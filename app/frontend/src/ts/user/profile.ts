import { log_sending_to_page } from "../utils/other";
import { checkUpdateTokens } from "../utils/secured";

async function loadUserBio() {
    const bioContentElement = document.querySelector('#user_bio');
    
    if (bioContentElement) {
        const bio = bioContentElement.getElementsByTagName('h4')[0];

        if (bio && bio.textContent !== null && bio.textContent.trim() !== "") {
            bioContentElement.innerHTML = `
            <p>Био:</p>
            <h4>${bio.textContent}</h4>
            `;
        } else {
            bioContentElement.innerHTML = `<a href="/edit_profile">Добавить био</a>`;
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const data = await checkUpdateTokens();

    if (!data || !data.success) {
        log_sending_to_page(`Не вернулось значение функции checkUpdateTokens: ${data}`, "error");
        return;
    }

    await loadUserBio();
});