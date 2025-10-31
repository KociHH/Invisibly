import { log_sending_to_page, getUrlParams, clearItemsStorage, TIME_EXP_REPEATED, TIME_EXP_TOKEN } from "../../utils/other.js";
import { checkUpdateTokens, securedApiCall } from "../../utils/secured.js";

class ChangedEmail {
    private pollIntervalId: number | null = null;
    private email = document.querySelector("#current_email") as HTMLElement;
    private getEmailStorage = localStorage.getItem("HASHED_EMAIL_PAGE")

    private setupDefaultButton(buttonSubmit: HTMLButtonElement) {
        localStorage.removeItem("CHANGE_EMAIL_PENDING");
        if (buttonSubmit) {
            buttonSubmit.disabled = false;
            buttonSubmit.textContent = "Сменить почту";
        }
    }

    private async pollUntilTokenReady(): Promise<void> {
        const buttonSubmit = document.querySelector(".change_email") as HTMLButtonElement;
        if (buttonSubmit) {
            buttonSubmit.disabled = true;
            buttonSubmit.textContent = "Отправка, подождите...";
        }
        const pollStartTime = Date.now();
        const POLL_TIMEOUT = 10000;

        const tick = async () => {
            const elapsed = Date.now() - pollStartTime;
            if (elapsed >= POLL_TIMEOUT) {
                if (this.pollIntervalId !== null) {
                    window.clearInterval(this.pollIntervalId);
                    this.pollIntervalId = null;
                }
                this.setupDefaultButton(buttonSubmit)
                return;
            }

            try {
                const response = await securedApiCall(`/api/security/confirm_code/data?cause=${encodeURIComponent("change_email")}`);
                if (response && response.ok) {
                    const data = await response.json();
                    if (data.verification_token || data.token) {
                        if (this.pollIntervalId !== null) {
                            window.clearInterval(this.pollIntervalId);
                            this.pollIntervalId = null;
                        }
                        this.setupDefaultButton(buttonSubmit);
                        window.location.href = `/confirm_code?cause=${encodeURIComponent("change_email")}`;
                        return;
                    }
                }
            } catch {} // 404
        };
        await tick();
        this.pollIntervalId = window.setInterval(tick, 1500);
    }

    private async getElemEmail() {
        const response = await securedApiCall("/api/settings/change_email/data")
        if (!response || !response.ok) {
            log_sending_to_page('Не удалось загрузить данные для настроек', "error");
            return;
        }

        const data_elem = await response.json();

        localStorage.removeItem("HASHED_EMAIL_PAGE")
        this.email.textContent = data_elem.email
        localStorage.setItem("HASHED_EMAIL_PAGE", data_elem.email)
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
    
            try {
                localStorage.setItem("CHANGE_EMAIL_PENDING", "1");
            } catch {}

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
                    this.setupDefaultButton(buttonSubmit)
                    localStorage.removeItem("HASHED_EMAIL_PAGE")
                    window.location.href = `/confirm_code?cause=${encodeURIComponent("change_email")}`;
                    return;     

                } else {
                    this.setupDefaultButton(buttonSubmit)
                    alert(data.message);
                }
    
            } else {
                localStorage.removeItem("CHANGE_EMAIL_PENDING");
                buttonSubmit.disabled = false;
                buttonSubmit.textContent = "Сменить почту";
                console.error("Не получены данные с сервера, либо запрос завершился неудачей.");
                return;
            }
        });
    }
    
    async init() {
        console.log(localStorage.getItem("CHANGE_EMAIL_PENDING"))
        try {
            const pending = localStorage.getItem("CHANGE_EMAIL_PENDING");
            if (pending === "1") {
                this.email.textContent = this.getEmailStorage || "null"
                const buttonSubmit = document.querySelector(".change_email") as HTMLButtonElement;
                if (buttonSubmit) {
                    buttonSubmit.disabled = true;
                    buttonSubmit.textContent = "Отправка, подождите...";
                }
                await this.pollUntilTokenReady();
                return;
            }
        } catch {}

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