import os
import glob
import subprocess
from playwright.sync_api import sync_playwright

def get_playwright_browsers_path():
    browsers_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
    return browsers_path

def ensure_chromium_installed(callback_log):
    browsers_path = get_playwright_browsers_path()
    chromium_found = glob.glob(os.path.join(browsers_path, "chromium-*", "chrome-win64", "chrome.exe"))
    
    if not chromium_found:
        callback_log("Chromium não encontrado. Instalando pela primeira vez (pode demorar)...")
        try:
            from playwright._impl._driver import compute_driver_executable
            driver = compute_driver_executable()
            
            if isinstance(driver, tuple):
                cmd = [driver[0], driver[1], "install", "chromium"]
            else:
                cmd = [str(driver), "install", "chromium"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(result.stderr or result.stdout)
            callback_log("Chromium instalado com sucesso.")
        except Exception as e:
            raise Exception(f"Erro ao instalar Chromium: {e}")

def launch_browser(playwright):
    return playwright.chromium.launch(
        headless=False,
        args=['--start-maximized']
    )

def create_standard_context(browser):
    return browser.new_context(
        no_viewport=True
    )
