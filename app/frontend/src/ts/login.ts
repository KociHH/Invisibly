(() => {
const form = document.getElementById('login-form') as HTMLFormElement;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = (document.getElementById('name') as HTMLInputElement).value;
    const password = (document.getElementById('password') as HTMLInputElement).value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password}),
    });
    const data = await response.json();
    if (data.success) {
        window.location.href = `/home/${data.user_id}`;
    } else {
        alert(data.msg);
    }
});
})();