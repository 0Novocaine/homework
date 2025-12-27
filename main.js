const formChat = document.getElementById('formChat');
const textField = document.getElementById('textField');
const subscribe = document.getElementById('subscribe');

// подключение к WebSocket серверу
const ws = new WebSocket('ws://localhost:8080');

ws.onopen = () => {
    console.log('Connected to WebSocket server');
};

ws.onmessage = (e) => {
    console.log('Message from server:', e.data);

    const elMsg = document.createElement('div');
    elMsg.innerHTML = e.data;
    subscribe.appendChild(elMsg);
};

ws.onerror = (e) => console.error('WebSocket error', e);
ws.onclose = () => console.log('Disconnected from server');

// отправка сообщений через форму
formChat.addEventListener('submit', (e) => {
    e.preventDefault();
    if (textField.value) {
        ws.send(textField.value);
        textField.value = '';
    }
});