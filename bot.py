import os
import random
import time
from typing import Callable

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import CHROME_PROFILE_DIR, MAX_CONSECUTIVE_ERRORS


class WhatsAppBot:
    def __init__(
        self,
        acao: str,
        reutilizar_sessao: bool,
        on_status: Callable[[str, str], None],
        on_progress: Callable[[float], None],
    ):
        self.acao_desejada = acao  # "true" | "false"
        self.reutilizar_sessao = reutilizar_sessao
        self.on_status = on_status    # callback(texto, cor)
        self.on_progress = on_progress  # callback(0.0 – 1.0)

    # ------------------------------------------------------------------
    # Configuração do Chrome
    # ------------------------------------------------------------------

    def _setup_driver(self) -> webdriver.Chrome:
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        if self.reutilizar_sessao:
            profile_dir = os.path.abspath(CHROME_PROFILE_DIR)
            os.makedirs(profile_dir, exist_ok=True)
            options.add_argument(f"--user-data-dir={profile_dir}")
            options.add_argument("--profile-directory=Default")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )
        return driver

    # ------------------------------------------------------------------
    # Interação humana
    # ------------------------------------------------------------------

    def _type_humanlike(self, element, text: str) -> None:
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    # ------------------------------------------------------------------
    # Processamento de um grupo
    # ------------------------------------------------------------------

    def _process_group(
        self, driver: webdriver.Chrome, wait: WebDriverWait, nome: str
    ) -> None:
        # Pesquisa o grupo
        search_box = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            )
        )
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
        time.sleep(random.uniform(0.5, 1.0))

        self._type_humanlike(search_box, nome)
        time.sleep(random.uniform(1.5, 2.5))
        search_box.send_keys(Keys.ENTER)

        # Abre informações do grupo
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "header div[role='button']"))
        ).click()
        time.sleep(random.uniform(1.0, 1.5))

        # Navega até Permissões
        btn_per = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Permiss')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_per)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", btn_per)

        # Altera o switch "Enviar Mensagens"
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@role='switch']")))
        switches = driver.find_elements(By.XPATH, "//*[@role='switch']")

        if len(switches) >= 2:
            alvo = switches[1]
            if alvo.get_attribute("aria-checked") != self.acao_desejada:
                driver.execute_script("arguments[0].click();", alvo)
                time.sleep(random.uniform(1.0, 2.0))

        # Fecha o painel
        close_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[@aria-label='Voltar'] | //span[@data-icon='back'] | //div[@aria-label='Fechar']",
                )
            )
        )
        close_btn.click()

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def run(self, grupos: list) -> int:
        driver = self._setup_driver()
        wait = WebDriverWait(driver, 25)
        processed = 0
        consecutive_errors = 0

        try:
            driver.get("https://web.whatsapp.com")
            self.on_status("Escaneie o QR Code ou aguarde o login...", "#FF8C00")
            wait.until(EC.presence_of_element_located((By.ID, "pane-side")))

            self.on_status("Sincronizando (aguarde)...", "#FF8C00")
            time.sleep(random.randint(60, 80))

            for i, nome in enumerate(grupos, 1):
                if i > 1 and i % 10 == 0:
                    pausa = random.randint(120, 180)
                    self.on_status(f"Pausa de seguranca: {pausa}s", "#FF8C00")
                    time.sleep(pausa)

                self.on_status(f"{i}/{len(grupos)}: {nome}", "#007BFF")
                self.on_progress(i / len(grupos))

                try:
                    self._process_group(driver, wait, nome)
                    processed += 1
                    consecutive_errors = 0
                    time.sleep(random.uniform(4.0, 8.0))
                except Exception as e:
                    consecutive_errors += 1
                    if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                        raise RuntimeError(
                            f"Muitas falhas seguidas ({consecutive_errors}). Parando por seguranca."
                        ) from e
                    driver.get("https://web.whatsapp.com")
                    time.sleep(20)

        finally:
            driver.quit()

        return processed
