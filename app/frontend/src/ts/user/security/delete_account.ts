import { getUrlParams, log_sending_to_page } from "../../utils/other.js";
import { checkUpdateTokens, securedApiCall } from "../../utils/secured.js";

class DeleteAccount {
    private button: HTMLButtonElement | undefined = this.buttonObj();
    private isVerifyOnce = false;
    private isVeifySecond = false;
    private Delete = false

    private buttonObj(): HTMLButtonElement | undefined {
        const button = document.getElementById("further") as HTMLButtonElement;
        if (button === null || button === undefined) {
            log_sending_to_page("Не найдена кнопка", 'error');
            return undefined;
        }
        return button;
    }

    private getVerify(): any | null {
        const urlParams = getUrlParams(['verify'])
        const verify = urlParams.verify

        if (verify) {
            return verify;
        } else {
            return null;
        }
    }

    private async buttonQuery(user_id: number | string) {
        if (!this.button) {
            log_sending_to_page("Кнопка не найдена.", 'error');
            return;
        }
        this.button.addEventListener('click', async () => {
            if (!this.button) {
                log_sending_to_page("Кнопка не найдена.", 'error');
                return;
            }

            if (!this.isVerifyOnce) {
                if (this.getVerify() && this.getVerify() === 'true') {
                    this.isVerifyOnce = true;
                } else {
                    log_sending_to_page(`Запрос на подтверждение пароля пользователя ${user_id}`, "log", `/confirm_password?cause=${encodeURIComponent("delete_account")}`);
                    return;
                }
            }

            if (!this.isVeifySecond) {
                if (this.getVerify() && this.getVerify() === 'true') {
                    this.isVeifySecond = true;
                } else {
                    log_sending_to_page(`Запрос на подтверждение почты пользователя ${user_id}`, "log", `/confirm_code?cause=${encodeURIComponent("delete_account")}`);
                    return;
                }
            }

            if (this.isVerifyOnce && this.isVeifySecond && !this.Delete) {
                const description = document.getElementsByClassName("description")[0] as HTMLDivElement;
                
                this.button.textContent = "Запланировать удаление";
                description.innerHTML = `
                <h3>После того как вы нажмете на кнопку, то произойдет заморозка, это значит доступ к этому аккаунту у вас пропадет, но данные останутся на 7 дней.
                <br>За это время можно отменить удаление, но после этого времени данные аккаунта полностью удалятся.</h3>
                `; 
                this.Delete = true;
                return;
            }

            if (this.Delete) {
                const response = await securedApiCall("/delete_account", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id,
                        "delete_confirmation": this.Delete,
                    }),
                });
                if (response && response.ok) {
                    const data = await response.json()
                    if (data.success) {
                        alert("Аккаунт успешно запланирован на удаление.")
                        log_sending_to_page(data.message, "log", "/");
                        return;
                    } else {
                        alert(data.message);
                        return;
                    }
                } else {
                    log_sending_to_page("Не получены данные с сервера, либо запрос завершился неудачей.", "error");
                    return;
                }
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

        await this.buttonQuery(user_id);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const deleteA = new DeleteAccount();
    await deleteA.init();
});