import os

from simulador.gui import AplicacaoSimulador, criar_janela

if __name__ == "__main__":
    if os.environ.get("SIMULADOR_SMOKE") == "1":
        app = AplicacaoSimulador()
        app.update_idletasks()
        app.destroy()
    else:
        criar_janela()
