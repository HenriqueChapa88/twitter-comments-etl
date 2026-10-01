# Coleta Automatizada de Comentários do X/Twitter

Projeto desenvolvido em **Python** para automatizar a coleta, filtragem e organização de comentários públicos do X/Twitter utilizando o serviço **ScrapeBadger**.

O sistema realiza buscas avançadas relacionadas a jogadores de futebol em períodos específicos, coleta os comentários encontrados, trata falhas de conexão e indisponibilidade da API e organiza os dados em uma base estruturada para posterior análise.

O projeto foi desenvolvido como parte do meu **Trabalho de Conclusão de Curso (TCC)**, que analisou a relação entre o desempenho de jogadores de futebol e os comentários publicados por torcedores nas redes sociais.

## 🚀 Funcionalidades

- Coleta automatizada de comentários do X/Twitter
- Integração com a API do ScrapeBadger
- Utilização de consultas avançadas com palavras-chave
- Definição automática de intervalos de datas para coleta
- Leitura das datas de partidas a partir de uma planilha Excel
- Filtragem de comentários relacionados ao jogador analisado
- Paginação automática dos resultados utilizando cursor
- Definição de quantidade mínima e máxima de comentários por período
- Tratamento de erros HTTP e indisponibilidade temporária da API
- Novas tentativas automáticas em caso de falhas de conexão
- Controle de intervalo entre requisições
- Salvamento de backups durante a execução
- Recuperação dos dados em caso de interrupção ou erro crítico
- Exportação dos resultados para Excel
- Exportação emergencial para CSV caso ocorra erro no salvamento da planilha

## 🔎 Estratégia de busca

A coleta utiliza consultas avançadas combinando:

- Nome do jogador
- Nome e variações do clube
- Termos relacionados à atuação e desempenho
- Intervalos específicos de datas
- Exclusão de termos considerados pouco relevantes para a análise

Exemplos de termos utilizados na pesquisa incluem palavras relacionadas a:

- atuação
- desempenho
- jogo
- craque
- ruim
- melhor
- pior
- errou
- decidiu

Essa estratégia busca priorizar comentários que expressem opiniões dos torcedores sobre a atuação do jogador.

## 📅 Coleta baseada nas datas das partidas

As datas utilizadas na coleta são carregadas a partir de um arquivo Excel.

Para cada data, o programa calcula automaticamente uma janela de busca anterior à partida ou baseada na diferença entre as datas cadastradas.

Esse processo permite automatizar a coleta de comentários referentes a diferentes períodos sem a necessidade de configurar manualmente cada pesquisa.

## 🔄 Pipeline de dados

O projeto utiliza um fluxo simplificado de ETL:

### Extract

Os comentários são obtidos por meio de requisições HTTP ao ScrapeBadger, utilizando consultas avançadas para localizar publicações relacionadas ao jogador analisado.

### Transform

Os resultados retornados em JSON são processados e filtrados.

Nesta etapa são realizadas tarefas como:

- Extração do texto das publicações
- Validação da presença do nome do jogador
- Associação dos comentários às respectivas datas de análise
- Controle da quantidade de comentários coletados
- Tratamento de respostas inválidas ou incompletas

### Load

Após o processamento, os comentários são armazenados em um DataFrame utilizando Pandas e exportados para arquivos Excel.

Durante a execução, backups também são gerados para reduzir o risco de perda de dados.

## 🛡️ Tratamento de erros

O projeto implementa mecanismos de tolerância a falhas durante a coleta.

Entre eles estão:

- Novas tentativas em caso de erros HTTP 500, 502, 503 e 504
- Tempo de espera progressivo entre novas tentativas
- Tentativas de reconexão em caso de falha de internet
- Salvamento periódico dos dados já coletados
- Captura de interrupções manuais
- Salvamento final garantido através de `try`, `except` e `finally`
- Exportação para CSV como alternativa caso o Excel não possa ser gerado

Esses mecanismos ajudam a preservar os dados obtidos durante processos de coleta mais longos.

## 📊 Estrutura dos dados

A base final contém principalmente:

| Campo | Descrição |
|---|---|
| DATA | Data utilizada como referência para a coleta |
| COMENTARIO | Texto da publicação coletada |

Os dados estruturados podem posteriormente ser utilizados em etapas de processamento de linguagem natural, análise de sentimentos e mineração de dados.

## 🛠️ Tecnologias utilizadas

- Python
- Pandas
- Requests
- ScrapeBadger
- APIs REST
- JSON
- Excel
- CSV
- Datetime

## 🎯 Objetivo do projeto

Este projeto foi desenvolvido como parte do meu Trabalho de Conclusão de Curso (TCC), voltado à análise da relação entre o desempenho de jogadores de futebol e os comentários publicados por torcedores nas redes sociais.

O objetivo desta etapa foi automatizar a coleta de comentários relacionados aos jogadores analisados, criando uma base textual estruturada para utilização nas etapas posteriores do projeto.

Os comentários coletados foram utilizados posteriormente em processos de pré-processamento e análise de sentimentos, permitindo classificá-los como positivos, negativos ou neutros e relacionar essas informações às estatísticas de desempenho esportivo coletadas em outra etapa do projeto.

Dessa forma, este projeto representa a etapa de coleta de dados textuais de um pipeline maior envolvendo extração de dados, processamento, análise de sentimentos e mineração de dados.
