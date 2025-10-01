import { checkUpdateTokens, securedApiCall } from "../../utils/secured.js";
import { deleteFriend } from "../../utils/user.js"

class FriendsProcess {
    private friendsData: Record<string, any> | null = null

    private async FriendProcessControl() {
        if (!this.friendsData) {
            return;
        }

        const friendsDiv = document.getElementById("friends") as HTMLDivElement;

        if (friendsDiv) {
            friendsDiv.addEventListener("click", async (event) => {
                const target = event.target as HTMLElement;

                if (target.tagName === "BUTTON") {
                    const form = target.closest(".friend_control-form") as HTMLFormElement;

                    if (form) {
                        const friendDiv = form.closest("div[data-friend-id]") as HTMLDivElement;
                        const action = target.dataset.action;
                        const friendId = Number(friendDiv.dataset.friendId);

                        if (friendDiv && action && friendId) {

                            switch (action) {
                                case "delete":
                                    const deleted = await deleteFriend(friendId);

                                    if (deleted) {
                                        window.location.reload();
                                    }
                                    break;
                            }
                        }
                    }
                }
            })
        }
    };

    private async getFriendsPage() {
        
        const response = await securedApiCall("/friends/data")
        
        if (response && response.ok) {
            const data = await response.json();
            
            if (data.success) {
                const friendsDiv = document.getElementById("friends") as HTMLDivElement;
                
                if (data.friends) {
                    friendsDiv.innerHTML = 'Загрузка..'
                    this.friendsData = data.friends;
                    
                    let friendsHtml = `<h4>Ваши друзья:</h4>`

                    for (let friendId in this.friendsData) {
                        const friend = this.friendsData[friendId];
                        
                        friendsHtml += `
                        <div class="friend-${friend.addition_number}" data-friend-id="${friendId}">
                            <a href="/friends/${friendId}/profile">${friend.full_name}</a>
                            <form class="friend_control-form">
                                <button data-action="delete">Удалить из друзей</button>
                            </form>
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
        await this.FriendProcessControl();
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