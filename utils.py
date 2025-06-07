import requests
import datetime
import time

def get_timestamp():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def get_latlon_from_endereco(endereco_completo):
    lat, lon = None, None
    tentativas_endereco = []

    # 1. Primeira tentativa: Endereço completo (como veio do formulário, incluindo número)
    tentativas_endereco.append(endereco_completo)

    # Extrair rua, cidade, estado, país de forma robusta para uma segunda tentativa
    # Assumimos que o formato é "Logradouro, Número, Bairro, Cidade, Estado, País"
    # ou "Logradouro, Bairro, Cidade, Estado, País"
    partes = [p.strip() for p in endereco_completo.split(',')]
    
    # Tentativa de extrair Logradouro, Cidade, Estado, País
    # Isso é um pouco heurístico, mas visa pegar os elementos essenciais
    logradouro_simplificado = ""
    cidade_simplificada = ""
    estado_simplificado = ""
    pais_simplificado = "Brasil" # Hardcoded, já que estamos no Brasil

    if len(partes) >= 4: # Pelo menos Logradouro, Cidade, Estado, País
        logradouro_simplificado = partes[0]
        cidade_simplificada = partes[-3]
        estado_simplificada = partes[-2]
        pais_simplificado = partes[-1]
    elif len(partes) == 3: # Logradouro, Cidade, Estado (pode acontecer com alguns CEPs)
        logradouro_simplificado = partes[0]
        cidade_simplificada = partes[1]
        estado_simplificada = partes[2]
    elif len(partes) == 2: # Logradouro, Cidade (muito simplificado)
        logradouro_simplificado = partes[0]
        cidade_simplificada = partes[1]
    elif len(partes) == 1: # Apenas logradouro, ou algo isolado
        logradouro_simplificado = partes[0]


    # 2. Segunda tentativa: Apenas Logradouro, Cidade, Estado, País
    # Esta é a tentativa mais crucial para garantir algum resultado.
    # Evitamos número e bairro específicos que podem não estar no OSM.
    endereco_rua_cidade_estado_pais = f"{logradouro_simplificado}, {cidade_simplificada}, {estado_simplificada}, {pais_simplificado}"
    if endereco_rua_cidade_estado_pais not in tentativas_endereco and logradouro_simplificado and cidade_simplificada:
        tentativas_endereco.append(endereco_rua_cidade_estado_pais)
    
    # 3. Terceira tentativa (caso as anteriores falhem): Apenas Cidade, Estado, País
    # Isso serve como um último recurso para ter alguma localização, se nem a rua for encontrada.
    endereco_cidade_estado_pais = f"{cidade_simplificada}, {estado_simplificada}, {pais_simplificado}"
    if endereco_cidade_estado_pais not in tentativas_endereco and cidade_simplificada:
        tentativas_endereco.append(endereco_cidade_estado_pais)


    # Remover duplicatas e manter ordem de preferência
    tentativas_endereco_final = []
    for item in tentativas_endereco:
        if item.strip() and item not in tentativas_endereco_final: # Garante que não adiciona strings vazias
            tentativas_endereco_final.append(item)

    print(f"Tentativas de endereço para Nominatim: {tentativas_endereco_final}")

    for tentativa_endereco in tentativas_endereco_final:
        if lat is not None and lon is not None: # Se já achou, sai do loop
            break
        try:
            print(f"Tentando Nominatim com: '{tentativa_endereco}'")
            time.sleep(1.5) # Atraso para respeitar a política de uso do Nominatim

            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": tentativa_endereco, "format": "json", "limit": 1},
                headers={"User-Agent": "AlertaPorGestoApp/1.0"},
                timeout=10 # Aumentar o timeout
            )
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                print(f"Nominatim Lat/Lon encontrada com '{tentativa_endereco}': {lat}, {lon}")
                return lat, lon # Retorna assim que encontrar
            else:
                print(f"Nominatim não encontrou coordenadas para: '{tentativa_endereco}'")
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão ou timeout com Nominatim para '{tentativa_endereco}': {e}")
        except Exception as e:
            print(f"Erro inesperado com Nominatim para '{tentativa_endereco}': {e}")

    print(f"Não foi possível encontrar lat/lon por nenhuma tentativa do Nominatim para: {endereco_completo}")
    return None, None