import time
import os
import django
from core.models import JobOffer, Responsibility, Requirement, Availability, Category, Mode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from django.core.management import call_command
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backtf.settings')
django.setup()


def extract_offers(base_url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)
    offers = []
    try:
        current_page = 1
        while True:
            url = f"{base_url}?page={current_page}"
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//a[@class="sc-ccSCjj dlMgrl"]')))
            except TimeoutException:
                print("No further elements were found, exiting the loop.")
                break
            elements = driver.find_elements(By.XPATH, '//a[@class="sc-ccSCjj dlMgrl"]')
            for element in elements:
                href_value = element.get_attribute("href")
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                try:
                    ActionChains(driver).move_to_element(element).click().perform()
                except Exception as e:
                    print(f"Error al hacer clic en el elemento: {e}")
                    continue
                WebDriverWait(driver, 15).until(EC.number_of_windows_to_be(2))
                driver.switch_to.window(driver.window_handles[1])
                wait = WebDriverWait(driver, 15)
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="ficha-detalle"]')))
                titulo_trabajo = driver.find_element(By.XPATH, "//div[@id='header-component']/div[1]/div[1]/h1[1]").text
                fecha = driver.find_element(By.XPATH, "//div[@id='ficha-detalle']/div[2]/div[1]/div[1]/div[1]/div["
                                                      "1]/div[1]/li[1]/h2[1]").text
                lugar_elementos = driver.find_elements(By.XPATH, "//div[@id='ficha-detalle']/div[2]/div[1]/div["
                                                                 "1]/div[1]/div[1]/div[1]/li[2]/a[1]/h2[1]")
                if lugar_elementos:
                    lugar = lugar_elementos[0].text
                else:
                    lugar_elementos = driver.find_elements(By.XPATH, "//div[@id='ficha-detalle']/div[2]/div[1]/div["
                                                                     "1]/div[1]/div[1]/div[1]/li[2]/span[1]/h2[1]")
                    if lugar_elementos:
                        lugar = lugar_elementos[0].text
                    else:
                        lugar = ""
                descripcion = ' '.join([valor.text for valor in driver.find_elements(By.XPATH,
                                                                                     "//div[@id='ficha-detalle']/div["
                                                                                     "2]/div[1]/div[1]/p")])
                tareas = ' '.join([valor.text for valor in driver.find_elements(By.XPATH,
                                                                                "//div[@id='ficha-detalle']/div["
                                                                                "2]/div[1]/div[1]/ul[1]")])
                requisitos = ' '.join([valor.text for valor in driver.find_elements(By.XPATH,
                                                                                    "//div[@id='ficha-detalle']/div["
                                                                                    "2]/div[1]/div[1]/ul[2]")])
                modalidad_publicacion_elementos = driver.find_elements(By.XPATH,
                                                                       "//div[@id='ficha-detalle']/div[2]/div[1]/div["
                                                                       "1]/div[3]/div[1]/ul[1]/div[1]/li[1]/a[1]/h2["
                                                                       "1]")
                if modalidad_publicacion_elementos:
                    modalidad_publicacion = modalidad_publicacion_elementos[0].text
                else:
                    modalidad_publicacion = ""
                rubro_publicacion_elementos = driver.find_elements(By.XPATH,
                                                                   "//div[@id='ficha-detalle']/div[2]/div[1]/div["
                                                                   "1]/div[3]/div[1]/ul[1]/div[1]/li[2]/a[1]/h2[1]")
                if rubro_publicacion_elementos:
                    rubro_publicacion = rubro_publicacion_elementos[0].text
                else:
                    rubro_publicacion = ""
                disponibilidad_publicacion_elementos = driver.find_elements(By.XPATH,
                                                                            "//div[@id='ficha-detalle']/div[2]/div["
                                                                            "1]/div[1]/div[3]/div[1]/ul[1]/div[1]/li["
                                                                            "3]/h2[1]")
                if disponibilidad_publicacion_elementos:
                    disponibilidad_publicacion = disponibilidad_publicacion_elementos[0].text
                else:
                    disponibilidad_publicacion = ""
                empresa_elementos = driver.find_elements(By.XPATH,
                                                         "//div[@id='header-component']/div[1]/div[1]/div[1]/a[1]/div["
                                                         "1]/div[1] | //div[@id='header-component']/div[1]/div[1]/div["
                                                         "1]/span[1]/div[1]/div[1] | //div[@id='header-component']/div["
                                                         "1]/div[1]/div[1]/h3[1]")
                if empresa_elementos:
                    empresa = empresa_elementos[0].text
                else:
                    empresa = ""

                oferta = {
                    "titulo_empleo": titulo_trabajo,
                    "fecha": fecha,
                    "lugar": lugar,
                    "description": descripcion,
                    "tareas": tareas,
                    "requisitos": requisitos,
                    "disponibilidad": disponibilidad_publicacion,
                    "rubro": rubro_publicacion,
                    "modalidad": modalidad_publicacion,
                    "empresa": empresa,
                    "link": href_value
                }
                for oferta_existente in offers:
                    if oferta_existente["titulo_empleo"].lower() == oferta["titulo_empleo"].lower() and \
                            oferta_existente["empresa"] == oferta["empresa"] and \
                            oferta_existente["description"] == oferta["description"]:
                        break
                else:
                    offers.append(oferta)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            current_page += 1
    finally:
        driver.quit()
    print('successful extraction')
    return offers


def save_offers(data):
    json_data = data
    for data in json_data:
        category, _ = Category.objects.get_or_create(name=data['rubro'])
        mode, _ = Mode.objects.get_or_create(name=data['modalidad'])
        job_offer = JobOffer(
            title=data['titulo_empleo'],
            description=data['description'],
            location=data['lugar'],
            company=data['empresa'],
            date_publication=data['fecha'],
            link=data['link'],
            category=category,
            mode=mode,
        )
        job_offer.save()
        responsibilities = data['tareas'].split('\n')
        for responsibility in responsibilities:
            Responsibility(description=responsibility, job_offer=job_offer).save()
        requirements = data['requisitos'].split('\n')
        for requirement in requirements:
            Requirement(description=requirement, job_offer=job_offer).save()
        Availability(description=data['disponibilidad'], job_offer=job_offer).save()
    print('Offers successfully saved')


def load_data():
    base_url = "https://www.zonajobs.com.ar/en-jujuy/empleos.html"
    call_command('clear_db')
    offers = extract_offers(base_url)
    save_offers(offers)

# while True:
#    load_data()
#    time.sleep(300) 5 minutes
#    time.sleep(12 * 60 * 60) 12 horas
