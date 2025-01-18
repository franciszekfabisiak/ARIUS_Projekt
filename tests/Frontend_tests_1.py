from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

def wait_for_element(by, value, timeout=10):
    """Funkcja czeka na element przez określony czas"""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def handle_alert():
    """Funkcja obsługująca alert"""
    try:
        alert = Alert(driver)
        alert_text = alert.text
        print("Alert Text:", alert_text)
        alert.accept() 
        print("Alert closed")
    except Exception as e:
        print(f"An error occurred while handling alert: {e}")

try:
    driver.get("http://localhost:3000") 
    driver.maximize_window()


# Rejestracja użytkownika

    register_button = wait_for_element(By.ID, "register-modal")
    register_button.click()

    wait_for_element(By.XPATH, "//input[@placeholder='Username']").send_keys("Adam320")

# !!!!!!!!!!!!! Aby otrzymać maila należy podać odpowiedni email
    wait_for_element(By.XPATH, "//input[@placeholder='Email']").send_keys("test@test.test")
    wait_for_element(By.XPATH, "//input[@placeholder='Password']").send_keys("Adam023")
    wait_for_element(By.XPATH, "//input[@placeholder='Name']").send_keys("Adam")
    wait_for_element(By.XPATH, "//input[@placeholder='Surname']").send_keys("Kowalski")
    wait_for_element(By.XPATH, "//input[@placeholder='Phone number']").send_keys("123456789")

    register_submit_button = wait_for_element(By.ID, "register-submit")
    register_submit_button.click()
    time.sleep(2)

    close_button = wait_for_element(By.XPATH, "//button[text()='Close']")
    close_button.click()

# Logowanie użytkownika

    login_modal_button = wait_for_element(By.ID, "login-modal")
    login_modal_button.click()

    wait_for_element(By.XPATH, "//input[@placeholder='Username']").send_keys("Adam320")
    wait_for_element(By.XPATH, "//input[@placeholder='Password']").send_keys("Adam023")
    time.sleep(1)

    login_submit_button = wait_for_element(By.ID, "login-submit")
    login_submit_button.click()
    time.sleep(3)

    handle_alert()
    wait_for_element(By.CLASS_NAME, "pizzas-container")
    time.sleep(3)

# Obejrzenie danych użytkownika

    account_button = wait_for_element(By.ID, "account-modal")
    account_button.click()
    time.sleep(3)

# Powrót do strony głównej

    account_button = wait_for_element(By.ID, "pizzas-modal")
    account_button.click()
    time.sleep(3)

# Dodawanie pizz do koszyka

    pizza_card = wait_for_element(By.XPATH, "//div[contains(@class, 'pizza-card') and .//h3[text()='Margherita']]")
    pizza_card.click()
    time.sleep(1)

    yes_button = wait_for_element(By.XPATH, "//button[text()='Yes']")
    yes_button.click()
    time.sleep(1)

    pizza_card = wait_for_element(By.XPATH, "//div[contains(@class, 'pizza-card') and .//h3[text()='Pepperoni']]")
    pizza_card.click()
    time.sleep(1)

    yes_button = wait_for_element(By.XPATH, "//button[text()='Yes']")
    yes_button.click()
    time.sleep(1)

    pizza_card = wait_for_element(By.XPATH, "//div[contains(@class, 'pizza-card') and .//h3[text()='Vege']]")
    pizza_card.click()
    time.sleep(1)

# Odrzucenie ostatniej pizzy

    yes_button = wait_for_element(By.XPATH, "//button[text()='No']")
    yes_button.click()
    time.sleep(1)

# Przejście do koszyka

    cart_button = wait_for_element(By.ID, "cart-modal")
    cart_button.click()
    time.sleep(1)

