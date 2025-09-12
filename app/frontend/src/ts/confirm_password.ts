import { getUrlParams, log_sending_to_page } from "./utils/other.js";
import { ACCESS_TOKEN_KEY, checkUpdateTokens, securedApiCall } from "./utils/secured.js";

class ConfirmPassword {
    private async confirmPasswordForm(token: string, user_id: number | string) {
        const form = document.getElementById("confirm_password-form") as HTMLFormElement;
        if (!form) {
            log_sending_to_page("Форма не найдена", "error");
            return;
        }
        
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const passwordInput = document.getElementById("password") as HTMLInputElement;
            const password = passwordInput.value;

            const urlParams = getUrlParams(["cause"]);
            const cause = urlParams.get("cause");

            const response = await securedApiCall('/confirm_password', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    password,
                    token,
                })
            });
            if (response && response.ok) {
                const data = await response.json();
                if (data.success) {
                    log_sending_to_page(`Пароль успешно подтвержден пользователем ${user_id}`, "log", `/${cause}?verify=true`)
                    return;
                } else {
                    alert(data.message);
                    return;
                }
            } else {
                log_sending_to_page("Не получены данные с сервера, либо запрос завершился неудачей.", "error");
                return;
            }
        });
    }

    async init() {
        const data = await checkUpdateTokens()

        if (data && data.succses) {
            const token = localStorage.getItem(ACCESS_TOKEN_KEY)
            const user_id = data.get("user_id")
            if (!token) {
                log_sending_to_page("Токен истек, он не был обновлен через функцию checkUpdateTokens", "error")
                return;
            }
            
            await this.confirmPasswordForm(token, user_id)
        }
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const confirm = new ConfirmPassword();
    await confirm.init();
})