import { log_sending_to_page } from "../utils/other.js";
import { checkUpdateTokens, securedApiCall } from "../utils/secured";

class Buttons {
    public save = this.saveButton()
    public cancle = this.cancleButton()

    private saveButton() {
        const button = document.getElementById("submit") as HTMLButtonElement;
        if (!button) {
            log_sending_to_page("Кнопка submit не найдена", "error");
            return;
        }
        return button
    }

    private cancleButton() {
        const button = document.getElementById("cancle") as HTMLButtonElement;
        if (!button) {
            log_sending_to_page("Кнопка cancle не найдена", "error");
            return;
        }
        return button
    }
}

class ItemsInput {
    public name = this.getNamePage()
    public surname = this.getSurnamePage()
    public login = this.getLoginPage()
    public bio = this.getBioContentPage()

    private getNamePage(): HTMLInputElement {
        const nameInput = document.getElementById("name") as HTMLInputElement;
        return nameInput
    };
    private getSurnamePage(): HTMLInputElement {
        const surnameInput = document.getElementById("surname") as HTMLInputElement;
        return surnameInput
    };
    private getLoginPage(): HTMLInputElement {
        const loginInput = document.getElementById("login") as HTMLInputElement;
        return loginInput
    };
    private getBioContentPage(): HTMLTextAreaElement {
        const bioInput = document.getElementById("bio_content") as HTMLTextAreaElement;
        return bioInput
    };
}

class EditProfile {
    private buttons = new Buttons()
    private items = new ItemsInput()
    private isChanges = false

    private originalName: string = ""
    private originalSurname: string = ""
    private originalLogin: string = ""
    private originalBio: string = ""

    private async editProfileFrom(user_id: number | string) {
        this.updateIsChanges()
        
        this.buttons.save?.addEventListener("click", async () => {
            if (this.isChanges) {
                this.isChanges = false

                const response = await securedApiCall("/edit_profile", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id,
                        "name": this.items.name.value,
                        "surname": this.items.surname.value,
                        "login": this.items.login.value,
                        "bio": this.items.bio.value,
                    })
                });

                if (response && response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        alert("Успешно сохранено!")
                        return;
                        
                    } else {
                        alert("Не удалось сохранить.");
                        return;
                    }
                }
            }
        });

        this.buttons.cancle?.addEventListener("click", async () => {
            if (this.isChanges) {
                this.items.name.value = this.originalName;
                this.items.surname.value = this.originalSurname;
                this.items.login.value = this.originalLogin;
                this.items.bio.value = this.originalBio;
                this.updateIsChanges();
                alert("Изменения отменены.");
            }
        })
    }

    private updateIsChanges(): boolean {
        this.isChanges = 
            this.items.name.value !== this.originalName ||
            this.items.surname.value !== this.originalSurname ||
            this.items.login.value !== this.originalLogin ||
            this.items.bio.value !== this.originalBio;
        return this.isChanges;
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

        this.originalName = this.items.name.value;
        this.originalSurname = this.items.surname.value;
        this.originalLogin = this.items.login.value;
        this.originalBio = this.items.bio.value;

        this.editProfileFrom(user_id); 

        this.items.name.addEventListener('input', () => {this.updateIsChanges()});
        this.items.surname.addEventListener('input', () => {this.updateIsChanges()});
        this.items.login.addEventListener('input', () => {this.updateIsChanges()});
        this.items.bio.addEventListener('input', () => {this.updateIsChanges()});
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const edit = new EditProfile();
    await edit.init();
});