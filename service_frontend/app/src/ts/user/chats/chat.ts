import { checkUpdateTokens } from "../../utils/secured.js";
import { WSConfig } from "../../utils/websocket.js";

class ChatProcess {
    private history: Record<string | number, any> | null = null 

    private async renderChat() {

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

    }

    async init() {        
        await this.renderChat();
        await this.connectWebSocket();
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const data = await checkUpdateTokens();

    if (!data || !data.success) {
        console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
        return;
    }
    
    const chat = new ChatProcess();
    await chat.init();
})