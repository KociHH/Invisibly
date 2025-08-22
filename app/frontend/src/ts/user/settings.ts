import {securedApiCall} from "../utils/secured";

async function EditUserProfile() {
    try {
        const response = await securedApiCall('/edit_profile');
        if (response && response.ok) {
            return
        } else {
            console.error('Не удалось загрузить данные профиля.');
            return;
        }
    } catch (error) {
        console.error('Ошибка при запросе данных профиля:', error);
    }
    window.location.href = "about:blank";
}

document.addEventListener('DOMContentLoaded', EditUserProfile);