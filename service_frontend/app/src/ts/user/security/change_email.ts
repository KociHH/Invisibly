import { log_sending_to_page, getUrlParams, clearItemsStorage, TIME_EXP_REPEATED, TIME_EXP_TOKEN } from "../../utils/other.js";
import { checkUpdateTokens, securedApiCall } from "../../utils/secured.js";

class ChangedEmail {
    private async getElemEmail() {
        const response = await securedApiCall("/api/settings/change_email/data")
        if (!response || !response.ok) {
            log_sending_to_page('Не удалось загрузить данные для настроек', "error");
            return;
        }

        const data_elem = await response.json();

        const email = document.querySelector("#current_email") as HTMLElement;
    
        email.textContent = data_elem.email
    }

    private async changedEmailForm(user_id: number | string) {
        const form = document.getElementById("change_email-form") as HTMLFormElement;
        
        if (!form) {
            log_sending_to_page("Форма не найдена", "error");
            return;
        }

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
        
            clearItemsStorage([TIME_EXP_REPEATED, TIME_EXP_TOKEN]);

            const buttonSubmit = document.querySelector(".change_email") as HTMLButtonElement;
            buttonSubmit.disabled = true;
            buttonSubmit.textContent = "Отправка, подождите...";
            
            const emailInput = document.getElementById("email") as HTMLInputElement;
            const email = emailInput.value.trim();

            const requestBody: any = {
                user_id,
                email,
            };
    
            const response = await securedApiCall("/api/settings/change_email", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
    
            if (response && response.ok) {
                const data = await response.json();

                if (data.success) {
                    window.location.href = `/confirm_code?cause=${encodeURIComponent("change_email")}`;
                    return;     

                } else {
                    buttonSubmit.disabled = false;
                    buttonSubmit.textContent = "Сменить почту";
                    alert(data.message);
                }
    
            } else {
                console.error("Не получены данные с сервера, либо запрос завершился неудачей.");
                return;
            }
        });
    }
    
    async init() {
        const data = await checkUpdateTokens();
        
        let user_id;
        if (data && data.success) {
            user_id = data.user_id;
        } else {
            console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
            return;
        }
    
        await this.getElemEmail();

        await this.changedEmailForm(user_id);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const change = new ChangedEmail();
    await change.init();
});