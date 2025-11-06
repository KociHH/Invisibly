import { checkUpdateTokens, securedApiCall } from "../../utils/secured.js";
import { WSConfig } from "../../utils/websocket.js";

class ChatsProcess {
    private chatsData: Record<string | number, any> | null = null 

    private async getChats() {
        const response = await securedApiCall("/api/chat/chats/data")

        if (response && response.ok) {
            this.chatsData = await response.json();
            this.renderChats();

        } else {
            console.error('Вызов /chats/data вернулся с ошибкой');
            return;
        }
    }

    private renderChats() {
        const chats = document.getElementById('chats') as HTMLDivElement;
        if (!chats) return;

        if (this.chatsData && Object.keys(this.chatsData).length > 0) {
            let result_chats = ``

            for (let chatId in this.chatsData) {
                const chat = this.chatsData[chatId];
            
                let prefix = "";
                const isWrittenByUser = chat.written_by_current_user === true || chat.written_by_current_user === "true";
                if (isWrittenByUser) {
                    prefix = "вы: ";
                }

                result_chats += `
                <div id='chat-${chatId}'>
                    <h5>${chat.full_name}</h5>
                    <span>${prefix}${chat.content}</span>    
                    <span>${new Date(chat.send_at).toLocaleString()}</span>
                    <a href="/chats/${chatId}">Перейти в чат</a>
                </div>
                `
            }

            chats.innerHTML = result_chats

        } else {
            chats.innerHTML = `Увы, но у вас ещё нет ни одного чата.`
        }
    }

    private readonly WS_RECONNECT_DELAY = 3000

    private reconnectWs(wsc: WSConfig) {
        if (!wsc.wsReconnectTimeout) {
            wsc.wsReconnectTimeout = window.setTimeout(() => {
                wsc.wsReconnectTimeout = null;
                this.connectWebSocket();
            }, this.WS_RECONNECT_DELAY);
        }
    }

    private async connectWebSocket() {
        try {
            const data = await checkUpdateTokens();
            if (!data || !data.success) {
                console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
                return;
            }

            const wsc = new WSConfig;
            try {
                wsc.connect("chat");
            } catch (error) {
                console.error('Ошибка при подключении к WebSocket:', error);
                this.reconnectWs(wsc);
            }

            if (!wsc.ws || !wsc.wsUrl) {
                console.error(`Атрибут 'ws'=${wsc.ws} или 'wsUrl'=${wsc.wsUrl} не был назначен`)
                return;
            }

            wsc.ws.onopen = () => {
                console.log('WebSocket подключен для чатов');
                if (wsc.wsReconnectTimeout) {
                    clearTimeout(wsc.wsReconnectTimeout);
                    wsc.wsReconnectTimeout = null;
                }
            };

            wsc.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data && typeof data === 'object') {
                        this.chatsData = data;
                        this.renderChats();
                    }
                } catch (error) {
                    console.error('Ошибка при парсинге WebSocket сообщения:', error);
                }
            };

            wsc.ws.onerror = (error) => {
                console.error('WebSocket ошибка:', error);
            };

            wsc.ws.onclose = () => {
                console.log('WebSocket отключен, переподключение через 3 секунды...');
                this.reconnectWs(wsc);
            };

        } catch (error) {
            console.error(`Ошибка работы websocket: ${error}`)
            return;
        }
    }

    async init() {        
        await this.getChats();
        await this.connectWebSocket();
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const data = await checkUpdateTokens();

    if (!data || !data.success) {
        console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
        return;
    }

    const chats = new ChatsProcess();
    await chats.init();
});
