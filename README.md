# Neuro Literature Mapper

Projeto inicial para apoiar o trabalho de FSI: localizar, registrar, classificar e organizar literatura de Sistemas de Informação sobre LLMs, IA generativa, vieses cognitivos, julgamento, confiança e decisão.

## Objetivo

Este projeto implementa um pipeline **semi-automatizado** para apoiar um levantamento exploratório estruturado da literatura de SI.

Ele não substitui a leitura acadêmica. Ele ajuda a:

- executar buscas em APIs abertas;
- gerar buscas direcionadas por venue usando `site:`;
- consolidar metadados;
- remover duplicatas;
- sugerir tags;
- sugerir prioridade preliminar;
- exportar uma matriz CSV para análise;
- preparar importação posterior no Zotero.

## Fontes contempladas

### Busca automatizada ampla

- OpenAlex
- Crossref
- Semantic Scholar

### Busca direcionada por venues de SI

- SBSI
- iSys
- AIS eLibrary: ICIS, ECIS, AMCIS, HICSS
- Periódicos internacionais: MISQ, ISJ, BISE, IPM, IS, KAIS, TEIS, IJWIS

A busca direcionada por venues é registrada no arquivo de saída, mas a seleção final continua manual.

## Instalação

```bash
cd neuro-literature-mapper
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copie o arquivo de ambiente:

```bash
cp .env.example .env
```

A chave do Semantic Scholar é opcional, mas ajuda em limites de uso.

## Uso via CLI

### Rodar buscas automatizadas

```bash
python -m neuro_mapper.cli search --config config/queries_neuro.yaml --output outputs/resultados_neuro.csv
```

### Gerar buscas direcionadas por venue

```bash
python -m neuro_mapper.cli venue-search --config config/queries_neuro.yaml --output outputs/buscas_venues.csv
```

### Rodar tudo

```bash
python -m neuro_mapper.cli all --config config/queries_neuro.yaml --output-dir outputs
```

## Uso com Streamlit

```bash
streamlit run app_streamlit.py
```

## Fluxo recomendado

1. Ajustar `config/queries_neuro.yaml`.
2. Rodar `venue-search`.
3. Executar manualmente as buscas `site:` no navegador.
4. Salvar artigos relevantes no Zotero.
5. Rodar `search` para busca ampla por APIs.
6. Abrir `outputs/resultados_neuro.csv`.
7. Classificar manualmente os artigos.
8. Importar os selecionados para o Zotero.
9. Preencher a matriz de extração.

## Limitações

- O script não raspa Google Acadêmico nem Google Search.
- As APIs abertas podem não cobrir todos os artigos dos venues indicados.
- A classificação automática é apenas uma triagem inicial.
- A seleção final e a interpretação acadêmica devem ser feitas pelo pesquisador.

## Estrutura Zotero sugerida

```text
FSI 2026.1 - LLMs, Vieses Cognitivos e SI
├── 00 - Inbox / Triagem
├── 01 - Literatura central de SI
├── 02 - IA Generativa e LLMs em SI
├── 03 - Interação Humano-IA, Confiança e Decisão
├── 04 - Vieses Cognitivos na Interação com IA
├── 05 - Literatura Brasileira de SI
├── 06 - Clássicos e Fundamentos Teóricos
├── 07 - Metodologia / Protocolo / Revisão de Literatura
├── 90 - Apoio / Áreas Vizinhas
└── 99 - Descartados
```
