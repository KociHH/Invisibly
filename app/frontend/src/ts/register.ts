(() => {
const form = document.getElementById('register-form') as HTMLFormElement;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = (document.getElementById('name') as HTMLInputElement).value;
    const username = (document.getElementById('username') as HTMLInputElement).value;
    const password = (document.getElementById('password') as HTMLInputElement).value;

    const response = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, username, password}),
    });
    const data = await response.json();
    alert(data.msg);
});
})();