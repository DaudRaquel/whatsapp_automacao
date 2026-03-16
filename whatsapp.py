import customtkinter as ctk
import json
import os
import threading
import time
import random
from datetime import datetime
from tkinter import filedialog, messagebox

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

ctk.set_appearance_mode("dark")

# CONFIGURAÇÕES DE LIMITES E SEGURANÇA
USAGE_LOG_FILE = "whatsapp_usage_log.json"
AUDIT_LOG_FILE = "whatsapp_audit_log.jsonl"
CHROME_PROFILE_DIR = "chrome-profile"
MAX_GROUPS_PER_SESSION = 30
MAX_GROUPS_PER_DAY = 60
MAX_GROUPS_PER_TURN = 30
MAX_CONSECUTIVE_ERRORS = 3

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CEO - Automação WhatsApp Enterprise")
        self.geometry("600x720")
        self.configure(fg_color="#1A1A1D")

        # UI - Título
        self.label = ctk.CTkLabel(self, text="GERENCIADOR DE GRUPOS", font=("Roboto", 26, "bold"), text_color="#FF8C00")
        self.label.pack(pady=20)

        # UI - Seletor de Ação
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=10)
        self.label_acao = ctk.CTkLabel(self.action_frame, text="O que fazer com as mensagens?", font=("Roboto", 14))
        self.label_acao.pack()
        self.switch_acao = ctk.CTkSegmentedButton(self.action_frame, values=["Ativar", "Desativar"],
                                                 command=self.set_acao, selected_color="#FF8C00")
        self.switch_acao.set("Desativar")
        self.switch_acao.pack(pady=5)

        # UI - Compliance e Turnos
        self.compliance_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.compliance_frame.pack(pady=10)
        self.label_turno = ctk.CTkLabel(self.compliance_frame, text="Turno (para auditoria e limite):", font=("Roboto", 13))
        self.label_turno.pack()
        self.turno_select = ctk.CTkSegmentedButton(self.compliance_frame, values=["Auto", "Manha", "Noite"], selected_color="#FF8C00")
        self.turno_select.set("Auto")
        self.turno_select.pack(pady=5)

        self.confirmar_var = ctk.BooleanVar(value=True)
        self.chk_confirmar = ctk.CTkCheckBox(self.compliance_frame, text="Confirmar antes de iniciar (Modo Seguro)", variable=self.confirmar_var)
        self.chk_confirmar.pack(pady=5)

        self.reutilizar_sessao_var = ctk.BooleanVar(value=True)
        self.chk_reutilizar_sessao = ctk.CTkCheckBox(self.compliance_frame, text="Reutilizar sessão do Chrome (Antidetect)", variable=self.reutilizar_sessao_var)
        self.chk_reutilizar_sessao.pack(pady=5)

        # UI - Botões de Arquivo
        self.btn_modelo = ctk.CTkButton(self, text="BAIXAR MODELO EXCEL", command=self.baixar_modelo, 
                                        fg_color="#FF8C00", hover_color="#E67E00", text_color="white", font=("Roboto", 14, "bold"))
        self.btn_modelo.pack(pady=10)

        self.btn_carregar = ctk.CTkButton(self, text="CARREGAR LISTA (EXCEL/CSV)", command=self.carregar_arquivo,
                                          fg_color="#007BFF", hover_color="#0056b3", font=("Roboto", 14, "bold"))
        self.btn_carregar.pack(pady=10)

        # UI - Status e Progresso
        self.status_label = ctk.CTkLabel(self, text="Aguardando importação...", text_color="#CCCCCC", font=("Roboto", 13), wraplength=500)
        self.status_label.pack(pady=20)

        self.progress_bar = ctk.CTkProgressBar(self, width=450, progress_color="#FF8C00", fg_color="#333333")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.btn_iniciar = ctk.CTkButton(self, text="INICIAR PROCESSAMENTO", command=self.start_thread,
                                         state="disabled", fg_color="#28a745", height=60, font=("Roboto", 18, "bold"))
        self.btn_iniciar.pack(pady=20)

        # UI - Botão Ajuda (canto superior direito)
        self.btn_ajuda = ctk.CTkButton(self, text="? Ajuda", command=self.mostrar_ajuda,
                                       fg_color="#444444", hover_color="#FF8C00",
                                       text_color="white", font=("Roboto", 12, "bold"),
                                       width=80, height=30, corner_radius=8)
        self.btn_ajuda.place(x=508, y=12)

        self.lista_grupos = []
        self.acao_desejada = "false"
        self.consecutive_errors = 0

    # --- AJUDA ---
    def mostrar_ajuda(self):
        win = ctk.CTkToplevel(self)
        win.title("Ajuda - Passo a Passo")
        win.geometry("520x600")
        win.configure(fg_color="#1A1A1D")
        win.grab_set()

        ctk.CTkLabel(win, text="COMO USAR O SISTEMA", font=("Roboto", 18, "bold"),
                     text_color="#FF8C00").pack(pady=(20, 10))

        passos = [
            ("1", "BAIXAR MODELO EXCEL",
             "Clique em 'Baixar Modelo Excel' e salve o arquivo.\n"
             "Ele contém a coluna obrigatória: 'Nome do Grupo'."),
            ("2", "PREENCHER A LISTA",
             "Abra o arquivo Excel e preencha os nomes dos grupos\n"
             "exatamente como aparecem no WhatsApp (maiúsculas,\n"
             "acentos e espaços incluídos)."),
            ("3", "CARREGAR O ARQUIVO",
             "Clique em 'Carregar Lista (Excel/CSV)' e selecione\n"
             "o arquivo preenchido. O sistema exibirá quantos grupos\n"
             "foram detectados."),
            ("4", "ESCOLHER A AÇÃO",
             "Selecione 'Ativar' para permitir mensagens nos grupos\n"
             "ou 'Desativar' para bloquear o envio de mensagens."),
            ("5", "CONFIGURAR O TURNO",
             "Escolha 'Auto' (detecta manhã/noite automaticamente),\n"
             "'Manha' ou 'Noite'. Limite: 30 grupos por turno,\n"
             "60 grupos por dia."),
            ("6", "OPCOES DE SEGURANÇA",
             "• Confirmar antes de iniciar: exibe resumo antes de rodar.\n"
             "• Reutilizar sessão: mantém o login do WhatsApp Web\n"
             "  salvo entre execuções (recomendado)."),
            ("7", "INICIAR O PROCESSAMENTO",
             "Clique em 'Iniciar Processamento'. O Chrome abrirá\n"
             "automaticamente. Se for o primeiro uso, escaneie o\n"
             "QR Code do WhatsApp Web. O bot processará cada grupo\n"
             "com pausas humanas para evitar bloqueios."),
        ]

        frame = ctk.CTkScrollableFrame(win, fg_color="#242427", corner_radius=10)
        frame.pack(fill="both", expand=True, padx=15, pady=10)

        for num, titulo, desc in passos:
            row = ctk.CTkFrame(frame, fg_color="#2E2E32", corner_radius=8)
            row.pack(fill="x", padx=8, pady=5)

            ctk.CTkLabel(row, text=num, font=("Roboto", 20, "bold"),
                         text_color="#FF8C00", width=36).pack(side="left", padx=(10, 5), pady=10)

            col = ctk.CTkFrame(row, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True, pady=8)
            ctk.CTkLabel(col, text=titulo, font=("Roboto", 13, "bold"),
                         text_color="#FFFFFF", anchor="w").pack(anchor="w")
            ctk.CTkLabel(col, text=desc, font=("Roboto", 11),
                         text_color="#AAAAAA", anchor="w", justify="left", wraplength=400).pack(anchor="w")

        ctk.CTkButton(win, text="Fechar", command=win.destroy,
                      fg_color="#FF8C00", hover_color="#E67E00",
                      font=("Roboto", 13, "bold"), height=36).pack(pady=12)

    # --- FUNÇÕES DE APOIO ---
    def set_acao(self, value):
        self.acao_desejada = "true" if value == "Ativar" else "false"

    def _now_iso(self):
        return datetime.now().isoformat(timespec="seconds")

    def _get_turno(self):
        selected = self.turno_select.get()
        if selected in ("Manha", "Noite"): return selected.lower()
        return "manha" if datetime.now().hour < 12 else "noite"

    def _append_audit(self, record):
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=True) + "\n")
        except: pass

    def _today_key(self):
        return datetime.now().strftime("%Y-%m-%d")

    def _load_usage(self):
        if not os.path.exists(USAGE_LOG_FILE): return {}
        try:
            with open(USAGE_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}

    def _save_usage(self, usage):
        with open(USAGE_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(usage, f, ensure_ascii=True, indent=2)

    def baixar_modelo(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile="modelo_whatsapp.xlsx")
        if path:
            pd.DataFrame({"Nome do Grupo": ["[Exemplo] Grupo VIP", "Equipe Vendas"]}).to_excel(path, index=False)
            messagebox.showinfo("Sucesso", "Modelo criado!")

    def carregar_arquivo(self):
        path = filedialog.askopenfilename(filetypes=[("Arquivos", "*.xlsx *.xls *.csv")])
        if not path: return
        try:
            df = pd.read_excel(path) if not path.endswith(".csv") else pd.read_csv(path)
            self.lista_grupos = [str(n).strip() for n in df["Nome do Grupo"].dropna().tolist()]
            self.status_label.configure(text=f"{len(self.lista_grupos)} grupos prontos!", text_color="#28a745")
            self.btn_iniciar.configure(state="normal")
        except:
            messagebox.showerror("Erro", "Coluna 'Nome do Grupo' não encontrada!")

    def start_thread(self):
        self.btn_iniciar.configure(state="disabled")
        threading.Thread(target=self.rodar_bot, daemon=True).start()

    def _prepare_session_groups(self):
        usage = self._load_usage()
        today = self._today_key()
        turno = self._get_turno()
        day_entry = usage.get(today, {"total": 0, "manha": 0, "noite": 0})
        if isinstance(day_entry, int): day_entry = {"total": day_entry, "manha": 0, "noite": 0}

        used_total = int(day_entry.get("total", 0))
        used_turno = int(day_entry.get(turno, 0))
        remaining = min(MAX_GROUPS_PER_DAY - used_total, MAX_GROUPS_PER_TURN - used_turno)

        if remaining <= 0:
            self.status_label.configure(text="Limite atingido para hoje/turno!", text_color="#dc3545")
            messagebox.showwarning("Limite", f"Hoje: {used_total}/{MAX_GROUPS_PER_DAY}\nTurno: {used_turno}/{MAX_GROUPS_PER_TURN}")
            return [], usage, today, turno, day_entry

        limit = min(MAX_GROUPS_PER_SESSION, remaining, len(self.lista_grupos))
        grupos = self.lista_grupos[:limit]

        if self.confirmar_var.get():
            acao_txt = "ATIVAR" if self.acao_desejada == "true" else "DESATIVAR"
            ok = messagebox.askyesno("Confirmar Lote", f"Ação: {acao_txt}\nGrupos: {limit}\nTurno: {turno}\n\nDeseja iniciar?")
            if not ok: return [], usage, today, turno, day_entry

        return grupos, usage, today, turno, day_entry

    # --- MOTOR PRINCIPAL ---
    def rodar_bot(self):
        grupos_para_rodar, usage, today, turno, day_entry = self._prepare_session_groups()
        if not grupos_para_rodar:
            self.btn_iniciar.configure(state="normal")
            return

        # Configurações Antidetect
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        if self.reutilizar_sessao_var.get():
            profile_dir = os.path.abspath(CHROME_PROFILE_DIR)
            os.makedirs(profile_dir, exist_ok=True)
            options.add_argument(f"--user-data-dir={profile_dir}")
            options.add_argument("--profile-directory=Default")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Oculta navigator.webdriver
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        wait = WebDriverWait(driver, 25)
        processed_in_session = 0
        acao_txt = "ativar" if self.acao_desejada == "true" else "desativar"

        try:
            driver.get("https://web.whatsapp.com")
            self.status_label.configure(text="🛰️ Escaneie o QR Code ou aguarde o login...", text_color="#FF8C00")
            wait.until(EC.presence_of_element_located((By.ID, "pane-side")))
            
            self.status_label.configure(text="⏳ Sincronização inicial (Segura)...", text_color="#FF8C00")
            time.sleep(random.randint(60, 80))

            for i, nome in enumerate(grupos_para_rodar, 1):
                # Pausas humanas extras
                if i > 1 and i % 10 == 0:
                    pausa = random.randint(120, 180)
                    self.status_label.configure(text=f"☕ Pausa de segurança: {pausa}s", text_color="#FF8C00")
                    time.sleep(pausa)

                self.status_label.configure(text=f"🔄 {i}/{len(grupos_para_rodar)}: {nome}", text_color="#007BFF")
                self.progress_bar.set(i / len(grupos_para_rodar))

                try:
                    # Busca Humana
                    search_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
                    search_box.click()
                    search_box.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    for char in nome:
                        search_box.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    
                    time.sleep(random.uniform(1.5, 2.5))
                    search_box.send_keys(Keys.ENTER)

                    # Navegação
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "header div[role='button']"))).click()
                    time.sleep(random.uniform(1.0, 1.5))

                    btn_per = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Permiss')]")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_per)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn_per)

                    # Troca do Switch (Enviar Mensagens)
                    wait.until(EC.presence_of_element_located((By.XPATH, "//*[@role='switch']")))
                    switches = driver.find_elements(By.XPATH, "//*[@role='switch']")
                    
                    if len(switches) >= 2:
                        alvo = switches[1]
                        if alvo.get_attribute("aria-checked") != self.acao_desejada:
                            driver.execute_script("arguments[0].click();", alvo)
                            time.sleep(random.uniform(1.0, 2.0))

                    # Fecha abas
                    close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Voltar'] | //span[@data-icon='back'] | //div[@aria-label='Fechar']")))
                    close_btn.click()
                    
                    processed_in_session += 1
                    self.consecutive_errors = 0
                    time.sleep(random.uniform(4.0, 8.0)) # Intervalo entre grupos

                except Exception as e:
                    self.consecutive_errors += 1
                    if self.consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                        raise Exception("Muitas falhas seguidas. Parando por segurança.")
                    driver.get("https://web.whatsapp.com")
                    time.sleep(20)

            # Salva progresso
            day_entry["total"] = int(day_entry.get("total", 0)) + processed_in_session
            day_entry[turno] = int(day_entry.get(turno, 0)) + processed_in_session
            usage[today] = day_entry
            self._save_usage(usage)
            
            self.status_label.configure(text="🏁 CONCLUÍDO COM SUCESSO!", text_color="#28a745")
            messagebox.showinfo("Fim", f"Processados: {processed_in_session}\nTotal hoje: {day_entry['total']}")

        except Exception as e:
            messagebox.showerror("Erro Crítico", str(e))
        finally:
            self.btn_iniciar.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()