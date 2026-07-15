# Neuro Literature Mapper

Pipeline semi-automatizado para apoiar o mapeamento exploratório da literatura sobre **Brain-Computer Interfaces (BCI)**, **Brain-Machine Interfaces (BMI)**, **Large Language Models (LLMs)**, neuroengenharia, neurotecnologia, vieses, segurança, privacidade e governança.

## Objetivo

Este projeto foi criado para localizar, consolidar, classificar e organizar literatura científica situada na interseção entre:

- interfaces cérebro-computador e cérebro-máquina;
- decodificação neural;
- modelos de linguagem;
- geração de linguagem a partir de sinais neurais;
- interação humano-IA;
- vieses e vulnerabilidades informacionais;
- segurança, privacidade, neuroética e governança.

O pipeline não substitui leitura acadêmica, avaliação crítica ou seleção manual. Ele oferece apoio para:

- executar buscas em APIs acadêmicas abertas;
- gerar buscas direcionadas por periódicos e conferências;
- consolidar metadados;
- remover registros duplicados;
- sugerir tags temáticas;
- sugerir prioridade preliminar;
- exportar resultados em CSV;
- apoiar a triagem e a organização no Zotero.

## Escopo conceitual

O projeto considera sistemas compostos por diferentes camadas:

```text
Sinais neurais
    ↓
Aquisição por BMI/BCI
    ↓
Processamento e decodificação neural
    ↓
Representação textual ou semântica
    ↓
LLM ou sistema de geração de linguagem
    ↓
Resposta, ação ou apoio à decisão
    ↓
Interpretação humana
```

O interesse de pesquisa não está em atribuir cognição humana aos LLMs.

O foco está em investigar como sistemas BMI–LLM podem:

- reproduzir padrões presentes nos dados;
- amplificar distorções na cadeia de processamento;
- induzir interpretações inadequadas;
- gerar confiança excessiva;
- introduzir riscos de privacidade e segurança;
- afetar autonomia, decisão e responsabilidade.

## Fontes contempladas

### Busca automatizada ampla

O pipeline utiliza APIs abertas para localizar publicações e recuperar metadados:

- OpenAlex;
- Crossref;
- Semantic Scholar.

A chave da API do Semantic Scholar é opcional, mas pode melhorar os limites de uso.

### Busca direcionada por venues

As buscas por venues são organizadas em áreas complementares.

#### Neuroengenharia, BMI e BCI

- Journal of Neural Engineering;
- IEEE Transactions on Neural Systems and Rehabilitation Engineering;
- IEEE Transactions on Biomedical Engineering;
- Journal of NeuroEngineering and Rehabilitation;
- Brain-Computer Interfaces;
- Frontiers in Neuroscience;
- Frontiers in Human Neuroscience;
- NeuroImage;
- International IEEE EMBS Conference on Neural Engineering;
- IEEE Engineering in Medicine and Biology Society;
- BCI Meeting.

#### Interação humano-computador e sistemas interativos

- ACM CHI Conference on Human Factors in Computing Systems;
- ACM Transactions on Computer-Human Interaction;
- ACM Conference on Computer-Supported Cooperative Work and Social Computing.

#### IA, LLMs e processamento de linguagem

- ACL;
- EMNLP;
- NAACL;
- COLING;
- NeurIPS;
- ICLR;
- ICML;
- AAAI.

#### Ética, governança e responsabilidade

- ACM Conference on Fairness, Accountability, and Transparency;
- AAAI/ACM Conference on AI, Ethics, and Society;
- AI and Ethics;
- Neuroethics.

A busca direcionada é registrada pelo pipeline, mas a seleção final continua sendo realizada manualmente.

## Instalação

```bash
cd neuro-literature-mapper

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Copie o arquivo de configuração de ambiente:

```bash
cp .env.example .env
```

## Uso via CLI

### Consultar os comandos disponíveis

```bash
python -m neuro_mapper.cli --help
```

### Rodar buscas automatizadas

```bash
python -m neuro_mapper.cli search \
  --config config/queries_neuro.yaml \
  --output outputs/resultados_neuro.csv
```

### Gerar buscas direcionadas por venue

```bash
python -m neuro_mapper.cli venue-search \
  --config config/queries_neuro.yaml \
  --output outputs/buscas_venues_neuro.csv
```

### Rodar o pipeline completo

```bash
python -m neuro_mapper.cli all \
  --config config/queries_neuro.yaml \
  --output-dir outputs
