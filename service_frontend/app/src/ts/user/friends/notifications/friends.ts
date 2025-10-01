import { checkUpdateTokens, securedApiCall } from "../../../utils/secured.js";

class NotificationsFriends {
    private friendsRequestsData: Record<string, any> | null = null

    private async getFriendsRequests() {
        const response = await securedApiCall("/notifications/friends/data")
    
        if (response && response.ok) {
            const data = await response.json();

            if (data.success) {
                this.friendsRequestsData = data.friends_requests;

                const friendsRequests = document.getElementById("friends_requests") as HTMLDivElement;

                if (this.friendsRequestsData) {
                    let result_text = `<h4>Заявки других пользователей на добавление в друзья</h4>`

                    for (let requestId in this.friendsRequestsData) {
                        const request = this.friendsRequestsData[requestId]

                        result_text += `
                        <div id="request-${requestId}">
                            <span>${request.full_name}</span>
                            <form class="request_control-form">
                                <button data-action="accept">Принять</button>
                                <button data-action="refuse">Отказать</button>
                            </from>    
                            <span>${request.send_at}</span>
                        </div>
                        `

                        friendsRequests.innerHTML = result_text;
                    }

                } else {
                    friendsRequests.innerHTML = `Ничего не найдено.`
                }

            }
            
        } else {
            console.error('Вызов /notifications/friends/data вернулся с ошибкой');
            return;
        }
    }   

    async init() {
        await this.getFriendsRequests();
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const data = await checkUpdateTokens();

    if (!data || !data.success) {
        console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
        return;
    }

    const notifications = new NotificationsFriends;
    await notifications.init();
});