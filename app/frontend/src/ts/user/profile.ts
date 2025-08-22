import { log_sending_to_page } from "../utils/other";
import {securedApiCall} from "../utils/secured";

async function loadUserProfile() {
    try {
        const response = await securedApiCall('/profile', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            }

        });
        if (response && response.ok) {
            const data = await response.json();
            console.log('Данные профиля:\n', data);

            const bioContentElement = document.querySelector('.bio-block');
            if (bioContentElement) {
                const bio = data.user_info.bio ? String(data.user_info.bio).trim() : '';
                if (bio) {
                    bioContentElement.innerHTML = `<h3>${bio}</h3><h4>О себе</h4>`;
                } else {
                    bioContentElement.innerHTML = `<a href="/edit_profile">Добавить био</a>`;
                }
            }

        } else {
            log_sending_to_page('Не удалось загрузить данные профиля.', 'error');
        }
    } catch (error) {
        log_sending_to_page(`Ошибка при запросе данных профиля: ${error}`, 'error');
    }
}

document.addEventListener('DOMContentLoaded', loadUserProfile);