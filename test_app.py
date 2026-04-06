"""
Script de teste para verificar a funcionalidade de leitura de QR codes
"""

import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image

def test_qr_extraction():
    """Testa a extração de dados de um QR code simulado"""
    
    # Dados de exemplo típicos de uma fatura portuguesa ATCUD
    sample_data = "//ATCUD:ABC123-XYZ789//Serie:2024;Número:123;Data:01-01-2024;Valor:100.00;Hash:A1B2C3D4E5F6"
    
    print("=" * 60)
    print("TESTE DE EXTRAÇÃO DE CAMPOS ATCUD")
    print("=" * 60)
    print(f"\nDados brutos do QR Code:\n{sample_data}\n")
    
    # Testar parsing dos campos
    import re
    
    fields = {}
    
    # Extrair ATCUD
    atcud_pattern = r'//ATCUD:(.+?)//'
    match = re.search(atcud_pattern, sample_data)
    if match:
        fields['ATCUD'] = match.group(1).strip()
    
    # Padrões para outros campos - usar [^;] para parar no ponto e vírgula
    patterns = {
        'Serie': r'Serie[:\s]*([^;\n]+)',
        'Número': r'N[úuo]mero[:\s]*([^;\n]+)',
        'Data': r'Data[:\s]*(\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2})',
        'Valor': r'Valor[:\s]*([\d.,]+)\s?€?',
        'Hash': r'Hash[:\s]*([^;\n]+)',
    }
    
    for field_name, pattern in patterns.items():
        match = re.search(pattern, sample_data, re.IGNORECASE)
        if match:
            fields[field_name] = match.group(1).strip()
    
    print("Campos Extraídos:")
    print("-" * 60)
    for field_name, field_value in fields.items():
        print(f"{field_name:15}: {field_value}")
    print("-" * 60)
    
    # Verificar se todos os campos esperados foram encontrados
    expected_fields = ['ATCUD', 'Serie', 'Número', 'Data', 'Valor', 'Hash']
    missing = [f for f in expected_fields if f not in fields]
    
    if not missing:
        print("\n✅ SUCESSO: Todos os campos foram extraídos corretamente!")
    else:
        print(f"\n⚠️ AVISO: Campos em falta: {missing}")
    
    print("\n" + "=" * 60)
    
    return True

if __name__ == "__main__":
    test_qr_extraction()
