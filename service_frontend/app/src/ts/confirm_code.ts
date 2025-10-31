import { clearItemsStorage, getUrlParams, log_sending_to_page, GET_TOKEN_FROM_DATA, CHANGE_EMAIL_PENDING, TIME_EXP_REPEATED, TIME_EXP_TOKEN } from "./utils/other.js";
import { checkUpdateTokens, DeleteTokenRedis, securedApiCall } from "./utils/secured.js";
import { change_email_api } from "./utils/user.js";

function getStorageExp() {
    const exp_token = localStorage.getItem(TIME_EXP_TOKEN)
    const exp_repeated = localStorage.getItem(TIME_EXP_REPEATED)

    return {
        "exp_token": exp_token, 
        "exp_repeated": exp_repeated
    }
}


class ConfirmCodePage {
    private expiryIntervalId: number | null = null;
    private isExpiredUiShown: boolean = false;
    private isResending: boolean = false;
    private isResendButtonShown: boolean = false;

    private urlParams = getUrlParams(["cause", "email_send"]);
    private cause = decodeURIComponent(this.urlParams["cause"]) || '';

    private user_id: string | number | null = null;
    private getExpRepeatedCodeData: string | number | null = null;
    private getExpTokenData: string | number | null = null;
    private getTokenFromData: string | null = null;
    private newEmailData: string | null = null;

    private storageExp: Record<string, any> = getStorageExp();

    private pollIntervalId: number | null = null;

    private renderFrozenCountdownFromStorage(): void {
        const expTokenStr = localStorage.getItem(TIME_EXP_TOKEN);
        const expRepeatedStr = localStorage.getItem(TIME_EXP_REPEATED);
        if (!expTokenStr || !expRepeatedStr) return;
        const expMsToken = Number(expTokenStr);
        const expMsRepeated = Number(expRepeatedStr);
        if (!Number.isFinite(expMsToken) || !Number.isFinite(expMsRepeated)) return;
        const now = Date.now();
        const timeLeftToken = Math.max(0, expMsToken - now);
        const timeLeftRepeated = Math.max(0, expMsRepeated - now);
        this.updateCountdownUI(timeLeftToken, timeLeftRepeated);
    }

    private clearWindowInterval() {
        if (this.pollIntervalId !== null) {
            window.clearInterval(this.pollIntervalId);
            this.pollIntervalId = null;
        }
    }

    private async pollUntilResendReady(): Promise<void> {
        this.StopUiShown();

        const pollStartTime = Date.now();
        const POLL_TIMEOUT = 10000;

        const tick = async () => {
            const elapsed = Date.now() - pollStartTime;
            if (elapsed >= POLL_TIMEOUT) {
                this.clearWindowInterval();
                await this.startExpiryWatcher();
                this.setupResendButton();
                return;
            }
            // проверка на новый токен
            try {
                const response = await securedApiCall(`/api/security/confirm_code/data?cause=${encodeURIComponent(this.cause)}`);
                if (response && response.ok) {
                    const data_elem = await response.json();
                    
                    if (data_elem.verification_token !== localStorage.getItem(GET_TOKEN_FROM_DATA)) {
                        console.log(`verification_token: ${data_elem.verification_token} getTokenFromData: ${localStorage.getItem(GET_TOKEN_FROM_DATA)}`)
                        this.clearWindowInterval();
                        this.StopUiShown();
                        localStorage.removeItem(GET_TOKEN_FROM_DATA)
                        clearItemsStorage([TIME_EXP_REPEATED, TIME_EXP_TOKEN, CHANGE_EMAIL_PENDING])
                        this.isResendButtonShown = false
                        window.location.href = `/confirm_code?cause=${encodeURIComponent("change_email")}`;
                        return;
                    }
                }
                return;
            } catch {} // 404
        };
        await tick();
        this.pollIntervalId = window.setInterval(tick, 1500);
    }

    private async startPoll(): Promise<string | null> {
        const pending = localStorage.getItem(CHANGE_EMAIL_PENDING);
        if (pending === "1") {
            this.isResending = true;
            const resendDiv = document.getElementById("repeated_code") as HTMLElement;
            if (resendDiv && !this.isResendButtonShown) {
                resendDiv.innerHTML = '<button class="resend_button" disabled>Отправка, подождите...</button>';
                this.isResendButtonShown = true;
            }
            await this.pollUntilResendReady();
        }
        return pending;
    }

