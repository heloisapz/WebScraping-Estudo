from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime, timedelta
import json

# --- PARTE 1: CONFIGURAÇÃO INICIAL ---
Url = "https://www.smiles.com.br/home"

navegador = webdriver.Chrome()
navegador.get(Url)
navegador.maximize_window()

wait = WebDriverWait(navegador, 20)  # Aumento do tempo de espera para 20 segundos

btn_aceitar = wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
btn_aceitar.click()

navegador.find_element(By.ID, 'drop_fligthType').click()
navegador.find_element(By.ID, 'opt_oneWay').click()

navegador.find_element(By.ID, 'inp_flightOrigin_1').click()
navegador.find_element(By.ID, 'opt_flight_2').click()

navegador.find_element(By.ID, 'inp_flightDestination_1').send_keys("MIA")
time.sleep(2)

# Escolher Miami
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

# --- PARTE 2: COLETA DE VOOS PARA OS PRÓXIMOS 10 DIAS ---
base_url = "https://www.smiles.com.br/mfe/emissao-passagem/?adults=1&cabin=ALL&children=0&departureDate={}&infants=0&isElegible=false&isFlexibleDateChecked=false&returnDate=&searchType=g3&segments=1&tripType=2&originAirport=GRU&originCity=&originCountry=&originAirportIsAny=false&destinationAirport=MIA&destinCity=&destinCountry=&destinAirportIsAny=false&novo-resultado-voos=true"

dados_voos = []

for i in range(10):
    proximoDia = datetime.now() + timedelta(days=i)
    timestamp_ms = int(proximoDia.timestamp() * 1000)
    url = base_url.format(timestamp_ms)
    print(f"\n[{proximoDia.strftime('%d/%m/%Y')}] → Acessando {url}")
    
    navegador.get(url)

    try:
        # Aguardar até a lista de voos estar carregada
        wait.until(EC.presence_of_all_elements_located((By.ID, 'header-content')))
        navegador.find_element(By.CLASS_NAME, 'select-flight-not-found')  # Verificar se não há voos
        print("Nenhum voo encontrado para este dia.")
        continue
    except NoSuchElementException:
        print("Voos encontrados!")
    except TimeoutException:
        print("Timeout esperando a lista de voos. Pulando dia.")
        continue

    # Clicar no botão "Mostrar mais passagens" até que todos os voos sejam carregados
    while True:
        try:
            botao_mais_passagens = WebDriverWait(navegador, 5).until(
                EC.element_to_be_clickable((By.ID, "SelectFlightList-ida-more"))
            )
            botao_mais_passagens.click()
            print("Botão 'Mostrar mais passagens' clicado")
            time.sleep(1)
        except TimeoutException:
            print("Todos os voos carregados para este dia")
            break

    voos = navegador.find_elements(By.CLASS_NAME, "header")
    print(f"Encontrados {len(voos)} voos.")
    
    for idx, voo in enumerate(voos, start=1):
        try:
            info = voo.find_element(By.CLASS_NAME, "info")

            companhia = info.find_element(By.CSS_SELECTOR, "p.company-and-seat > span.company").text
            classe = info.find_element(By.CSS_SELECTOR, "p.company-and-seat > span.seat").text

            horarios = info.find_elements(By.CLASS_NAME, "iata-code")
            horario_partida = horarios[0].text if len(horarios) > 0 else "Não informado"
            horario_chegada = horarios[1].text if len(horarios) > 1 else "Não informado"

            duracao = voo.find_element(By.CLASS_NAME, "scale-duration__time").text if voo.find_elements(By.CLASS_NAME, "scale-duration__time") else "Não informado"
            preco = voo.find_element(By.CLASS_NAME, "miles").text if voo.find_elements(By.CLASS_NAME, "miles") else "Não informado"

            data_voo = datetime.now() + timedelta(days=i)

            dados_voos.append({
                "dia_pesquisado": data_voo.strftime("%d/%m/%Y"),
                "companhia": companhia,
                "classe": classe,
                "horario_partida": horario_partida,
                "horario_chegada": horario_chegada,
                "duracao_voo": duracao,
                "preco": preco
            })

            # Exibir as informações no console
            print(f"""
                🚀 Voo encontrado:
                    ✈️ Companhia: {companhia}
                    💺 Classe: {classe}
                    🕓 Saída: {horario_partida}
                    🕖 Chegada: {horario_chegada}
                    ⏱️ Duração: {duracao}
                    💰 Valor: {preco}
                        """)

        except Exception as e:
            print(f"Erro ao capturar voo {idx}: {str(e)}")
            continue

# Salvar dados em arquivo JSON
with open("voos_smiles.json", "w", encoding='utf-8') as f:
    json.dump(dados_voos, f, ensure_ascii=False, indent=2)

print("\n✅ Dados salvos no arquivo 'voos_smiles.json'.")
navegador.quit()
