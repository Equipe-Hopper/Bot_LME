from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from time import sleep
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
import pandas as pd

def fechar_privacidade(driver: Driver):
    try:
        privacy_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
        )
        privacy_button.click()
        print("Banner de privacidade fechado.")
    except (NoSuchElementException, TimeoutException):
        print("Banner de privacidade não encontrado ou já fechado.")

def baixar_arquivos(driver: Driver):
    # download dos arquivos
    sleep(2)
    for n in range(1, 4):  
        try:
            download = driver.find_element(By.XPATH, f'/html/body/main/div/div[1]/div[1]/div[2]/div/p[{n}]/a')
            download.click()
            print(f"Arquivo {n} baixado com sucesso.")
            sleep(2)  
        except NoSuchElementException:
            print(f"Arquivo {n} não encontrado.")

def extrair_dados():
    data = []
    # caminho da pasta onde os arquivos foram baixados
    download_path = os.path.join(os.path.dirname(__file__), 'downloaded_files')

    lme_file = os.path.join(download_path, 'dados_lme.xlsx')
    if os.path.exists(lme_file):
        lme_data = pd.read_excel(lme_file)
        data.append(lme_data)

    # Lê apenas esses arquivos 
    expected_files = [
        "August 2024 No Steel  Molybdenum.xlsx",
        "July 2024 No Steel  Molybdenum.xlsx",
        "June 2024 No Steel  Molybdenum.xlsx"
    ]

    for file in expected_files:
        file_path = os.path.join(download_path, file)
        if os.path.exists(file_path):
            print(f"Lendo o arquivo: {file_path}")
            try:
                df = pd.read_excel(file_path)
                data.append(df)
            except Exception as e:
                print(f"Erro ao ler o arquivo {file}: {e}")

    # Combina os arquvios
    if data:
        combined_data = pd.concat(data, ignore_index=True)
        output_dir = os.path.join(os.path.dirname(__file__), 'dados_lme')
        os.makedirs(output_dir, exist_ok=True)
        combined_data.to_excel(os.path.join(output_dir, 'dados_combinados.xlsx'), index=False)
        print("Dados salvos com sucesso no arquivo 'dados_combinados.xlsx'.")
    else:
        print("Nenhum dado foi extraído.")

def navegar(driver: Driver):
    wait = WebDriverWait(driver, 20)

    # Login
    while True:
        try:
            email_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Email"]')))
            email_input.send_keys('falberto.dev@gmail.com')

            password_input = driver.find_element(By.XPATH, '//*[@id="Password"]')
            password_input.send_keys('Juniorg13?')

            break
        except NoSuchElementException:
            sleep(1)

    login_button = driver.find_element(By.XPATH, '/html/body/main/div/div[1]/div/form/div[3]/button')
    login_button.click()

    # Fechar o banner 
    fechar_privacidade(driver)

    # Espera o botão ficar clicável
    try:
        market_data = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="meganav-drawer"]/nav/ul/li[4]/button')))
        market_data.click()

        reports = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="meganav-drawer"]/nav/ul/li[4]/div/ul/li[3]/button/span')))
        reports.click()

        averages = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="meganav-drawer"]/nav/ul/li[4]/div/ul/li[3]/div/div[2]/ul/li[2]/a')))
        averages.click()
    except TimeoutException:
        print("O elemento não estava disponível.")

def main():
    driver = Driver(uc=True, headless=False)
    driver.get("https://www.lme.com/en/Account/Login")
    driver.maximize_window()

    # Navegar e baixar arquivos
    navegar(driver)
    baixar_arquivos(driver)

    # Extrair dados dos arquivos 
    extrair_dados()

    driver.quit()

if __name__ == '__main__':
    main()
