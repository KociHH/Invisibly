(() => {
const form = document.getElementById('register-form') as HTMLFormElement;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = (document.getElementById('name') as HTMLInputElement).value;
    const login = (document.getElementById('login') as HTMLInputElement).value;
    const password = (document.getElementById('password') as HTMLInputElement).value;
    const email = (document.getElementById('email') as HTMLInputElement).value;

    const response = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name, 
            login, 
            password, 
            email, 
            "register": true
        }),
    });
    const data = await response.json();
    if (data.success) {
        localStorage.setItem('accessToken', data.access_token);
        localStorage.setItem('refreshToken', data.refresh_token);
        
        window.location.href = `/profile`;
    } else {
        alert(data.msg);
    }
});
})();