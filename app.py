import threading
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from bot import WhatsAppBot
from config import (
    MAX_GROUPS_PER_DAY,
    MAX_GROUPS_PER_SESSION,
    MAX_GROUPS_PER_TURN,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from usage import UsageTracker

ctk.set_appearance_mode("dark")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CEO - Automacao WhatsApp Enterprise")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color="#1A1A1D")

        self.lista_grupos: list = []
        self.acao_desejada = "false"
        self.tracker = UsageTracker()

        self._build_ui()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_header()
        self._build_action_selector()
        self._build_compliance_options()
        self._build_file_buttons()
        self._build_status_area()
        self._build_help_button()

    def _build_header(self) -> None:
        ctk.CTkLabel(
            self,
            text="GERENCIADOR DE GRUPOS",
            font=("Roboto", 26, "bold"),
            text_color="#FF8C00",
        ).pack(pady=20)

    def _build_action_selector(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=10)
        ctk.CTkLabel(frame, text="O que fazer com as mensagens?", font=("Roboto", 14)).pack()
        self.switch_acao = ctk.CTkSegmentedButton(
            frame,
            values=["Ativar", "Desativar"],
            command=self._set_acao,
            selected_color="#FF8C00",
        )
        self.switch_acao.set("Desativar")
        self.switch_acao.pack(pady=5)

    def _build_compliance_options(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=10)

        ctk.CTkLabel(frame, text="Turno (para auditoria e limite):", font=("Roboto", 13)).pack()
        self.turno_select = ctk.CTkSegmentedButton(
            frame, values=["Auto", "Manha", "Noite"], selected_color="#FF8C00"
        )
        self.turno_select.set("Auto")
        self.turno_select.pack(pady=5)

        self.confirmar_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            frame,
            text="Confirmar antes de iniciar (Modo Seguro)",
            variable=self.confirmar_var,
        ).pack(pady=5)

        self.reutilizar_sessao_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            frame,
            text="Reutilizar sessao do Chrome (Antidetect)",
            variable=self.reutilizar_sessao_var,
        ).pack(pady=5)

    def _build_file_buttons(self) -> None:
        ctk.CTkButton(
            self,
            text="BAIXAR MODELO EXCEL",
            command=self._baixar_modelo,
            fg_color="#FF8C00",
            hover_color="#E67E00",
            text_color="white",
            font=("Roboto", 14, "bold"),
        ).pack(pady=10)

        ctk.CTkButton(
            self,
            text="CARREGAR LISTA (EXCEL/CSV)",
            command=self._carregar_arquivo,
            fg_color="#007BFF",
            hover_color="#0056b3",
            font=("Roboto", 14, "bold"),
        ).pack(pady=10)

    def _build_status_area(self) -> None:
        self.status_label = ctk.CTkLabel(
            self,
            text="Aguardando importacao...",
            text_color="#CCCCCC",
            font=("Roboto", 13),
            wraplength=500,
        )
        self.status_label.pack(pady=20)

        self.progress_bar = ctk.CTkProgressBar(
            self, width=450, progress_color="#FF8C00", fg_color="#333333"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.btn_iniciar = ctk.CTkButton(
            self,
            text="INICIAR PROCESSAMENTO",
            command=self._start_thread,
            state="disabled",
            fg_color="#28a745",
            height=60,
            font=("Roboto", 18, "bold"),
        )
        self.btn_iniciar.pack(pady=20)

    def _build_help_button(self) -> None:
        ctk.CTkButton(
            self,
            text="? Ajuda",
            command=self._mostrar_ajuda,
            fg_color="#444444",
            hover_color="#FF8C00",
            text_color="white",
            font=("Roboto", 12, "bold"),
            width=80,
            height=30,
            corner_radius=8,
        ).place(x=508, y=12)

    # ------------------------------------------------------------------
    # Callbacks da UI
    # ------------------------------------------------------------------

    def _set_acao(self, value: str) -> None:
        self.acao_desejada = "true" if value == "Ativar" else "false"

    def _get_turno(self) -> str:
        selected = self.turno_select.get()
        if selected in ("Manha", "Noite"):
            return selected.lower()
        return "manha" if datetime.now().hour < 12 else "noite"

    def _set_status(self, text: str, color: str = "#CCCCCC") -> None:
        self.status_label.configure(text=text, text_color=color)

    def _set_progress(self, value: float) -> None:
        self.progress_bar.set(value)

    def _baixar_modelo(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", initialfile="modelo_whatsapp.xlsx"
        )
        if path:
            pd.DataFrame({"Nome do Grupo": ["[Exemplo] Grupo VIP", "Equipe Vendas"]}).to_excel(
                path, index=False
            )
            messagebox.showinfo("Sucesso", "Modelo criado!")

    def _carregar_arquivo(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Arquivos", "*.xlsx *.xls *.csv")])
        if not path:
            return
        try:
            df = pd.read_excel(path) if not path.endswith(".csv") else pd.read_csv(path)
            self.lista_grupos = [str(n).strip() for n in df["Nome do Grupo"].dropna().tolist()]
            self._set_status(f"{len(self.lista_grupos)} grupos prontos!", "#28a745")
            self.btn_iniciar.configure(state="normal")
        except Exception:
            messagebox.showerror("Erro", "Coluna 'Nome do Grupo' nao encontrada!")

    # ------------------------------------------------------------------
    # Controle de limites
    # ------------------------------------------------------------------

    def _prepare_session(self):
        usage = self.tracker.load()
        today = self.tracker.today_key()
        turno = self._get_turno()
        day_entry = self.tracker.get_day_entry(usage, today)

        used_total = int(day_entry.get("total", 0))
        used_turno = int(day_entry.get(turno, 0))
        remaining = min(MAX_GROUPS_PER_DAY - used_total, MAX_GROUPS_PER_TURN - used_turno)

        if remaining <= 0:
            self._set_status("Limite atingido para hoje/turno!", "#dc3545")
            messagebox.showwarning(
                "Limite",
                f"Hoje: {used_total}/{MAX_GROUPS_PER_DAY}\nTurno: {used_turno}/{MAX_GROUPS_PER_TURN}",
            )
            return None, usage, today, turno, day_entry

        limit = min(MAX_GROUPS_PER_SESSION, remaining, len(self.lista_grupos))
        grupos = self.lista_grupos[:limit]

        if self.confirmar_var.get():
            acao_txt = "ATIVAR" if self.acao_desejada == "true" else "DESATIVAR"
            ok = messagebox.askyesno(
                "Confirmar Lote",
                f"Acao: {acao_txt}\nGrupos: {limit}\nTurno: {turno}\n\nDeseja iniciar?",
            )
            if not ok:
                return None, usage, today, turno, day_entry

        return grupos, usage, today, turno, day_entry

    # ------------------------------------------------------------------
    # Execução do bot
    # ------------------------------------------------------------------

    def _start_thread(self) -> None:
        self.btn_iniciar.configure(state="disabled")
        threading.Thread(target=self._run_bot, daemon=True).start()

    def _run_bot(self) -> None:
        grupos, usage, today, turno, day_entry = self._prepare_session()
        if not grupos:
            self.btn_iniciar.configure(state="normal")
            return

        bot = WhatsAppBot(
            acao=self.acao_desejada,
            reutilizar_sessao=self.reutilizar_sessao_var.get(),
            on_status=self._set_status,
            on_progress=self._set_progress,
        )

        try:
            processed = bot.run(grupos)

            day_entry["total"] = int(day_entry.get("total", 0)) + processed
            day_entry[turno] = int(day_entry.get(turno, 0)) + processed
            usage[today] = day_entry
            self.tracker.save(usage)
            self.tracker.append_audit(
                {
                    "date": today,
                    "turno": turno,
                    "processed": processed,
                    "acao": self.acao_desejada,
                }
            )

            self._set_status("CONCLUIDO COM SUCESSO!", "#28a745")
            messagebox.showinfo(
                "Fim", f"Processados: {processed}\nTotal hoje: {day_entry['total']}"
            )
        except Exception as e:
            messagebox.showerror("Erro Critico", str(e))
        finally:
            self.btn_iniciar.configure(state="normal")

    # ------------------------------------------------------------------
    # Janela de ajuda
    # ------------------------------------------------------------------

    def _mostrar_ajuda(self) -> None:
        win = ctk.CTkToplevel(self)
        win.title("Ajuda - Passo a Passo")
        win.geometry("520x600")
        win.configure(fg_color="#1A1A1D")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="COMO USAR O SISTEMA",
            font=("Roboto", 18, "bold"),
            text_color="#FF8C00",
        ).pack(pady=(20, 10))

        passos = [
            (
                "1", "BAIXAR MODELO EXCEL",
                "Clique em 'Baixar Modelo Excel' e salve o arquivo.\n"
                "Ele contem a coluna obrigatoria: 'Nome do Grupo'.",
            ),
            (
                "2", "PREENCHER A LISTA",
                "Abra o arquivo Excel e preencha os nomes dos grupos\n"
                "exatamente como aparecem no WhatsApp (maiusculas,\n"
                "acentos e espacos incluidos).",
            ),
            (
                "3", "CARREGAR O ARQUIVO",
                "Clique em 'Carregar Lista (Excel/CSV)' e selecione\n"
                "o arquivo preenchido. O sistema exibira quantos grupos\n"
                "foram detectados.",
            ),
            (
                "4", "ESCOLHER A ACAO",
                "Selecione 'Ativar' para permitir mensagens nos grupos\n"
                "ou 'Desativar' para bloquear o envio de mensagens.",
            ),
            (
                "5", "CONFIGURAR O TURNO",
                "Escolha 'Auto' (detecta manha/noite automaticamente),\n"
                "'Manha' ou 'Noite'. Limite: 30 grupos por turno,\n"
                "60 grupos por dia.",
            ),
            (
                "6", "OPCOES DE SEGURANCA",
                "- Confirmar antes de iniciar: exibe resumo antes de rodar.\n"
                "- Reutilizar sessao: mantem o login do WhatsApp Web\n"
                "  salvo entre execucoes (recomendado).",
            ),
            (
                "7", "INICIAR O PROCESSAMENTO",
                "Clique em 'Iniciar Processamento'. O Chrome abrira\n"
                "automaticamente. Se for o primeiro uso, escaneie o\n"
                "QR Code do WhatsApp Web. O bot processara cada grupo\n"
                "com pausas humanas para evitar bloqueios.",
            ),
        ]

        frame = ctk.CTkScrollableFrame(win, fg_color="#242427", corner_radius=10)
        frame.pack(fill="both", expand=True, padx=15, pady=10)

        for num, titulo, desc in passos:
            row = ctk.CTkFrame(frame, fg_color="#2E2E32", corner_radius=8)
            row.pack(fill="x", padx=8, pady=5)

            ctk.CTkLabel(
                row, text=num, font=("Roboto", 20, "bold"), text_color="#FF8C00", width=36
            ).pack(side="left", padx=(10, 5), pady=10)

            col = ctk.CTkFrame(row, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True, pady=8)
            ctk.CTkLabel(
                col, text=titulo, font=("Roboto", 13, "bold"), text_color="#FFFFFF", anchor="w"
            ).pack(anchor="w")
            ctk.CTkLabel(
                col,
                text=desc,
                font=("Roboto", 11),
                text_color="#AAAAAA",
                anchor="w",
                justify="left",
                wraplength=400,
            ).pack(anchor="w")

        ctk.CTkButton(
            win,
            text="Fechar",
            command=win.destroy,
            fg_color="#FF8C00",
            hover_color="#E67E00",
            font=("Roboto", 13, "bold"),
            height=36,
        ).pack(pady=12)
