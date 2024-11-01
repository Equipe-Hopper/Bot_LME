from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from time import sleep
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
import pandas as pd
# from botcity.web import WebBot, Browser, By
from botcity.maestro import *

BotMaestroSDK.RAISE_NOT_CONNECTED = False

class LmeScraper:
    def __init__(self, headless=False):
        self.driver = Driver(uc=True, headless=headless)
        self.wait = WebDriverWait(self.driver, 20)
        self.download_path = os.path.join(os.path.dirname(__file__), 'downloaded_files')

    def iniciar_navegador(self, url):
        self.driver.get(url)
        self.driver.maximize_window()

    def fechar_privacidade(self):
        try:
            privacy_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
            )
            privacy_button.click()
            print("Banner de privacidade fechado.")
        except (NoSuchElementException, TimeoutException):
            print("Banner de privacidade não encontrado ou já fechado.")

    def fazer_login(self, email, senha):
    # Fecha o banner de privacidade antes de tentar clicar no botão de login
        self.fechar_privacidade()
        
        while True:
            try:
                email_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Email"]')))
                email_input.send_keys(email)

                password_input = self.driver.find_element(By.XPATH, '//*[@id="Password"]')
                password_input.send_keys(senha)

                # Verifica se o botão de login está clicável e clica
                login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div/div[1]/div/form/div[3]/button')))
                login_button.click()
                break
            # except ElementClickInterceptedException:
            #     # Tenta fechar o banner novamente se o clique for interceptado
            #     print("Tentando fechar o banner de privacidade novamente.")
            #     self.fechar_privacidade()
            except NoSuchElementException:
                print("Tentando fechar o banner de privacidade novamente.")
                self.fechar_privacidade()
                sleep(1)

    def navegar_para_relatorios(self):
        try:
            market_data = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="meganav-drawer"]/nav/ul/li[4]/button')))
            market_data.click()

            reports = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="meganav-drawer"]/nav/ul/li[4]/div/ul/li[3]/button/span')))
            reports.click()

            averages = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="meganav-drawer"]/nav/ul/li[4]/div/ul/li[3]/div/div[2]/ul/li[2]/a')))
            averages.click()
        except TimeoutException:
            print("O elemento não estava disponível.")

    def baixar_arquivos(self):
        sleep(2)
        for n in range(1, 4):
            try:
                download = self.driver.find_element(By.XPATH, f'/html/body/main/div/div[1]/div[1]/div[2]/div/p[{n}]/a')
                download.click()
                print(f"Arquivo {n} baixado com sucesso.")
                sleep(2)
            except NoSuchElementException:
                print(f"Arquivo {n} não encontrado.")

    def extrair_dados(self):
        data = []

        lme_file = os.path.join(self.download_path, 'dados_lme.xlsx')
        if os.path.exists(lme_file):
            lme_data = pd.read_excel(lme_file)
            data.append(lme_data)

        expected_files = [
            "August 2024 No Steel  Molybdenum.xlsx",
            "July 2024 No Steel  Molybdenum.xlsx",
            "June 2024 No Steel  Molybdenum.xlsx"
        ]

        for file in expected_files:
            file_path = os.path.join(self.download_path, file)
            if os.path.exists(file_path):
                print(f"Lendo o arquivo: {file_path}")
                try:
                    df = pd.read_excel(file_path)
                    data.append(df)
                except Exception as e:
                    print(f"Erro ao ler o arquivo {file}: {e}")

        if data:
            combined_data = pd.concat(data, ignore_index=True)
            output_dir = os.path.join(os.path.dirname(__file__), 'dados_lme')
            os.makedirs(output_dir, exist_ok=True)
            combined_data.to_excel(os.path.join(output_dir, 'dados_combinados.xlsx'), index=False)
            print("Dados salvos com sucesso no arquivo 'dados_combinados.xlsx'.")
        else:
            print("Nenhum dado foi extraído.")

    def run(self, url, email, senha, execution = None):

        maestro = BotMaestroSDK.from_sys_args()
        execution = maestro.get_execution()
        print(f"Task ID is: {execution.task_id}")
        print(f"Task Parameters are: {execution.parameters}")
        
        

        try:
            maestro.alert(
            task_id=execution.task_id,
            title="Iniciando Automação",
            message="O processo de navegação e extração começou",
            alert_type=AlertType.INFO
        )
            
            self.iniciar_navegador(url)
            self.fazer_login(email, senha)
            self.fechar_privacidade()
            self.navegar_para_relatorios()
            self.baixar_arquivos()
            self.extrair_dados()

                      
            finshed_status = AutomationTaskFinishStatus.SUCCESS
            finish_message = "Tarefa finalizada com sucesso"

        except Exception as ex:
            print("Error: ", ex)
            self.save_screenshot("erro.png")

            finshed_status = AutomationTaskFinishStatus.FAILED
            finish_message = "Tarefa finalizada com erro"

        finally:
            sleep(3)
            self.driver.quit()

            maestro.finish_task(
                task_id=execution.task_id,
                status=AutomationTaskFinishStatus.SUCCESS,
                message="Task Finalizada com sucesso."
            )

if __name__ == '__main__':
    scraper = LmeScraper(headless=False)
    scraper.run("https://www.lme.com/en/Account/Login", "falberto.dev@gmail.com", "Juniorg13?")
