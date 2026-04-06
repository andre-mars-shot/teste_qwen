import streamlit as st
import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image
import re
import io

# Configuração da página
st.set_page_config(
    page_title="Leitor de QR Code - Faturas ATCUD",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Leitor de QR Code de Faturas (ATCUD)")
st.markdown("""
Esta aplicação permite ler o código QR de faturas portuguesas e extrair os campos ATCUD.
O código QR das faturas contém informações estruturadas que podem ser extraídas automaticamente.
""")

def decode_qr_code(image):
    """
    Decodifica códigos QR de uma imagem.
    
    Args:
        image: Imagem PIL ou array numpy
        
    Returns:
        Lista de dados decodificados
    """
    # Converter para formato OpenCV se necessário
    if isinstance(image, Image.Image):
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    else:
        img_cv = image
    
    # Decodificar códigos QR
    decoded_objects = pyzbar.decode(img_cv)
    
    results = []
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            results.append({
                'data': obj.data.decode('utf-8'),
                'rect': obj.rect,
                'polygon': obj.polygon
            })
    
    return results

def parse_atcud_fields(qr_data):
    """
    Extrai campos específicos do formato ATCUD do código QR.
    
    O formato típico é:
    //ATCUD:XXX-YYY//ZZZ...
    
    Campos comuns:
    - ATCUD: Código único do documento
    - Serie: Série da fatura
    - Numero: Número da fatura
    - Data: Data de emissão
    - Valor: Valor total
    - Hash: Hash de assinatura
    """
    fields = {}
    
    # Tentar extrair padrão ATCUD
    atcud_pattern = r'//ATCUD:(.+?)//'
    match = re.search(atcud_pattern, qr_data)
    if match:
        fields['ATCUD'] = match.group(1).strip()
    
    # Extrair outros campos comuns em faturas portuguesas
    # Padrões típicos encontrados em QR codes de faturas
    patterns = {
        'Serie': r'Serie[:\s]*([^;\n]+)',
        'Número': r'N[úuo]mero[:\s]*([^;\n]+)',
        'Data': r'Data[:\s]*(\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2})',
        'Valor': r'Valor[:\s]*([\d.,]+)\s?€?',
        'Hash': r'Hash[:\s]*([^;\n]+)',
        'RFC': r'RFC[:\s]*([^;\n]+)',
        'NIF': r'NIF[:\s]*(\d+)',
        'Emissor': r'Emissor[:\s]*([^;\n]+)',
    }
    
    for field_name, pattern in patterns.items():
        match = re.search(pattern, qr_data, re.IGNORECASE)
        if match:
            fields[field_name] = match.group(1).strip()
    
    # Se não encontrou padrões nomeados, tenta dividir por delimitadores comuns
    if not fields:
        # Tentar dividir por ponto e vírgula ou vírgula
        if ';' in qr_data:
            parts = qr_data.split(';')
            for i, part in enumerate(parts):
                fields[f'Campo_{i+1}'] = part.strip()
        elif ',' in qr_data:
            parts = qr_data.split(',')
            for i, part in enumerate(parts):
                fields[f'Campo_{i+1}'] = part.strip()
        else:
            fields['Conteúdo Completo'] = qr_data
    
    return fields

def process_image(image_source, source_type='upload'):
    """
    Processa uma imagem para extrair códigos QR.
    
    Args:
        image_source: Caminho do arquivo ou dados da imagem
        source_type: 'upload' ou 'camera'
        
    Returns:
        Resultados da decodificação
    """
    try:
        if source_type == 'upload':
            image = Image.open(image_source)
        else:
            image = image_source
        
        # Decodificar QR codes
        qr_results = decode_qr_code(image)
        
        return qr_results
    except Exception as e:
        st.error(f"Erro ao processar imagem: {str(e)}")
        return []

# Sidebar com opções
st.sidebar.header("Opções")
input_method = st.sidebar.radio(
    "Método de entrada:",
    ["Upload de Imagem", "Usar Webcam"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Formatos suportados:**
- PNG
- JPG/JPEG
- GIF
- BMP

**Dicas:**
- Certifique-se que o QR code está bem iluminado
- Evite reflexos na imagem
- O código deve estar nítido e legível
""")

# Área principal
if input_method == "Upload de Imagem":
    st.header("📤 Upload da Imagem")
    
    uploaded_file = st.file_uploader(
        "Escolha uma imagem com o QR Code da fatura",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp']
    )
    
    if uploaded_file is not None:
        # Display da imagem
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Imagem Carregada")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
        
        with col2:
            st.subheader("Resultados")
            
            # Processar imagem
            with st.spinner("A processar QR Code..."):
                qr_results = process_image(uploaded_file, 'upload')
            
            if qr_results:
                st.success(f"✅ {len(qr_results)} QR Code(s) encontrado(s)!")
                
                for i, qr in enumerate(qr_results, 1):
                    with st.expander(f"QR Code #{i}", expanded=True):
                        st.markdown("**Dados Brutos:**")
                        st.code(qr['data'], language='text')
                        
                        st.markdown("**Campos Extraídos (ATCUD):**")
                        fields = parse_atcud_fields(qr['data'])
                        
                        if fields:
                            for field_name, field_value in fields.items():
                                st.text_input(field_name, value=field_value, key=f"field_{i}_{field_name}")
                        else:
                            st.warning("Não foi possível identificar campos específicos.")
                        
                        # Botão para copiar dados
                        if st.button(f"📋 Copiar Dados Brutos #{i}"):
                            st.session_state[f'copy_{i}'] = qr['data']
                            st.success("Dados copiados! (Use Ctrl+C)")
            else:
                st.warning("⚠️ Nenhum QR Code encontrado na imagem.")
                st.info("Verifique se a imagem contém um QR Code legível.")

else:  # Webcam
    st.header("📷 Usar Webcam")
    st.markdown("Aponte a câmera para o QR Code da fatura.")
    
    # Nota sobre limitações do Streamlit com webcam em tempo real
    st.info("""
    **Nota:** A captura por webcam no Streamlit tem limitações. 
    Para melhores resultados, recomenda-se:
    1. Tirar uma foto do QR Code
    2. Fazer upload da imagem
    """)
    
    # Usando st.camera_input (disponível em versões recentes do Streamlit)
    try:
        camera_image = st.camera_input("Ativar câmera")
        
        if camera_image is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Captura da Câmera")
                image = Image.open(camera_image)
                st.image(image, use_column_width=True)
            
            with col2:
                st.subheader("Resultados")
                
                with st.spinner("A processar QR Code..."):
                    qr_results = process_image(camera_image, 'camera')
                
                if qr_results:
                    st.success(f"✅ {len(qr_results)} QR Code(s) encontrado(s)!")
                    
                    for i, qr in enumerate(qr_results, 1):
                        with st.expander(f"QR Code #{i}", expanded=True):
                            st.markdown("**Dados Brutos:**")
                            st.code(qr['data'], language='text')
                            
                            st.markdown("**Campos Extraídos (ATCUD):**")
                            fields = parse_atcud_fields(qr['data'])
                            
                            if fields:
                                for field_name, field_value in fields.items():
                                    st.text_input(field_name, value=field_value, key=f"cam_field_{i}_{field_name}")
                else:
                    st.warning("⚠️ Nenhum QR Code encontrado.")
    except Exception as e:
        st.error(f"Erro ao acessar câmera: {str(e)}")
        st.info("Alternativa: Use a opção de upload de imagem.")

# Secção de ajuda
with st.expander("ℹ️ Sobre o formato ATCUD"):
    st.markdown("""
    ### O que é o ATCUD?
    
    O **ATCUD** (Atribuição de Código Único de Documento) é um sistema português 
    que atribui um código único a cada documento fiscal.
    
    ### Estrutura do QR Code em Faturas Portuguesas
    
    Os códigos QR em faturas portuguesas normalmente contêm:
    - Código ATCUD único
    - Número da fatura
    - Série da fatura
    - Data de emissão
    - Valor total
    - Hash de verificação
    - NIF do emitente
    
    ### Formato Típico
    
    ```
    //ATCUD:ABC123-XYZ789//Serie:2024;Número:123;Data:01-01-2024;Valor:100.00;Hash:...
    ```
    
    ### Validação
    
    Pode validar a autenticidade da fatura no portal das Finanças:
    [Portal e-Fatura](https://www.portaldasfinancas.gov.pt/)
    """)

# Footer
st.markdown("---")
st.markdown("""
**Nota:** Esta aplicação processa as imagens localmente. Nenhuma imagem é enviada para servidores externos.
""")