    public async init(): Promise<void> {
        const pending = localStorage.getItem(CHANGE_EMAIL_PENDING);
        const data = await checkUpdateTokens();

        let user_id;
        if (data && data.success) {
            user_id = data.user_id;
        } else {
            log_sending_to_page(`Не вернулось значение функции checkUpdateTokens: ${data}`, "error");
            return;
        }
        this.user_id = user_id;

        try {
            await this.startPoll();
        } catch {}

        if (pending === "1") {
            this.renderFrozenCountdownFromStorage();
            return;
        }

        await this.getElemDataCode();

        if (!this.getTokenFromData) {
            console.error(`Токен не найден или не удалось загрузить данные: ${this.getTokenFromData}`);
            return;
        }
        
        const email = document.getElementsByClassName("email")[0] as HTMLElement;
        email.textContent = this.newEmailData

        try {
            this.setupForm();
            await this.startExpiryWatcher();     

        } catch (error) {
            log_sending_to_page(`Ошибка инициализации: ${error}`, "error");
            return;
        }
    }

    private setupForm(): void {
        const form = document.getElementById('verification-form') as HTMLFormElement;
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }

    private async handleFormSubmit(e: Event): Promise<void> {
        e.preventDefault();
        
        this.StopUiShown();

        const codeInput = document.getElementById('code') as HTMLInputElement;
        const code = codeInput.value.trim();

        try {
            const response = await securedApiCall(`/api/security/confirm_code`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: code,
                    token: this.getTokenFromData
                })
            });

            if (response && response.ok) {
                if (!this.newEmailData) {
                    console.error("Не задана переменная emailData");
                    return;
                }

                const result = await response.json();
                
                if (result.success) {
                    if (this.cause == "change_email") {
                        await change_email_api(this.newEmailData, "/settings");
                        return;
                    
                    } else if (this.cause == "change_password") {
                        log_sending_to_page(`Код подтвержден успешно юзера ${result.user_id}`, 'log', `/${this.cause}?verify=${encodeURIComponent("true")}&cause=${encodeURIComponent(this.cause)}&email=${encodeURIComponent(this.newEmailData)}`);
                        return;
                    }

                } else {
                    alert('Invalid verification code; open your email.');
                    await this.startExpiryWatcher();
                }
            }
        } catch {}
    }

    private async getElemDataCode(): Promise<void> {
        try {
            const response = await securedApiCall(`/api/security/confirm_code/data?cause=${encodeURIComponent(this.cause)}`)
            if (!response || !response.ok) {
                if (!response || (response && response.status !== 404)) {
                    console.error('Не удалось загрузить данные для подтверждения email');
                }
                return;
            }

            const data_elem = await response.json();

            this.newEmailData = data_elem.email
            this.getTokenFromData = data_elem.verification_token
            localStorage.setItem(GET_TOKEN_FROM_DATA, this.getTokenFromData || "null")

            if (!this.storageExp.exp_token || !this.storageExp.exp_repeated) {
                this.getExpRepeatedCodeData = data_elem.exp_repeated_code_iso
                this.getExpTokenData = data_elem.exp_token
            } 
        } catch (error) {
            console.error(`Ошибка при запросе данных GET: ${error}`);
            return;
        }
    }

    private async startExpiryWatcher(): Promise<void> {
        if (this.expiryIntervalId !== null) return;
        const noApi = (!this.getExpRepeatedCodeData || !this.getExpTokenData);
        const noStorage = (!this.storageExp.exp_token || !this.storageExp.exp_repeated);
        if (noApi && noStorage) {
            console.warn("Нет дедлайнов ни из API, ни из storage");
            return;
        }

        const expRepeated = this.getExpRepeatedCodeData ? this.getExpRepeatedCodeData : Number(this.storageExp.exp_repeated);
        const expToken = this.getExpTokenData ? this.getExpTokenData : Number(this.storageExp.exp_token);
        if (!expToken) return;
        
        // ISO format
        const expMsRepeated = new Date(expRepeated).getTime()
        const expMsToken = new Date(expToken).getTime();
        if (isNaN(expMsToken)) return;

        localStorage.setItem(TIME_EXP_REPEATED, String(expMsRepeated))
        localStorage.setItem(TIME_EXP_TOKEN, String(expMsToken))

        const tick = async () => {
            const now = Date.now();
            const timeLeftRepeated = Math.max(0, expMsRepeated - now);
            const timeLeftToken = Math.max(0, expMsToken - now);
            // истек токен
            if (timeLeftToken <= 0 && !this.isExpiredUiShown) {
                this.StopUiShown();
                if (!this.user_id || !this.getTokenFromData) {
                    console.warn("Не передано значение переменной user_id либо getTokenFromData");
                    return;
                }

                try {
                    const data = await DeleteTokenRedis(this.cause);
                    if (data) {                        
                        window.location.href = `/${this.cause}`;
                        return;
                    }
        
                } catch (error) {
                    console.error(`Ошибка при удалении токена: ${error}`);
                    return;
                }
            }
            // показывает кнопку
            if (timeLeftRepeated <= 0 && !this.isResendButtonShown) {
                this.setupResendButton();
            }

            this.updateCountdownUI(timeLeftToken, timeLeftRepeated);
        };

        await tick();
        this.expiryIntervalId = window.setInterval(tick, 1000);
    }

    private updateCountdownUI(timeLeftToken: number, timeLeftRepeated: number): void {
        this.updateTokenUI(timeLeftToken);
        this.updateRepeatedUI(timeLeftRepeated);
    }
      
    private updateTokenUI(left: number): void {
        const minutes = Math.floor(left / 60000);
        const seconds = Math.floor((left % 60000) / 1000);

        const secondsStr = seconds < 10 ? `0${seconds}` : String(seconds);
        const minutesStr = minutes < 10 ? `0${minutes}` : String(minutes);

        const life_time_code = document.querySelector("#life_time_code");
        if (life_time_code) {
          life_time_code.innerHTML = `<p>Текущий код будет действителен еще:</p><h4>${minutesStr}:${secondsStr}</h4>`;
        }
    }
      
    private updateRepeatedUI(left: number): void {
        const repeated_code = document.querySelector("#repeated_code");
        if (!repeated_code) return;
        if (left > 0) {
          const minutes = Math.floor(left / 60000);
          const seconds = Math.floor((left % 60000) / 1000);

          const secondsStr = seconds < 10 ? `0${seconds}` : String(seconds);
          const minutesStr = minutes < 10 ? `0${minutes}` : String(minutes);

          repeated_code.innerHTML = `<p>Можно отправить повторно через:</p><h4>${minutesStr}:${secondsStr}</h4>`;
        }
    }

    private setupResendButton(): void {
        clearItemsStorage([CHANGE_EMAIL_PENDING, TIME_EXP_REPEATED]);
        const resendDiv = document.getElementById("repeated_code") as HTMLElement;
        if (resendDiv && !this.isResendButtonShown) {
            resendDiv.innerHTML = '';
            const resendButton = document.createElement('button');
            resendButton.textContent = "Отправить повторно";
            resendButton.className = 'resend_button';
            resendButton.addEventListener('click', () => this.handleResendCode());
            
            resendDiv.appendChild(resendButton);
            this.isResendButtonShown = true; 
        }
    }
    
    private StopUiShown() {
        if (this.expiryIntervalId !== null) {
            clearInterval(this.expiryIntervalId);
            this.expiryIntervalId = null;
        } else return
    }

    private async handleResendCode(): Promise<void> {
        if (this.isResending) return;
        
        this.isResending = true;
        
        try {
            localStorage.setItem(CHANGE_EMAIL_PENDING, "1");
        } catch {}
        const resendButton = document.querySelector('.resend_button') as HTMLButtonElement;
        if (resendButton) {
            resendButton.disabled = true;
            resendButton.textContent = 'Отправка, подождите...';
            this.StopUiShown();
        }

        // отправка email и обновление токена
        try {
            const response = await securedApiCall(`/api/security/confirm_code/data?cause=${encodeURIComponent(this.cause)}&resend=${encodeURIComponent("true")}`);
            if (response && response.ok) {
                clearItemsStorage([TIME_EXP_TOKEN, TIME_EXP_REPEATED, CHANGE_EMAIL_PENDING]);
                
                const data = await response.json();
                if (data.token || data.verification_token) {
                    this.getTokenFromData = data.token || data.verification_token;
        
                    const expToken = new Date(data.exp_token).getTime();
                    const expRepeated = new Date(data.exp_repeated_code_iso).getTime();
        
                    if (Number.isFinite(expToken)) {
                        localStorage.setItem(TIME_EXP_TOKEN, String(expToken));
                        this.getExpTokenData = data.exp_token;
                    }
                    if (Number.isFinite(expRepeated)) {
                        localStorage.setItem(TIME_EXP_REPEATED, String(expRepeated));
                        this.getExpRepeatedCodeData = data.exp_repeated_code_iso;
                    }
        
                    this.isResendButtonShown = false;

                    window.location.href = `/confirm_code?cause=${encodeURIComponent(this.cause)}`;
                }
                return;
            }   
        } catch {}
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const page = new ConfirmCodePage();
    await page.init();
});
