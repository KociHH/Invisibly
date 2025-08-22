import { log_sending_to_page, getUrlParams } from "../../utils/other";
import { checkUpdateTokens, securedApiCall } from "../../utils/secured"

class ChangedEmail {
    private async changedEmailForm(user_id: number | string) {
        const form = document.getElementById("change_email-form") as HTMLFormElement;
        
        if (!form) {
            log_sending_to_page("Форма не найдена", "error");
            return;
        }

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
        
            const emailInput = document.getElementById("email") as HTMLInputElement;
            const email = emailInput.value.trim();
    
            if (!email) {
                log_sending_to_page("Введите email", "error");
                return;
            }

            const urlParams = getUrlParams(['verify', 'cause']);
            const isVerified = urlParams.verify === 'true' && urlParams.cause === 'change_email';

            const requestBody: any = {
                email,
                user_id,
            };

            if (isVerified) {
                requestBody.confirm = true;
            }

            const response = await securedApiCall("/change_email", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
    
            if (response && response.ok) {
                const data = await response.json();
    
                if (data.send_for_verification) {
                    window.location.href = `/confirm_code?cause=${encodeURIComponent("change_email")}`;
                    return;
                }
    
                if (data.success) {
                    alert("Email successfully changed!");
                    window.location.href = "/settings";
                    return;
                } else {
                    alert(data.message || "Ошибка при смене email");
                    return;
                }
    
            } else {
                log_sending_to_page("Не получены данные с сервера, либо запрос завершился неудачей.", "error");
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
            log_sending_to_page(`Не вернулось значение функции checkUpdateTokens: ${data}`, "error");
            return;
        }
    
        await this.changedEmailForm(user_id);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const change = new ChangedEmail();
    await change.init();
});