# CEO WhatsApp — Gerenciador de Grupos

Ferramenta desktop para **ativar ou desativar o envio de mensagens** em grupos do WhatsApp Web de forma automatizada, com controle de limites diários, auditoria de ações e proteção antidetecção.

---

## Funcionalidades

- Ativa ou desativa o envio de mensagens em lotes de grupos via WhatsApp Web
- Importa a lista de grupos a partir de planilha `.xlsx` ou `.csv`
- Controle de limites por turno (manhã/noite) e por dia
- Log de auditoria em arquivo `.jsonl` para rastreabilidade
- Sessão persistente do Chrome (evita novo QR Code a cada execução)
- Pausas humanizadas entre ações para reduzir risco de bloqueio
- Interface gráfica moderna com tema escuro

---

## Estrutura do projeto

```
├── main.py          # Ponto de entrada
├── app.py           # Interface gráfica (customtkinter)
├── bot.py           # Automação via Selenium
├── usage.py         # Controle de limites e log de auditoria
├── config.py        # Constantes e configurações
├── requirements.txt # Dependências Python
├── build.bat        # Gera executável .exe com PyInstaller
└── .gitignore
```

---

## Pré-requisitos

- Python 3.10 ou superior
- Google Chrome instalado

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo

# Instale as dependências
pip install -r requirements.txt
```

---

## Como usar

### 1. Execute a aplicação

```bash
python main.py
```

### 2. Prepare a planilha

Clique em **Baixar Modelo Excel** para obter o modelo com a coluna `Nome do Grupo`.
Preencha os nomes exatamente como aparecem no WhatsApp (maiúsculas, acentos e espaços incluídos).

### 3. Carregue a lista

Clique em **Carregar Lista (Excel/CSV)** e selecione o arquivo preenchido.

### 4. Escolha a ação

| Opção | Efeito |
|-------|--------|
| **Ativar** | Permite que membros enviem mensagens no grupo |
| **Desativar** | Bloqueia o envio de mensagens por membros |

### 5. Configure o turno

- **Auto** — detecta manhã (antes das 12h) ou noite automaticamente
- **Manha / Noite** — força o turno manualmente

Limites aplicados:

| Limite | Valor padrão |
|--------|-------------|
| Por sessão | 30 grupos |
| Por turno | 30 grupos |
| Por dia | 60 grupos |

### 6. Inicie o processamento

Clique em **Iniciar Processamento**. O Chrome abrirá automaticamente.
Na primeira execução, escaneie o QR Code do WhatsApp Web.
Com a opção **Reutilizar sessão** ativada, o login fica salvo para as próximas execuções.

---

## Gerar executável (.exe)

```bash
build.bat
```

O arquivo `CEO_WhatsApp.exe` será gerado na pasta `dist/`.

---

## Arquivos gerados em tempo de execução

| Arquivo | Descrição |
|---------|-----------|
| `whatsapp_usage_log.json` | Contador de grupos processados por dia/turno |
| `whatsapp_audit_log.jsonl` | Histórico completo de sessões (data, turno, ação, quantidade) |
| `chrome-profile/` | Perfil do Chrome com sessão salva do WhatsApp Web |

> Esses arquivos estão no `.gitignore` e não são versionados.

---

## Aviso

Este projeto automatiza interações no WhatsApp Web.
O uso de automação pode estar em conflito com os [Termos de Serviço do WhatsApp](https://www.whatsapp.com/legal/terms-of-service).
Use com responsabilidade e apenas em grupos que você administra.
