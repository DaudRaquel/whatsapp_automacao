# 💬 WhatsApp Automação — Selenium + Flask

> Bot de automação para WhatsApp Web com interface Flask. Controla grupos em lote, simula digitação humana para evitar detecção, suporta reutilização de sessão autenticada e execução com feedback de progresso em tempo real.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?logo=selenium&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![WhatsApp](https://img.shields.io/badge/WhatsApp_Web-automation-25D366?logo=whatsapp&logoColor=white)

---

## ✨ Funcionalidades

- **Automação de grupos** — operações em lote com lista de grupos configurável
- **Anti-detecção** — máscara de `navigator.webdriver`, user-agent real, CDP overrides
- **Digitação humanizada** — delay aleatório por caractere (50–150ms) para simular comportamento humano
- **Reutilização de sessão** — perfil Chrome persistido, evita QR Code a cada execução
- **Callbacks de progresso** — `on_status(texto, cor)` e `on_progress(0.0–1.0)` para feedback em tempo real
- **Tratamento de erros consecutivos** — para automaticamente após N falhas seguidas

## 🏗️ Fluxo

```
Flask UI
  │
  ▼
WhatsAppBot(acao, reutilizar_sessao, on_status, on_progress)
  │
  ├─▶ _setup_driver()     ── Chrome com anti-detecção
  ├─▶ WhatsApp Web login  ── reutiliza sessão salva (opcional)
  ├─▶ para cada grupo:
  │     _process_group()  ── busca, abre, executa ação
  │     _type_humanlike() ── digita simulando humano
  └─▶ on_progress(1.0)    ── notifica conclusão
```

## 🛠️ Stack

| Camada | Tecnologia |
|--------|-----------|
| Automação | Selenium 4 + WebDriver Manager |
| Interface | Flask (callbacks de progresso) |
| Anti-detecção | Chrome CDP + user-agent override |
| Configuração | python-dotenv |

## 📁 Estrutura

```
whatsapp_automacao/
├── bot.py          # Classe WhatsAppBot — core da automação
├── app.py          # Flask — interface e disparo do bot
├── main.py         # Entrypoint CLI
├── config.py       # Configurações via .env
├── usage.py        # Exemplos de uso
├── requirements.txt
└── .gitignore
```

## 🚀 Como rodar

```bash
pip install -r requirements.txt

# Via Flask (interface web):
python app.py

# Via CLI:
python main.py
```

> **Nota:** Na primeira execução, o Chrome abre para autenticação via QR Code. Com `reutilizar_sessao=True`, as execuções seguintes usam a sessão salva.

## ⚠️ Uso responsável

Este bot é para automação de processos internos legítimos. Respeite os [Termos de Uso do WhatsApp](https://www.whatsapp.com/legal/terms-of-service).

---
Desenvolvido por **Raquel Daud** — [LinkedIn](https://www.linkedin.com/in/raquel-daud-72a3991a2/) · [Portfolio](https://dauddev.netlify.app/)
