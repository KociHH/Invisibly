import { securedApiCall } from "./secured.js";

async function  change_email_api(
    emailNew: string,
    redirect_url: string,
) {
    const response = await securedApiCall("/change/email", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },  
        body: JSON.stringify({
            new_email: emailNew
        })
    });

    if (response && response.ok) {
        const data = await response.json();

        if (data.success) {
            window.location.href = redirect_url;
            return;

        } else {
            alert(data.message);
            return;
        }
        
    } else {
        console.error("Запрос /change/email завершился неудачей");
        return;
    }
}

export {change_email_api}