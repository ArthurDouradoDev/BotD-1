import sys
from src.utils.config import load_config
from src.ui.app import AutomaApp

def main():
    # Inicializa as configurações (.env)
    load_config()
    
    # Inicia a interface gráfica
    app = AutomaApp()
    app.mainloop()

if __name__ == "__main__":
    main()
