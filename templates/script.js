async function auth(action) {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    const msg = document.getElementById('msg');

   
    let url = "";
    if (action === 'register') {
        url = "http://127.0.0.1:5000/api/register";
    } else {
        url = "http://127.0.0.1:5000/api/login";
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass }),
            credentials: 'include' 
        });

        const data = await response.json();

        // 2. Controllo se l'operazione è andata a buon fine
        if (data.success) { // Usiamo "success" che arriva dal Python
            
            if (action === 'register') {
                // Caso REGISTRAZIONE
                msg.innerText = "Registrazione avvenuta! Ora fai il login.";
                msg.style.color = "green";
            } else {
                // Caso LOGIN
                msg.innerText = "Login effettuato... reindirizzamento";
                msg.style.color = "green";

                // 3. Reindirizzamento basato sul RUOLO (role)
                if (data.role === 'admin') {
                    // Se è admin, vai alla dashboard amministratore
                    window.location.href = 'dashboard-admin.html'; 
                } else {
                    // Se è un utente normale, vai alla pagina utente
                    window.location.href = 'dashboard-client.html'; 
                }
            }

        } else {
           
            msg.innerText = data.message; // Mostra il messaggio del Python
            msg.style.color = "red";
        }

    } catch (error) {
        console.error(error);
        msg.innerText = "Errore di connessione al server";
        msg.style.color = "red";
    }
}