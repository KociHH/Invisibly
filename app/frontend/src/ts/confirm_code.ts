import { getUrlParams, log_sending_to_page } from "./utils/other.js";

class ConfirmCodePage {
    private token: string;
    private expiryIntervalId: number | null = null;
    private isExpiredUiShown: boolean = false;
    private isResending: boolean = false;

    private urlParams = getUrlParams(["cause"])
    private cause = this.urlParams.get("cause") || '';

    constructor() {
        this.token = this.getTokenFromPage();
        this.init();
    }

    // Get Object from page
    private getTokenFromPage(): string {
        const tokenInput = document.getElementById('verification_token') as HTMLInputElement;
        return tokenInput?.value || '';
    }

    private getExpRepeatedCodePage(): string {
        const expRepeatedInput = document.getElementById('exp_repeated_code') as HTMLInputElement;
        return expRepeatedInput?.value || '';
    }

    private getExpTokenPage(): string {
        const expInput = document.getElementById('exp_token') as HTMLInputElement;
        return expInput?.value || '';
    }

    // main
    private async init(): Promise<void> {
        if (!this.token) {
            log_sending_to_page('Токен не найден', "error");
            return;
        }
        
        try {
            this.setupForm();
            this.startExpiryWatcher();     

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
        
        const codeInput = document.getElementById('code') as HTMLInputElement;
        const code = codeInput.value.trim();

        try {
            const response = await fetch(`/confirm_code?cause=${encodeURIComponent(this.cause)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: code,
                    token: this.token
                })
            });
            if (response.status == 401) {
                this.ExpireTokenPage()
            }

            let result: any
            try {
                result = await response.json();
            } catch {
                log_sending_to_page(`Нет ожидаемых данных от сервера: ${result}`, "error");
                return;
            }
            if (!response.ok) {
                log_sending_to_page(result?.detail || 'Ошибка сервера', 'error');
                return;
            }

            if (result.success) {
                log_sending_to_page(`Код подтвержден успешно юзера ${result.user_id}`, 'log', `/${this.cause}?verify=true`);
                return;
            } else {
                alert('Invalid verification code; open your email.');
            }
            

        } catch (error) {
            log_sending_to_page(`Ошибка отправки: ${error}`, "error");
            return;
        }
    }

    private ExpireTokenPage(): void {
        const life_time_code = document.getElementById("life_time_code");
        if (life_time_code) {
            life_time_code.textContent = 'Время текущего кода истекло, нажмите на кнопку ниже, чтобы отправить повторно код.';
        }
        this.isExpiredUiShown = true;
        this.setupResendButton()
    }

    private startExpiryWatcher(): void {
        const expRepeated = this.getExpRepeatedCodePage();
        const expToken = this.getExpTokenPage();
        if (!expToken) return;
        
        // ISO format
        const expMsRepeated = new Date(expRepeated).getTime()
        const expMsToken = new Date(expToken).getTime();
        if (isNaN(expMsToken)) return;

        const tick = () => {
            const now = Date.now();
            const timeLeftRepeated = Math.max(0, expMsRepeated - now);
            const timeLeftToken = Math.max(0, expMsToken - now);
            
            if (timeLeftToken <= 0 && !this.isExpiredUiShown) {
                this.ExpireTokenPage();
                this.CheckUiShown();
                return;
            }

            if (timeLeftRepeated <= 0) {
                this.setupResendButton();
                this.CheckUiShown();
            }

            this.updateCountdownUI(timeLeftToken, timeLeftRepeated);
        };

        tick();
        this.expiryIntervalId = window.setInterval(tick, 1000);
    }

    private updateCountdownUI(
        timeLeftToken: number,
        timeLeftRepeated: number,
    ): void {
        const timeLeft: number[] = [timeLeftToken, timeLeftRepeated]

        for (const time of timeLeft) {
            const minutes = Math.floor(time / 60000);
            const seconds = Math.floor((time % 60000) / 1000);
            const secondsStr = seconds < 10 ? `0${seconds}` : seconds.toString();
            const minutesStr = minutes < 10 ? `0${minutes}` : minutes.toString();
            
            if (time == timeLeftToken) {
                const lifeTimeElement = document.getElementById("life_time_code");
                
                if (lifeTimeElement) {
                    lifeTimeElement.innerHTML = `<h6>Текущий код будет действителен еще: ${minutesStr}:${secondsStr}</h6>`;
                }
            } else if (time == timeLeftRepeated) {
                const lifeTimeElementRepeated = document.getElementById("repeated_code")
                
                if (lifeTimeElementRepeated) {    
                    lifeTimeElementRepeated.innerHTML = `<h5>Можно отправить повторно через: ${minutesStr}:${secondsStr}</h5>`;
                }
            }
        };
        return;
    }

    private setupResendButton(): void {
        const resendDiv = document.getElementById('repeated_code');
        if (resendDiv) {
            const resendButton = document.createElement('button');
            resendButton.textContent = 'Отправить код повторно.';
            resendButton.className = 'resend-button';
            resendButton.addEventListener('click', () => this.handleResendCode());
            
            resendDiv.appendChild(document.createElement('br'));
            resendDiv.appendChild(resendButton);
        }
    }
    
    private CheckUiShown() {
        if (this.expiryIntervalId !== null) {
            clearInterval(this.expiryIntervalId);
            this.expiryIntervalId = null;
        } else return
    }

    private async handleResendCode(): Promise<void> {
        if (this.isResending) return;
        
        this.isResending = true;
        const resendButton = document.querySelector('.resend-button') as HTMLButtonElement;
        if (resendButton) {
            resendButton.disabled = true;
            resendButton.textContent = 'Отправка...';
        }

        try {
            const response = await fetch(`/confirm_code?cause=${encodeURIComponent(this.cause)}&resend=true`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
            });

            if (response.ok) {
                window.location.reload();
            } else {
                log_sending_to_page('Ошибка повторной отправки кода', "error");
                return;
            }
        } catch (error) {
            log_sending_to_page(`Ошибка повторной отправки: ${error}`, "error");
            return;

        } finally {
            this.isResending = false;
            if (resendButton) {
                resendButton.disabled = false;
                resendButton.textContent = 'Отправить код повторно';
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ConfirmCodePage();
});
