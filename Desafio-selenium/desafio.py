from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime, timedelta
import json

Url = "https://www.smiles.com.br/home"

navegador = webdriver.Chrome()
navegador.get(Url)
navegador.maximize_window()

wait = WebDriverWait(navegador, 20)

btnAceitar = wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
btnAceitar.click()

navegador.find_element(By.ID, 'drop_fligthType').click()
navegador.find_element(By.ID, 'opt_oneWay').click()

navegador.find_element(By.ID, 'inp_flightOrigin_1').click()
navegador.find_element(By.ID, 'opt_flight_2').click()

navegador.find_element(By.ID, 'inp_flightDestination_1').send_keys("MIA")
time.sleep(2)

lista = navegador.find_elements(By.CLASS_NAME, 'list-group-item')
for i in lista:
    if "Miami" in i.text:
        i.click()
        break

hoje = str(datetime.today().day)
dias = navegador.find_elements(By.CLASS_NAME, 'CalendarDay')
for dia in dias:
    if dia.text == hoje and dia.get_attribute('aria-disabled') == 'false':
        dia.click()
        break

navegador.find_element(By.ID, 'btn_search').click()
time.sleep(3)

try:
    navegador.find_element(By.ID, 'btn_sameDayInternational').click()
    time.sleep(2)
except NoSuchElementException:
    pass

baseUrl = "https://www.smiles.com.br/mfe/emissao-passagem/?adults=1&cabin=ALL&children=0&departureDate={}&infants=0&isElegible=false&isFlexibleDateChecked=false&returnDate=&searchType=g3&segments=1&tripType=2&originAirport=GRU&originCity=&originCountry=&originAirportIsAny=false&destinationAirport=MIA&destinCity=&destinCountry=&destinAirportIsAny=false&novo-resultado-voos=true"

dadosVoos = []

try:
    for i in range(10):
        proximoDia = datetime.now() + timedelta(days=i)
        timestamp_ms = int(proximoDia.timestamp() * 1000)
        url = baseUrl.format(timestamp_ms)
        print(f"\n[{proximoDia.strftime('%d/%m/%Y')}] → Acessando {url}")
        
        navegador.get(url)

        while True:
            try:
                btnMaisPassagens = WebDriverWait(navegador, 5).until(
                    EC.element_to_be_clickable((By.ID, "SelectFlightList-ida-more"))
                )
                btnMaisPassagens.click()
                print("Botão 'Mostrar mais passagens' clicado")
                time.sleep(1)
            except TimeoutException:
                print("Todos os voos carregados para este dia")
                break

        try:
            WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "header"))
            )
        except TimeoutException:
            print(f"Nenhum voo encontrado para {proximoDia.strftime('%d/%m/%Y')}")
            continue

        voos = navegador.find_elements(By.CLASS_NAME, "header")
        print(f"Encontrados {len(voos)} voos.")

        for idx, voo in enumerate(voos, start=1):
            try:
                info = voo.find_element(By.CLASS_NAME, "info")

                companhia = info.find_element(By.CSS_SELECTOR, "p.company-and-seat > span.company").text
                classe = info.find_element(By.CSS_SELECTOR, "p.company-and-seat > span.seat").text

                horarios = info.find_elements(By.CLASS_NAME, "iata-code")
                horaSaida = horarios[0].text if len(horarios) > 0 else "Não informado"
                horaChegada = horarios[1].text if len(horarios) > 1 else "Não informado"

                duracao_el = voo.find_elements(By.CLASS_NAME, "scale-duration__time")
                duracao = duracao_el[0].text if duracao_el else "Não informado"

                preco_el = voo.find_elements(By.CLASS_NAME, "miles")
                preco = preco_el[0].text if preco_el else "Não informado"

                dadosVoos.append({
                    "dia_pesquisado": proximoDia.strftime("%d/%m/%Y"),
                    "companhia": companhia,
                    "classe": classe,
                    "horaSaida": horaSaida,
                    "horaChegada": horaChegada,
                    "duracao_voo": duracao,
                    "preco": preco
                })

            except Exception as e:
                print(f"Erro ao capturar voo {idx}: {str(e)}")
                continue

    # Salvando os dados no arquivo JSON
    with open("voos_smiles.json", "w", encoding='utf-8') as f:
        json.dump(dadosVoos, f, ensure_ascii=False, indent=2)

    print("\n✅ Dados salvos no arquivo 'voos_smiles.json'.")

finally:
    navegador.quit()
