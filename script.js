const items = document.querySelectorAll('.item');
const next = document.getElementById('next');
const prev = document.getElementById('prev');
const number = document.querySelector('.numbers');
const dots = document.querySelectorAll('.indicators li');

let index = 0;

function showItem(i) {
    items.forEach(item => item.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    items[i].classList.add('active');
    dots[i].classList.add('active');

    number.textContent = String(i + 1).padStart(2, '0');
}

next.addEventListener('click', () => {
    index++;
    if (index >= items.length) index = 0;
    showItem(index);
});

prev.addEventListener('click', () => {
    index--;
    if (index < 0) index = items.length - 1;
    showItem(index);
});


//const API_URL = "http://localhost:8000"; 
const API_URL = "/api";

let currentSessionId = localStorage.getItem('chat_session_id');
if (!currentSessionId) {
    currentSessionId = "sessao_" + Math.random().toString(36).substring(2, 10);
    localStorage.setItem('chat_session_id', currentSessionId);
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_URL}/portfolio/historico/${currentSessionId}`);
        
        if (!response.ok) return; 

        const history = await response.json();
        
        history.forEach(msg => {
            const chatBox = document.querySelector(`.chat-box[data-model="${msg.model_used}"]`);
            if (chatBox) {
                const historyArea = chatBox.querySelector('.chat-history');
                const senderRole = msg.role === 'user' ? 'user' : 'bot';
                appendMessage(historyArea, msg.content, senderRole);
            }
        });
    } catch (error) {
        console.log("Erro ao carregar histórico:", error);
    }
}

document.addEventListener("DOMContentLoaded", loadHistory);

function appendMessage(container, text, sender, id = null) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = text;
    if (id) msgDiv.id = id; 
    container.appendChild(msgDiv);
    
    container.scrollTop = container.scrollHeight;
}

async function sendMessage(buttonElement) {
    const chatBox = buttonElement.closest('.chat-box');
    const inputField = chatBox.querySelector('input');
    const historyArea = chatBox.querySelector('.chat-history');
    const modelChoice = chatBox.getAttribute('data-model'); 
    
    const messageText = inputField.value.trim();
    if (!messageText) return;

    appendMessage(historyArea, messageText, 'user');
    inputField.value = '';

    buttonElement.disabled = true;
    inputField.disabled = true;
    buttonElement.style.opacity = "0.5"; 
    
    const loadingId = "loading-" + Date.now();
    appendMessage(historyArea, "Lendo os documentos e pensando...", 'bot', loadingId);

    try {
        const response = await fetch(`${API_URL}/portfolio/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: messageText,
                model_choice: modelChoice 
            })
        });

        document.getElementById(loadingId)?.remove();

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const data = await response.json();
        const botResponse = data.response || "Resposta recebida, mas sem conteúdo de texto.";
        appendMessage(historyArea, botResponse, 'bot');
        
    } catch (error) {
        document.getElementById(loadingId)?.remove();
        console.error("Erro na comunicação com o backend:", error);
        appendMessage(historyArea, "Erro ao conectar com o servidor.", 'bot');
    } finally {
        buttonElement.disabled = false;
        inputField.disabled = false;
        buttonElement.style.opacity = "1";
        inputField.focus(); 
    }
}

document.querySelectorAll('.chat-input-area input').forEach(input => {
    input.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault(); 
            if (!this.disabled) { 
                sendMessage(this.nextElementSibling); 
            }
        }
    });
});


function openModal(event) {
    event.preventDefault(); 
    document.getElementById("contact-modal").style.display = "block";
}

function closeModal() {
    document.getElementById("contact-modal").style.display = "none";
}

window.onclick = function(event) {
    const modal = document.getElementById("contact-modal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
    
}

function scrollToTop(event) {
    event.preventDefault();
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}