# Zaznaczanie dodatkowych składników

    topping_button = driver.find_element(By.XPATH, "(//button[@class='cart-button topping-button'])[1]")
    topping_button.click()
    time.sleep(1)

    mushroom_checkbox = driver.find_element(By.XPATH, "//span[contains(text(), 'Mushrooms')]//preceding-sibling::input[@type='checkbox']")
    mushroom_checkbox.click()
    time.sleep(1)

    save_button = driver.find_element(By.XPATH, "//button[text()='Save']")
    save_button.click()
    time.sleep(1)

    topping_button = driver.find_element(By.XPATH, "(//button[@class='cart-button topping-button'])[2]")
    topping_button.click()
    time.sleep(1)

    mushroom_checkbox = driver.find_element(By.XPATH, "//span[contains(text(), 'Extra Cheese')]//preceding-sibling::input[@type='checkbox']")
    mushroom_checkbox.click()
    time.sleep(1)

    mushroom_checkbox = driver.find_element(By.XPATH, "//span[contains(text(), 'Bacon')]//preceding-sibling::input[@type='checkbox']")
    mushroom_checkbox.click()
    time.sleep(1)

    save_button = driver.find_element(By.XPATH, "//button[text()='Save']")
    save_button.click()
    time.sleep(1)

# Wypełnianie danych dostawy

    delivery_address_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter your delivery address']")
    delivery_address_input.send_keys("Losowa 44a")

    delivery_date_input = driver.find_element(By.XPATH, "//input[@type='date']")
    delivery_date_input.send_keys("14-01-2025")

    delivery_time_input = driver.find_element(By.XPATH, "//input[@type='time']")
    delivery_time_input.send_keys("16:00")
    time.sleep(2)

# Wysłanie zamówienia

    place_order_button = driver.find_element(By.CLASS_NAME, "place-order-button")
    place_order_button.click()
    time.sleep(3)

    handle_alert()
    time.sleep(1)

# Ocena pizzerii

    rating_input = driver.find_element(By.CSS_SELECTOR, ".rating-input")
    rating_input.clear() 
    rating_input.send_keys("7")
    time.sleep(1)

    comment_input = driver.find_element(By.CSS_SELECTOR, ".comment-textarea")
    comment_input.clear()
    comment_input.send_keys("The best pizzeria :)")
    time.sleep(1)

# Wysłanie oceny

    submit_button = driver.find_element(By.CSS_SELECTOR, ".rate-submit-button")
    submit_button.click()
    time.sleep(3)

    handle_alert()
    wait_for_element(By.CLASS_NAME, "pizzas-container")
    time.sleep(1)

# W zakładce z informacjami o koncie użytkownika pojawiło się zamówienie w historii 

    account_button = wait_for_element(By.ID, "account-modal")
    account_button.click()
    time.sleep(3)

# Edycja danych użytkownika

    edit_button = driver.find_element(By.CSS_SELECTOR, ".edit-button")
    edit_button.click()
    time.sleep(1)

    telephone_input = driver.find_element(By.NAME, "telephone_number")
    telephone_input.clear()
    telephone_input.send_keys("123123123")

    cancel_button = driver.find_element(By.CSS_SELECTOR, ".cancel-button")
    cancel_button.click()
    time.sleep(1)

    edit_button.click()
    time.sleep(1)

    telephone_input = driver.find_element(By.NAME, "telephone_number")
    telephone_input.clear()
    telephone_input.send_keys("456456456")
    time.sleep(1)

    save_button = driver.find_element(By.CSS_SELECTOR, ".save-button")
    save_button.click()
    time.sleep(3)

# Powrót do strony głównej

    pizza_button = wait_for_element(By.ID, "pizzas-modal")
    pizza_button.click()
    time.sleep(3)

# Wylogowanie użytkownika

    register_button = wait_for_element(By.ID, "loguot-modal")
    register_button.click()
    time.sleep(2)

# Zalogowanie użytkownika

    register_button = wait_for_element(By.ID, "login-modal")
    register_button.click()
    time.sleep(1)

    wait_for_element(By.XPATH, "//input[@placeholder='Username']").send_keys("Adam320")
    wait_for_element(By.XPATH, "//input[@placeholder='Password']").send_keys("Adam023")
    time.sleep(1)

    login_submit_button = wait_for_element(By.ID, "login-submit")
    login_submit_button.click()
    time.sleep(2)

# Po wylogowaniu i ponownym zalogowaniu

    register_button = wait_for_element(By.ID, "account-modal")
    register_button.click()

finally:
    time.sleep(10)
    driver.quit()
