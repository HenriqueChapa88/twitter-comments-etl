import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES DA API ---
API_KEY = "" 
ENDPOINT_URL = "https://scrapebadger.com/v1/twitter/tweets/advanced_search"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

sessao = requests.Session()
sessao.headers.update(headers)

# --- LEITURA DAS DATAS ---
df_datas = pd.read_excel('datas.xlsx')
df_datas['Data'] = pd.to_datetime(df_datas['Data'], format='%d/%m/%Y')
df_datas = df_datas.sort_values(by='Data').reset_index(drop=True)

# ==========================================
# LISTA ONDE TODOS OS DADOS SERÃO GUARDADOS
# ==========================================
lista_final_consolidada = []

print("Iniciando rotina de coleta automática...")

# O 'try' principal envolve TUDO. Se qualquer erro fatal acontecer aqui dentro, 
# ele pula direto para o 'except' e depois para o 'finally' para salvar os dados.
try:
    # --- LOOP DE AUTOMAÇÃO POR DATA ---
    for i in range(len(df_datas)):
        data_atual = df_datas.loc[i, 'Data']
        data_atual_formatada = data_atual.strftime('%d/%m/%Y')
        
        if i == 0:
            data_inicio = data_atual - timedelta(days=7)
        else:
            data_anterior = df_datas.loc[i-1, 'Data']
            diferenca_dias = (data_atual - data_anterior).days
            
            if diferenca_dias <= 14:
                data_inicio = data_anterior + timedelta(days=1)
            else:
                data_inicio = data_atual - timedelta(days=7)
                
        since_str = data_inicio.strftime('%Y-%m-%d')
        until_str = data_atual.strftime('%Y-%m-%d')
        
        print("\n" + "="*60)
        print(f"[{i+1}/{len(df_datas)}] Coletando para a data alvo: {data_atual_formatada}")
        print(f"Buscando de {since_str} até {until_str}...")
        
        query_avancada = (
        f'since:{since_str} until:{until_str} '
    '(Arboleda) '
    '("São Paulo" OR "Sao Paulo" OR SPFC OR Tricolor OR "Tricolor Paulista") '
    '(jogou OR jogo OR atuação OR atuacao OR desempenho OR bem OR mal OR '
    'craque OR ruim OR decidiu OR errou OR melhor OR pior) '
    '-escalação -escalacao -escalado -"possível escalação" -"possivel escalacao"'
)         
        params = {
            "query": query_avancada,
            "query_type": "Top"
        }

        tweets_desta_data = []
        min_comentarios = 50
        max_comentarios = 100

        max_tentativas_erro = 3
        tentativas_atuais = 0
        falhas_conexao = 0 # Contador para quedas totais de internet

        while len(tweets_desta_data) < max_comentarios:
            try:
                response = sessao.get(ENDPOINT_URL, params=params) 
                falhas_conexao = 0 # Zeramos as falhas se a conexão deu certo
            except Exception as e:
                falhas_conexao += 1
                if falhas_conexao > 10:
                    # Se falhar 10 vezes seguidas (5 minutos sem internet), força a parada do script.
                    raise ConnectionError(f"Internet parece ter caído. Desistindo após 10 tentativas. Erro: {e}")
                    
                print(f"Erro de conexão ({falhas_conexao}/10). Tentando novamente em 30s...")
                time.sleep(30)
                continue
            
           # Trata erros de sobrecarga (503) e falhas internas do proxy da API (500, 502, 504)
            if response.status_code in [500, 502, 503, 504]:
                tentativas_atuais += 1

                if len(tweets_desta_data) >= min_comentarios:
                    print("Quantidade mínima atingida. Finalizando esta data.")
                    break

                if tentativas_atuais <= max_tentativas_erro:
                    tempo_espera = 30 * tentativas_atuais 
                    print(f"API ocupada (503). Aguardando {tempo_espera}s (Tentativa {tentativas_atuais}/{max_tentativas_erro})...")
                    time.sleep(tempo_espera)
                    continue 
                else:
                    print("Limite de tentativas atingido. Avançando para a próxima data.")
                    break
                    
            elif response.status_code != 200:
                print(f"Erro {response.status_code}: {response.text}")
                break
                
            tentativas_atuais = 0
            dados = response.json()
            tweets_atuais = dados.get("data", [])
            
            if not tweets_atuais:
                print("Fim dos resultados para esta janela de datas.")
                break
                
         # Processando os tweets retornados
            for t in tweets_atuais:
                texto = t.get("full_text") or t.get("text")
                
                # Lista de todas as formas que o torcedor pode ter escrito
                variacoes_nome = ['arboleda']
                
                # Se o texto existir E qualquer uma das variações estiver dentro dele
                if texto and any(nome in texto.lower() for nome in variacoes_nome):
                    
                    lista_final_consolidada.append({
                        'DATA': data_atual_formatada,
                        'COMENTARIO': texto
                    })
                    tweets_desta_data.append(texto)

            print(f"Coletados nesta rodada: {len(tweets_desta_data)} tweets...")

            next_cursor = dados.get("meta", {}).get("next_cursor") or dados.get("next_cursor")
            if not next_cursor or len(tweets_desta_data) >= max_comentarios:
                break
                
            params["cursor"] = next_cursor
            time.sleep(12) 

        # Continua salvando um backup rápido por segurança a cada data concluída
        if lista_final_consolidada:
            df_backup = pd.DataFrame(lista_final_consolidada)
            df_backup.to_excel("backup_coleta_em_andamento.xlsx", index=False)

        print(f"Acumulado até agora: {len(lista_final_consolidada)} comentários na lista final.")
        print("Aguardando 20 segundos antes de ir para a próxima data...")
        time.sleep(20)

# --- TRATAMENTO DE ERROS CRÍTICOS ---
except KeyboardInterrupt:
    print("\n[!] O script foi interrompido manualmente por você (Ctrl+C).")
except Exception as erro_critico:
    print(f"\n[!] O SCRIPT SOFREU UM ERRO CRÍTICO: {erro_critico}")
    print("Iniciando o resgate dos dados coletados até o momento do erro...")

# --- SALVAMENTO GARANTIDO (O 'TESTAMENTO' DO CÓDIGO) ---
finally:
    print("\n" + "="*60)
    print("EXECUTANDO ROTINA FINAL DE SALVAMENTO...")
    
    if lista_final_consolidada:
        df_final = pd.DataFrame(lista_final_consolidada)
        
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo_final = f"COLETA_FINAL_ARBOLEDA_{agora}.xlsx"
        
        try:
            df_final.to_excel(nome_arquivo_final, index=False)
            print("🚀 PLANILHA FINAL SALVA COM SUCESSO!")
            print(f"Total de linhas resgatadas/coletadas: {len(df_final)}")
            print(f"Arquivo gerado: {nome_arquivo_final}")
        except Exception as erro_salvamento:
            print(f"Erro extremo ao tentar salvar a planilha: {erro_salvamento}")
            print("Tentando salvar como CSV como último recurso...")
            df_final.to_csv(f"COLETA_EMERGENCIA_{agora}.csv", index=False)
    else:
        print("Nenhum dado válido foi coletado. Nenhuma planilha gerada.")