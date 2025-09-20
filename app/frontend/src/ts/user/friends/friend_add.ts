import { checkUpdateTokens, securedApiCall } from "../../utils/secured.js";

class FriendAddProcess {
    private async friendValid() {
        const form = document.getElementById("add_friend-form") as HTMLFormElement;

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const loginInput = (document.getElementById("login") as HTMLInputElement);
            const login = loginInput.value;

            const response = await securedApiCall("/friends/add", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({login})
            });

            if (response && response.ok) {
                const data = await response.json();

                if (data.success) {
                    alert(data.message);
                    loginInput.value = '';

                } else {
                    alert(data.message);
                }

            } else {
                console.error('Вызов /friends/add вернулся с ошибкой');
                return;
            }
        })
    }

    async init() {
        await this.friendValid();
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const data = await checkUpdateTokens();

    if (!data || !data.success) {
        console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
        return;
    }

    const friend = new FriendAddProcess;
    await friend.init();
});