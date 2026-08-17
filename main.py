import tkinter as tk

from interface.tela_principal import TelaPrincipal


def main():
    janela = tk.Tk()

    app = TelaPrincipal(janela)

    janela.mainloop()


if __name__ == "__main__":
    main()