<div align="center">

# 📱  WhatsApp — Gerenciador de Grupos

**Automatize o controle de permissões em grupos do WhatsApp Web com segurança, limites e rastreabilidade.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.15%2B-green?style=for-the-badge&logo=selenium&logoColor=white)](https://selenium.dev/)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-orange?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge)](LICENSE)

</div>

---

## 🧩 O problema que resolvemos

Quem gerencia muitos grupos no WhatsApp sabe: **ativar ou desativar o envio de mensagens em cada grupo é um processo 100% manual** — entrar em cada grupo, ir em configurações, permissões, alterar o switch, voltar... e repetir isso para cada um dos grupos.

Com 30, 40 ou 60 grupos, isso tomava **horas de trabalho** repetitivo e sujeito a erros.

> **Solução:** uma interface simples que lê uma planilha com os nomes dos grupos e faz todo esse processo automaticamente, com pausas humanizadas, controle de limites diários e log de auditoria.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| ⚡ **Automação em lote** | Processa vários grupos em sequência a partir de uma planilha |
| 🔀 **Ativar / Desativar** | Alterna a permissão de envio de mensagens por membros |
| 🛡️ **Controle de limites** | Máximo de 30 grupos por turno e 60 por dia para evitar bloqueios |
| 📋 **Auditoria** | Cada sessão é registrada em arquivo `.jsonl` com data, turno e ação |
| 🌙 **Turnos (manhã/noite)** | Detecção automática ou seleção manual do turno de operação |
| 🔒 **Sessão persistente** | Login do WhatsApp Web salvo entre execuções (sem novo QR Code) |
| 🧠 **Comportamento humano** | Digitação caractere a caractere e pausas aleatórias entre ações |
| ✅ **Modo seguro** | Confirmação de lote antes de iniciar o processamento |

---

## 🗂️ Estrutura do projeto

```
📦 ceo-whatsapp-grupos
 ├── 📄 main.py           # Ponto de entrada da aplicação
 ├── 🖥️  app.py            # Interface gráfica (CustomTkinter)
 ├── 🤖 bot.py            # Automação via Selenium (WhatsApp Web)
 ├── 📊 usage.py          # Controle de limites e log de auditoria
 ├── ⚙️  config.py         # Constantes e configurações globais
 ├── 📋 requirements.txt  # Dependências Python
 ├── 🔨 build.bat         # Gera executável .exe com PyInstaller
 └── 🚫 .gitignore        # Exclui dados sensíveis do versionamento
```

---

## 🚀 Instalação e execução

### Pré-requisitos

- [Python 3.10+](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/) instalado

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/ceo-whatsapp-grupos.git
cd ceo-whatsapp-grupos

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute
python main.py
```

---

## 📖 Como usar

<details>
<summary><strong>1️⃣ Baixar o modelo de planilha</strong></summary>

Clique em **"Baixar Modelo Excel"** dentro da aplicação e salve o arquivo.
O modelo contém a coluna obrigatória: **`Nome do Grupo`**.

</details>

<details>
<summary><strong>2️⃣ Preencher a lista de grupos</strong></summary>

Abra o arquivo Excel e preencha os nomes dos grupos **exatamente como aparecem no WhatsApp** — incluindo maiúsculas, acentos e espaços.

</details>

<details>
<summary><strong>3️⃣ Carregar o arquivo</strong></summary>

Clique em **"Carregar Lista (Excel/CSV)"** e selecione o arquivo preenchido.
A aplicação exibirá quantos grupos foram detectados.

</details>

<details>
<summary><strong>4️⃣ Escolher a ação</strong></summary>

| Opção | Efeito |
|---|---|
| **Ativar** | Permite que membros enviem mensagens no grupo |
| **Desativar** | Bloqueia o envio de mensagens por membros |

</details>

<details>
<summary><strong>5️⃣ Configurar o turno e limites</strong></summary>

Escolha entre **Auto**, **Manhã** ou **Noite**.

| Limite | Valor padrão |
|---|---|
| Por sessão | 30 grupos |
| Por turno (manhã ou noite) | 30 grupos |
| Por dia | 60 grupos |

Os contadores são zerados automaticamente a cada novo dia.

</details>

<details>
<summary><strong>6️⃣ Iniciar o processamento</strong></summary>

Clique em **"Iniciar Processamento"**. O Chrome abrirá automaticamente.

- **Primeiro uso:** escaneie o QR Code do WhatsApp Web.
- **Usos seguintes:** com a opção "Reutilizar sessão" ativada, o login já estará salvo.

O bot processará cada grupo com pausas humanizadas para reduzir o risco de bloqueio.

</details>

---

## 📁 Arquivos gerados em tempo de execução

> Estes arquivos estão no `.gitignore` e nunca são enviados ao repositório.

| Arquivo | Descrição |
|---|---|
| `whatsapp_usage_log.json` | Contador de grupos processados por dia e turno |
| `whatsapp_audit_log.jsonl` | Histórico completo de sessões (data, turno, ação, quantidade) |
| `chrome-profile/` | Perfil do Chrome com sessão salva do WhatsApp Web |

---

## 🔨 Gerar executável (.exe)

Para distribuir sem precisar instalar Python:

```bash
build.bat
```

O executável `CEO_WhatsApp.exe` será gerado em `dist/`.

---

## ⚠️ Aviso legal

Este projeto automatiza interações com o WhatsApp Web.
O uso de automação pode estar em conflito com os [Termos de Serviço do WhatsApp](https://www.whatsapp.com/legal/terms-of-service).
**Use apenas em grupos que você administra e sob sua responsabilidade.**

---

<div align="center">

Feito com 🧡 para gestão de grupos no WhatsApp Web

</div>
