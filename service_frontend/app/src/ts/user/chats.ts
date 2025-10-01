import { checkUpdateTokens, securedApiCall } from "../utils/secured.js";

class ChatsProcess {
    private chatsData: Record<string | number, any> | null = null 

    private async getChats() {
        const response = await securedApiCall("/chats/data")

        if (response && response.ok) {
            this.chatsData = await response.json();

            const chats = document.getElementById('chats') as HTMLDivElement;

            if (this.chatsData) {
                let result_chats = ``

                for (let chatId in this.chatsData) {
                    const chat = this.chatsData.get(chatId);
                
                    result_chats = `
                    <div id='chat-${chatId}'>
                        <h5>${chat.full_name}</h5>
                        <span>${chat.last_message}</span>    
                        <span>${chat.send_at}</span>
                    </div>
                    `
                }

                chats.innerHTML = result_chats

            } else {
                chats.innerHTML = `Увы, у вас ещё нет ни одного чата.`
                return;                
            }

        } else {
            console.error('Вызов /chats/data вернулся с ошибкой');
            return;
        }
    }
    

    async init() {
        await this.getChats();
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const data = await checkUpdateTokens();

    if (!data || !data.success) {
        console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
        return;
    }

    const chats = new ChatsProcess;
    await chats.init();
});