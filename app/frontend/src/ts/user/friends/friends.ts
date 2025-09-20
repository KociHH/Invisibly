import { checkUpdateTokens, securedApiCall } from "../../utils/secured.js";

class FriendsProcess {
    private friendsData: Record<string, any> | null = null

    private async getFriendsPage() {
        
        const response = await securedApiCall("/friends/data")
        
        if (response && response.ok) {
            const data = await response.json();
            
            if (data.success) {
                const friendsDiv = document.getElementById("friends") as HTMLDivElement;
                
                if (data.friends) {
                    friendsDiv.innerHTML = 'Загрузка..'
                    this.friendsData = data.friends;
                    
                    let friendsHtml = ``

                    for (let friendId in this.friendsData) {
                        const friend = this.friendsData[friendId];
                        
                        friendsHtml += `
                        <div class="friend-${friend.addition_number}">
                            <a href="/friends/${friendId}/profile">${friend.full_name}</a>
                        </div>
                        `                        
                    }
                    
                    friendsDiv.innerHTML = friendsHtml;

                } else {
                    friendsDiv.innerHTML = `Нет добавленных друзей.`;
                } 

            }

        } else {
            console.error('Вызов /friends/data вернулся с ошибкой');
            return;
        }
    }

    async init() {
        await this.getFriendsPage();
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const data = await checkUpdateTokens();

    if (!data || !data.success) {
        console.error(`Не вернулось значение функции checkUpdateTokens: ${data}`);
        return;
    }

    const friends = new FriendsProcess;
    await friends.init();
});