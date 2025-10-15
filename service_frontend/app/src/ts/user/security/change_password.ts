import { getUrlParams, log_sending_to_page } from "../../utils/other.js";
import { checkUpdateTokens, securedApiCall } from "../../utils/secured.js";

class ChangePassword {
    private async changedPasswordForm(user_id: number | string) {
        const form = document.getElementById("change_password-form") as HTMLFormElement;
        if (!form) {
            log_sending_to_page("Форма не найдена", "error")
            return;
        }

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const passwordInput = document.getElementById("password") as HTMLInputElement;
            const check_passwordInput = document.getElementById("check_password") as HTMLInputElement;

            const password = passwordInput.value.trim()
            const check_password = check_passwordInput.value.trim()

            if (password != check_password) {
                alert("Пароли не сходятся.");
                return;
            }

            const urlParams = getUrlParams(["verify", "cause"])
            const isVerified = urlParams.verify === "true" && urlParams.cause === "change_password"

            const requestBody: any = {
                password,
                user_id,
            }
            
            if (isVerified) {
                requestBody.confirm = isVerified
            }

            const response = await securedApiCall("/api/settings/change_password", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            })

            if (response && response.ok) {
                const data = await response.json();

                if (data.send_for_verification) {
                    window.location.href=`/confirm_code?cause=${encodeURIComponent("change_password")}`;
                    return;
                }

                if (!data.success) {
                    alert(data.message);
                    return;
                } else {
                    alert("Password changed successfully!");
                    window.location.href='/settings';
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
            console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
            return;
        }

        this.changedPasswordForm(user_id);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const change = new ChangePassword();
    await change.init();
});