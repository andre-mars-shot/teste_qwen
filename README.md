# Leitor de QR Code para Faturas ATCUD

Aplicação Streamlit para leitura e extração de campos ATCUD de códigos QR em faturas portuguesas.

## Funcionalidades

- 📤 **Upload de Imagem**: Carregue imagens de QR codes (PNG, JPG, GIF, BMP)
- 📷 **Webcam**: Capture QR codes diretamente com a câmera
- 🔍 **Extração Automática**: Identifica e extrai campos como:
  - Código ATCUD
  - Série da fatura
  - Número da fatura
  - Data de emissão
  - Valor total
  - Hash de verificação
  - NIF do emitente

## Instalação

### Linux (Ubuntu/Debian)

1. Instale a biblioteca zbar (necessária para o pyzbar):
```bash
sudo apt-get install libzbar0
```

2. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

### macOS

1. Instale a biblioteca zbar via Homebrew:
```bash
brew install zbar
```

2. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

### Windows

O instalador do pyzbar já inclui as bibliotecas necessárias. Basta:
```bash
pip install -r requirements.txt
```

### Executar a aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no seu navegador em `http://localhost:8501`

## Requisitos

- Python 3.8+
- streamlit >= 1.28.0
- opencv-python-headless >= 4.8.0
- numpy >= 1.24.0
- pyzbar >= 0.1.9
- Pillow >= 10.0.0

## Como Usar

1. Selecione o método de entrada (Upload ou Webcam)
2. Forneça a imagem com o QR code da fatura
3. A aplicação irá automaticamente:
   - Detectar o QR code
   - Decodificar os dados
   - Extrair os campos ATCUD
4. Visualize e copie os dados extraídos

## Formato ATCUD

O código QR das faturas portuguesas segue geralmente este formato:
```
//ATCUD:XXX-YYY//Serie:2024;Número:123;Data:01-01-2024;Valor:100.00;Hash:...
```

A aplicação tenta identificar automaticamente estes campos e apresentá-los de forma estruturada.

## Validação

Pode validar a autenticidade da fatura no portal das Finanças:
[Portal e-Fatura](https://www.portaldasfinancas.gov.pt/)

## Notas

- As imagens são processadas localmente
- Nenhum dado é enviado para servidores externos
- Para melhores resultados, certifique-se que o QR code está bem iluminado e nítido
