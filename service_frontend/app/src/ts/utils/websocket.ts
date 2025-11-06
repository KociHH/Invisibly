import { ACCESS_TOKEN_KEY } from "./secured";

class WSConfig {
    public ws: WebSocket | null = null
    public token: string | null = null
    public wsUrl: string | null = null
    public wsReconnectTimeout: number | null = null

    public connect(route: string) {
        const token = localStorage.getItem(ACCESS_TOKEN_KEY);
        if (!token) {
            console.error(`${ACCESS_TOKEN_KEY} токен не найден`);
            return;
        }
        this.token = token

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/api/${route}/ws?token=${encodeURIComponent(token)}`;
        
        this.ws = new WebSocket(wsUrl);
        this.wsUrl = wsUrl
    }

    public disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        if (this.wsReconnectTimeout) {
            clearTimeout(this.wsReconnectTimeout);
            this.wsReconnectTimeout = null;
        }
    }

    
}

export {
    WSConfig,
};