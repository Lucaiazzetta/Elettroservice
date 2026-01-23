async function auth(action) {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    const msg = document.getElementById('msg');

    try {
        const response = await fetch(`http://localhost:5000/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass }),
            credentials: 'include' // <--- FONDAMENTALE
        });

        const data = await response.json();

        if (response.ok) {
            if (action === 'login') {
                // Se il login è OK, il cookie è salvato. Ora cambiamo pagina.
                window.location.href = 'dashboard-client.html';
            } else {
                msg.innerText = "Registrato! Ora effettua il login.";
                msg.style.color = "green";
            }
        } else {
            msg.innerText = data.error || "Errore";
            msg.style.color = "red";
        }
    } catch (error) {
        msg.innerText = "Errore di connessione al server";
    }
}