```

## Uso com Streamlit

```bash
streamlit run app_streamlit.py
```

A interface permite executar o pipeline, visualizar resultados preliminares e baixar os arquivos gerados.

## Arquivos de configuração

### `config/queries_neuro.yaml`

Define:

- termos de busca;
- camadas temáticas;
- parâmetros das APIs;
- critérios preliminares de classificação;
- venues utilizados na busca direcionada.

### `config/taxonomy_neuro.yaml`

Define a taxonomia utilizada na classificação dos artigos.

Exemplos de categorias:

- BMI/BCI;
- neural decoding;
- brain-to-text;
- imagined speech;
- LLMs;
- interação humano-IA;
- vieses;
- segurança;
- privacidade;
- neuroética;
- governança.

### `config/venues_neuro.yaml`

Organiza periódicos, conferências e repositórios por área de pesquisa.

## Fluxo recomendado

1. Revisar `config/queries_neuro.yaml`.
2. Ajustar os parâmetros e o período das buscas.
3. Executar `venue-search`.
4. Realizar manualmente as buscas direcionadas no navegador.
5. Salvar no Zotero os artigos potencialmente relevantes.
6. Executar `search` para consultar as APIs abertas.
7. Abrir `outputs/resultados_neuro.csv`.
8. Revisar títulos, resumos, venues e palavras-chave.
9. Remover falsos positivos.
10. Classificar os artigos selecionados.
11. Preencher a matriz analítica.
12. Registrar decisões de inclusão e exclusão.

## Eixos analíticos iniciais

### 1. BMI/BCI e aquisição neural

- EEG;
- ECoG;
- implantes intracorticais;
- sinais invasivos e não invasivos;
- aquisição e pré-processamento de sinais.

### 2. Decodificação neural

- neural decoding;
- imagined speech;
- attempted speech;
- brain-to-text;
- semantic decoding;
- reconstrução de linguagem.

### 3. Integração com LLMs

- correção e expansão de texto;
- previsão linguística;
- geração assistida;
- contextualização semântica;
- interfaces conversacionais;
- comunicação assistiva.

### 4. Vieses e vulnerabilidades

- vieses nos dados;
- vieses de seleção;
- erros de decodificação;
- amplificação algorítmica;
- confiança excessiva;
- overreliance;
- automação indevida;
- interpretação equivocada.

### 5. Segurança, privacidade e governança

- neural privacy;
- proteção de dados neurais;
- consentimento;
- autonomia;
- rastreabilidade;
- explicabilidade;
- responsabilidade;
- validação humana;
- monitoramento;
- neuroética.

## Critério preliminar de relevância

Um artigo pode ser classificado como de alta prioridade quando combina dois ou mais dos seguintes elementos:

- BMI ou BCI;
- decodificação neural;
- linguagem ou comunicação;
- LLMs ou NLP;
- vieses, segurança ou privacidade;
- interação ou validação humana;
- governança ou neuroética.

Artigos que mencionem apenas IA, saúde ou neurociência de forma genérica devem ser revisados antes da inclusão.

## Limitações

- O pipeline não realiza scraping do Google Acadêmico.
- As APIs abertas não indexam todos os periódicos e conferências da mesma forma.
- Alguns registros podem apresentar resumos incompletos.
- A deduplicação por DOI e título pode exigir revisão manual.
- Siglas como `BMI`, `BCI` e `LLM` podem produzir falsos positivos.
- A classificação automática é apenas uma etapa preliminar.
- A avaliação de qualidade e relevância permanece sob responsabilidade do pesquisador.

## Estrutura sugerida no Zotero

```text
BMI-BCI, LLMs, Neurotecnologia e Vieses
├── 00 - Inbox / Triagem
├── 01 - BMI e BCI
├── 02 - Aquisição e Processamento de Sinais Neurais
├── 03 - Decodificação Neural
├── 04 - Brain-to-Text e Comunicação
├── 05 - LLMs e Processamento de Linguagem
├── 06 - Integração BMI-LLM
├── 07 - Interação Humano-IA
├── 08 - Vieses e Vulnerabilidades
├── 09 - Segurança e Privacidade Neural
├── 10 - Neuroética e Governança
├── 11 - Aplicações Clínicas e Assistivas
├── 12 - Revisões e Surveys
├── 90 - Metodologia
├── 91 - Fundamentos e Clássicos
└── 99 - Descartados
```

## Estrutura do projeto

```text
neuro-literature-mapper/
├── app_streamlit.py
├── config/
│   ├── queries_neuro.yaml
│   ├── taxonomy_neuro.yaml
│   └── venues_neuro.yaml
├── data/
├── docs/
│   ├── decisoes_conceituais.md
│   ├── matriz_analitica_neuro.md
│   ├── protocolo_neuro.md
│   └── zotero_setup_neuro.md
├── outputs/
├── src/
│   └── neuro_mapper/
│       ├── cli.py
│       ├── config.py
│       ├── export.py
│       ├── models.py
│       ├── pipeline.py
│       ├── tagging.py
│       ├── venue_search.py
│       └── sources/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Status do projeto

O projeto encontra-se em fase inicial de adaptação e validação.

Próximas etapas:

1. consolidar as queries;
2. validar a taxonomia;
3. revisar a lista de venues;
4. executar uma primeira busca piloto;
5. analisar falsos positivos e falsos negativos;
6. ajustar a classificação automática;
7. produzir a primeira matriz de artigos.
