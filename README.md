# 🚨 Alertae

**Alertae** é um sistema inteligente de detecção de gestos para situações de emergência. Através de uma interface gráfica intuitiva, os usuários podem cadastrar seu endereço, e em seguida, acionar alertas *moderados* ou *severos* usando **gestos com as mãos e postura corporal**, que são detectados em tempo real pela câmera, com envio automático para um banco de dados e notificação por e-mail.

## 🧠 Objetivo

Este projeto foi desenvolvido como parte de um trabalho prático de engenharia de software, com foco em aplicações de visão computacional, geolocalização e integração com back-end.

## 👥 Integrantes

- Julia Azevedo Lins — RM98690  
- Luis Gustavo Barreto Garrido — RM99210  
- Victor Hugo Aranda Forte — RM99667

---
## 📹 Demonstração em Vídeo

Confira a demonstração do sistema no YouTube:  
🔗 https://www.youtube.com/watch?v=V9zHy3jgKkI

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Tkinter** (GUI)
- **OpenCV** e **Mediapipe** (Visão Computacional)
- **Supabase** (Banco de dados e envio de notificações)
- **API ViaCEP** (Obtenção de endereço via CEP)
- **Nominatim OpenStreetMap** (Geocodificação de endereço)
- **ttkthemes** (Estilização da interface)

---

## 🎮 Como Funciona

### Etapa 1: Interface Gráfica
- O usuário preenche um formulário com seu nome, e-mail e CEP.
- A aplicação consulta o endereço via **ViaCEP** e permite confirmar o número.

### Etapa 2: Detecção de Gestos
- A câmera é ativada e detecta:
  - ✋ **Alerta Moderado**: gesto do "sinal universal" (mão aberta → polegar dobrado → punho fechado).
  - 🙅‍♂️ **Alerta Severo**: braços abertos cruzando na frente do corpo, abaixo dos ombros.

### Etapa 3: Envio de Alerta
- O alerta é enviado para a **Supabase**, com título, mensagem, e-mail e coordenadas geográficas.
- A localização é convertida via **Nominatim** com base no endereço do formulário.

---

## 📁 Estrutura do Projeto

```
Alertae/
│
├── main.py                  # Interface gráfica (Tkinter)
├── gesture_detector.py      # Lógica de detecção de gestos (OpenCV + Mediapipe)
├── supabase_client.py       # Integração com Supabase para envio dos alertas
├── utils.py                 # Utilitários de geolocalização e timestamps
├── logo.png                 # Logo opcional exibida no topo da interface
└── README.md                # Documentação do projeto
```

---

## ⚙️ Como Executar Localmente

### Pré-requisitos

- Python 3.10 ou superior
- Virtualenv (opcional, mas recomendado)

### Instalação de dependências

```bash
pip install opencv-python mediapipe requests ttkthemes supabase
```

### Execução do Projeto

```bash
python main.py
```

> Certifique-se de que sua webcam está funcionando corretamente.

---

## 🛡️ Segurança

⚠️ **Atenção:** a chave da Supabase utilizada no projeto está em modo anônimo. Para uso em produção, recomendamos:

- Criar uma Role com permissões limitadas.
- Usar autenticação segura com tokens de acesso.
- Nunca subir a chave pública no GitHub.

---

## 📌 Observações

- O sistema não detecta múltiplas pessoas simultaneamente.
- É necessário uma boa iluminação para que os gestos sejam detectados com precisão.
- A geolocalização pode não funcionar em endereços incompletos ou inexistentes no OpenStreetMap.

---

## 💡 Melhorias Futuras

- Integração com SMS ou WhatsApp.
- Detecção de quedas via pose corporal.
- Modo silencioso para alertas disfarçados.
- Dashboard com histórico de alertas.

---

## 🧠 Licença

Este projeto foi desenvolvido para fins acadêmicos e não possui licença de uso comercial.
