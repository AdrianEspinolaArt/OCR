import pytesseract
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import xml.etree.ElementTree as ET
import re

class OCRApp:
    def __init__(self, master):
        self.master = master
        self.master.title("OCR App")
        self.master.geometry("800x600")

        self.imagem_path = None

        # Carregar os parâmetros do modelo CNH do arquivo XML
        self.parametros_cnh = self.carregar_parametros_cnh("cnh_modelo.xml")

        # Criar um frame para a imagem
        self.imagem_frame = tk.Frame(self.master)
        self.imagem_frame.pack()

        # Criar um label para exibir a imagem
        self.imagem_label = tk.Label(self.imagem_frame)
        self.imagem_label.pack()

        # Criar um botão para selecionar arquivo
        self.selecionar_button = tk.Button(self.master, text="Selecionar Arquivo", command=self.carregar_imagem)
        self.selecionar_button.pack(side="left", padx=10)

        # Criar um botão para realizar o OCR
        self.ocr_button = tk.Button(self.master, text="Realizar OCR", command=self.realizar_ocr)
        self.ocr_button.pack(side="left")

        # Criar um widget para exibir o resultado do OCR
        self.resultado_texto = tk.Text(self.master, height=10, width=50, state="disabled")
        self.resultado_texto.pack()

    def carregar_imagem(self):
        self.imagem_path = filedialog.askopenfilename(title="Selecionar Imagem", filetypes=[("Imagens", "*.jpg *.png")])

        if self.imagem_path:
            imagem_pillow = Image.open(self.imagem_path)
            imagem_pillow = imagem_pillow.resize((600, 400), Image.BICUBIC)
            imagem_tk = ImageTk.PhotoImage(imagem_pillow)
            self.imagem_label.config(image=imagem_tk)
            self.imagem_label.image = imagem_tk

    def carregar_parametros_cnh(self, arquivo_xml):
        parametros_cnh = {}
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()

        for obj in root.findall("object"):
            nome = obj.find("name").text
            bndbox = obj.find("bndbox")
            xmin = int(bndbox.find("xmin").text)
            ymin = int(bndbox.find("ymin").text)
            xmax = int(bndbox.find("xmax").text)
            ymax = int(bndbox.find("ymax").text)

            parametros_cnh[nome] = (xmin, ymin, xmax, ymax)

        return parametros_cnh

    def realizar_ocr(self):
        if not self.imagem_path:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo de imagem primeiro.")
            return

        imagem = cv2.imread(self.imagem_path)
        
        # Verificar a qualidade da imagem
        if not self.detectar_bordas(imagem):
            messagebox.showwarning("Aviso", "Por favor, verifique as bordas da imagem do documento.")
            return
        elif not self.verificar_ocr_previo(imagem):
            messagebox.showwarning("Aviso", "Não foi possível extrair texto da imagem do documento.")
            return
        elif not self.verificar_ruido(imagem):
            messagebox.showwarning("Aviso", "Por favor, verifique o ruído na imagem do documento.")
            return
        elif not self.verificar_resolucao(imagem):
            messagebox.showwarning("Aviso", "Por favor, verifique a resolução da imagem do documento.")
            return

        caminho_tesseract = r"C:\Users\adrian.espinola\AppData\Local\Programs\Tesseract-OCR"
        pytesseract.pytesseract.tesseract_cmd = caminho_tesseract + r'\tesseract.exe'

        resultado = {}
        for campo, parametros in self.parametros_cnh.items():
            xmin, ymin, xmax, ymax = parametros
            # Extrair a região da imagem correspondente ao campo
            regiao_imagem = imagem[ymin:ymax, xmin:xmax]
            # Realizar OCR na região da imagem
            texto = pytesseract.image_to_string(regiao_imagem, lang="por")
            print(f"Texto detectado para '{campo}': {texto}")  # Printar texto detectado antes do processamento
            resultado[campo] = texto.strip() if texto else "Não encontrado"

        self.exibir_resultado(resultado)

    def detectar_bordas(self, imagem):
        imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        bordas = cv2.Canny(imagem_cinza, 100, 200)
        return cv2.countNonZero(bordas) != 0

    def verificar_ocr_previo(self, imagem):
        caminho_tesseract = r"C:\Users\adrian.espinola\AppData\Local\Programs\Tesseract-OCR"
        pytesseract.pytesseract.tesseract_cmd = caminho_tesseract + r'\tesseract.exe'
        texto = pytesseract.image_to_string(imagem, lang="por")
        return bool(texto)

    def verificar_ruido(self, imagem):
        imagem_filtrada = cv2.GaussianBlur(imagem, (5, 5), 0)
        diferenca = cv2.absdiff(imagem, imagem_filtrada)
        diferenca_cinza = cv2.cvtColor(diferenca, cv2.COLOR_BGR2GRAY)
        media_diferenca = cv2.mean(diferenca_cinza)[0]
        return media_diferenca <= 10

    def verificar_resolucao(self, imagem):
        altura, largura = imagem.shape[:2]
        resolucao_minima = 1000
        return altura >= resolucao_minima and largura >= resolucao_minima

    def extrair_dados(self, imagem):
        resultado = {}
        for campo, parametros in self.parametros_cnh.items():
            xmin, ymin, xmax, ymax = parametros
            regiao_imagem = imagem[ymin:ymax, xmin:xmax]  # Limitar a busca à região delimitada pelo campo
            texto = pytesseract.image_to_string(regiao_imagem, lang="por")
            resultado[campo] = texto.strip() if texto else "Não encontrado"
        return resultado

    def exibir_resultado(self, resultado):
        self.resultado_texto.config(state="normal")
        self.resultado_texto.delete("1.0", tk.END)
        for campo, valor in resultado.items():
            self.resultado_texto.insert(tk.END, f"{campo}: {valor}\n")
        self.resultado_texto.config(state="disabled")


def main():
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()