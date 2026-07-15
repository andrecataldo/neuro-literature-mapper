# Protocolo exploratório — BMI/BCI, LLMs, Neurotecnologia e Vieses

## 1. Tipo de estudo

Levantamento exploratório estruturado da literatura científica sobre a integração entre:

- Brain-Computer Interfaces — BCI;
- Brain-Machine Interfaces — BMI;
- decodificação neural;
- modelos de linguagem;
- geração e reconstrução de linguagem;
- interação humano-IA;
- vieses e vulnerabilidades;
- segurança, privacidade, neuroética e governança.

O estudo é orientado por protocolo, mas não pretende, nesta etapa, constituir uma revisão sistemática completa.

Seu objetivo é:

- mapear o estado inicial da literatura;
- identificar correntes de pesquisa;
- reconhecer terminologias utilizadas;
- localizar trabalhos centrais;
- identificar lacunas;
- apoiar a delimitação de uma pesquisa acadêmica posterior.

## 2. Tema

Integração entre BMI/BCI e Large Language Models, com foco em decodificação neural, geração de linguagem, vieses, vulnerabilidades, segurança, privacidade, confiança e governança.

## 3. Recorte conceitual

O objeto de investigação é tratado como um sistema composto por diferentes camadas:

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
Interpretação e validação humana
```

A análise considera que erros, distorções e riscos podem ser introduzidos ou amplificados em qualquer uma dessas camadas.

Não se atribuem processos cognitivos humanos aos LLMs.

O interesse está em investigar como sistemas BMI–LLM podem:

- reproduzir padrões presentes nos dados;
- amplificar distorções de aquisição ou decodificação;
- introduzir inferências não sustentadas pelos sinais neurais;
- induzir interpretações inadequadas;
- produzir confiança excessiva;
- afetar autonomia e tomada de decisão;
- gerar riscos de segurança e privacidade neural.

## 4. Questão principal

Como a literatura científica tem tratado a integração entre BMI/BCI e modelos de linguagem, especialmente em relação à decodificação neural, geração de linguagem, vieses, vulnerabilidades, confiança, segurança, privacidade e governança?

## 5. Subquestões

| Código | Subquestão |
|---|---|
| SQ01 | Quais arquiteturas, técnicas e aplicações têm sido utilizadas para integrar BMI/BCI, decodificação neural e modelos de linguagem? |
| SQ02 | Quais modalidades de sinais neurais aparecem nos estudos, como EEG, ECoG, fMRI ou implantes intracorticais? |
| SQ03 | Como os modelos de linguagem são utilizados na reconstrução, correção, expansão, interpretação ou geração de conteúdo a partir de sinais neurais? |
| SQ04 | Quais tipos de erro, distorção, viés ou vulnerabilidade são discutidos nos diferentes estágios do sistema? |
| SQ05 | Como os estudos tratam confiança, reliance, overreliance, incerteza, validação humana e supervisão? |
| SQ06 | Quais riscos de segurança, privacidade neural, autonomia, consentimento e uso indevido são identificados? |
| SQ07 | Quais estratégias de mitigação, monitoramento, rastreabilidade, explicabilidade ou governança são propostas? |
| SQ08 | Quais lacunas permanecem abertas na literatura sobre sistemas integrados BMI–LLM? |

## 6. Estratégia de busca

A busca é organizada em formato de funil, combinando quatro blocos conceituais.

### 6.1 Bloco A — Interfaces neurais

Termos relacionados a BMI, BCI e neurotecnologia:

```text
"brain-computer interface"
"brain machine interface"
"brain-machine interface"
BCI
BMI
"neural interface"
neurotechnology
neuroengineering
```

### 6.2 Bloco B — Decodificação e linguagem

Termos relacionados à interpretação de sinais neurais e produção de linguagem:

```text
"neural decoding"
"speech decoding"
"semantic decoding"
"brain-to-text"
"brain to text"
"imagined speech"
"attempted speech"
"language reconstruction"
"neural speech prosthesis"
```

### 6.3 Bloco C — Modelos de linguagem e IA

Termos relacionados a modelos de linguagem e processamento de linguagem natural:

```text
"large language model"
"large language models"
LLM
"generative AI"
"language model"
"natural language processing"
NLP
GPT
transformer
```

### 6.4 Bloco D — Riscos e dimensão humana

Termos relacionados a vieses, segurança e governança:

```text
bias
"cognitive bias"
"algorithmic bias"
uncertainty
hallucination
reliance
overreliance
trust
safety
security
privacy
"neural privacy"
neuroethics
governance
autonomy
consent
accountability
explainability
"human validation"
```

## 7. Strings conceituais de referência

### 7.1 Integração BMI/BCI com modelos de linguagem

```text
("brain-computer interface" OR "brain-machine interface" OR BCI OR BMI)
AND
("large language model" OR LLM OR "language model" OR "generative AI")
```

### 7.2 Decodificação neural e geração de linguagem

```text
("neural decoding" OR "speech decoding" OR "semantic decoding" OR "brain-to-text")
AND
("language model" OR LLM OR NLP OR transformer)
```

### 7.3 Vieses e vulnerabilidades

```text
("brain-computer interface" OR "brain-machine interface" OR "neural interface")
AND
(bias OR uncertainty OR hallucination OR overreliance OR trust)
```

### 7.4 Segurança, privacidade e governança

```text
("brain-computer interface" OR neurotechnology OR "neural data")
AND
(security OR privacy OR "neural privacy" OR neuroethics OR governance)
```

### 7.5 Validação humana

```text
("brain-to-text" OR "neural decoding" OR "neural speech prosthesis")
AND
("human validation" OR "human oversight" OR trust OR reliance OR uncertainty)
```

As strings amplas podem ser decompostas em buscas menores para reduzir ruído e melhorar a rastreabilidade.

## 8. Fontes de busca

### 8.1 APIs acadêmicas

- OpenAlex;
- Crossref;
- Semantic Scholar.

### 8.2 Mecanismos e repositórios complementares

- Google Scholar;
- IEEE Xplore;
- ACM Digital Library;
- PubMed;
- ACL Anthology;
- SpringerLink;
- ScienceDirect;
- arXiv;
- bioRxiv;
- medRxiv.

A busca nas fontes que não oferecem integração direta com o pipeline será registrada manualmente.

## 9. Áreas e venues prioritários

### 9.1 Neuroengenharia e BCI

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

### 9.2 Linguagem, NLP e IA

- ACL;
- EMNLP;
- NAACL;
- COLING;
- NeurIPS;
- ICLR;
- ICML;
- AAAI.

### 9.3 Interação humano-computador

- ACM CHI;
- ACM Transactions on Computer-Human Interaction;
- CSCW.

### 9.4 Ética e governança

- Neuroethics;
- ACM FAccT;
- AAAI/ACM AIES;
- AI and Ethics.

## 10. Período de busca

O período principal deve privilegiar publicações recentes, especialmente a partir de 2018, devido à evolução acelerada dos modelos de linguagem e das técnicas de decodificação neural.

Trabalhos anteriores a esse período poderão ser incluídos quando forem:

- fundacionais;
- amplamente citados;
- necessários para compreender a evolução de BMI/BCI;
- relevantes para conceitos de neuroética, privacidade ou interação humana.

## 11. Idiomas

Serão priorizados trabalhos em:

- inglês;
- português.

Outros idiomas poderão ser considerados quando o título, o resumo ou uma tradução confiável estiverem disponíveis.

## 12. Critérios de inclusão

| Código | Critério |
|---|---|
| CI1 | O estudo aborda BMI, BCI, interface neural, neuroengenharia ou neurotecnologia. |
| CI2 | O estudo aborda decodificação neural, comunicação, reconstrução de linguagem ou brain-to-text. |
| CI3 | O estudo utiliza ou discute LLMs, modelos de linguagem, NLP ou IA generativa em conexão com sinais neurais. |
| CI4 | O estudo discute erros, vieses, incerteza, confiança, reliance, overreliance ou validação humana. |
| CI5 | O estudo aborda segurança, privacidade neural, neuroética, autonomia, consentimento ou governança. |
| CI6 | O estudo apresenta aplicação clínica, assistiva, comunicacional, experimental ou sociotécnica relevante. |
| CI7 | O estudo apresenta texto completo, resumo informativo ou metadados suficientes para triagem. |
| CI8 | O estudo foi publicado em periódico, conferência, repositório acadêmico ou preprint relevante. |

Um artigo não precisa atender a todos os critérios. A combinação entre critérios determinará sua prioridade.

## 13. Critérios de exclusão

| Código | Critério |
|---|---|
| CE1 | O termo BMI refere-se apenas a Body Mass Index. |
| CE2 | O termo BCI aparece com significado diferente de Brain-Computer Interface. |
| CE3 | O estudo trata de IA, neurociência ou saúde apenas de forma genérica, sem relação com o recorte. |
| CE4 | O estudo trata apenas de arquitetura de LLM, sem relação com sinais neurais, interação humana ou riscos relevantes. |
| CE5 | O estudo trata apenas de classificação de sinais, sem comunicação, linguagem, decisão ou relação com o tema. |
| CE6 | O estudo não apresenta informações suficientes para análise preliminar. |
| CE7 | O registro é uma duplicata. |
| CE8 | Uma versão preliminar foi substituída por publicação mais completa. |
| CE9 | O conteúdo não possui natureza acadêmica ou técnica confiável. |

## 14. Critérios de prioridade

### Prioridade alta

O estudo combina:

- BMI/BCI ou sinais neurais;
- decodificação ou geração de linguagem;
- LLM, NLP ou modelo de linguagem;
- e pelo menos uma dimensão de risco, interação humana ou governança.

### Prioridade média

O estudo aborda:

- BMI/BCI e decodificação neural; ou
- BMI/BCI e riscos; ou
- modelos de linguagem e sinais neurais;

mas não cobre toda a integração.

### Prioridade baixa

O estudo:

- aborda apenas uma dimensão isolada;
- é muito genérico;
- possui relação apenas indireta;
- pode servir como fundamento ou contexto.

### Descartar

O estudo:

- é falso positivo;
- está fora do escopo;
- apresenta apenas coincidência terminológica;
- não oferece contribuição útil ao problema investigado.

## 15. Correntes analíticas

1. BMI/BCI e aquisição de sinais neurais.
2. Processamento e decodificação neural.
3. Reconstrução de fala, texto e significado.
4. Integração entre BMI/BCI e LLMs.
5. Aplicações clínicas e comunicação assistiva.
6. Interação humano-IA e validação humana.
7. Vieses, erros e vulnerabilidades.
8. Confiança, reliance e overreliance.
9. Segurança e privacidade neural.
10. Neuroética, autonomia e consentimento.
11. Governança, responsabilidade e rastreabilidade.
12. Métodos de avaliação e benchmarks.

## 16. Campos de extração

| Campo | Descrição |
|---|---|
| ID | Identificador interno do registro |
| Referência | Autor, ano e título |
| DOI | Digital Object Identifier |
| URL | Endereço da publicação |
| Ano | Ano de publicação |
| Venue/Fonte | Periódico, conferência ou repositório |
| Tipo de publicação | Artigo, conferência, revisão, preprint, tese etc. |
| Tipo de estudo | Teórico, empírico, experimental, revisão, survey ou estudo de caso |
| Área principal | Neuroengenharia, NLP, HCI, neuroética, segurança etc. |
| Modalidade neural | EEG, ECoG, fMRI, intracortical ou outra |
| Grau de invasividade | Invasivo, parcialmente invasivo ou não invasivo |
| População | Pessoas saudáveis, pacientes ou dados simulados |
| Tecnologia BMI/BCI | Técnica, dispositivo ou arquitetura utilizada |
| Técnica de decodificação | Método de processamento ou reconstrução |
| Modelo de linguagem | LLM, transformer, NLP clássico ou outro |
| Papel do LLM | Correção, geração, expansão, interpretação, predição ou interface |
| Aplicação | Comunicação, reabilitação, controle, decisão ou pesquisa |
| Tipo de risco | Viés, erro, segurança, privacidade, autonomia ou governança |
| Viés ou distorção | Tipo de viés ou efeito discutido |
| Incerteza | Como a incerteza é medida ou comunicada |
| Validação humana | Como ocorre revisão, confirmação ou supervisão |
| Mitigação | Estratégia proposta para reduzir riscos |
| Métricas | Acurácia, WER, ITR, latência, satisfação, confiança etc. |
| Resultados principais | Principais achados |
| Limitações | Limitações reconhecidas pelos autores |
| Relação com a pesquisa | Contribuição para o tema do projeto |
| Prioridade | Alta, média, baixa ou descartar |
| Decisão | Ler integralmente, citar, usar como apoio ou descartar |
| Observações | Notas do pesquisador |

## 17. Riscos de falso positivo

As buscas devem considerar especialmente os seguintes problemas:

### BMI

A sigla pode significar:

```text
Body Mass Index
```

Por isso, consultas com `BMI` devem ser combinadas com termos como:

```text
brain
neural
interface
neurotechnology
decoding
```

### BCI

A sigla pode aparecer em outros domínios ou nomes institucionais. Ela deve ser combinada com:

```text
brain-computer
neural
EEG
ECoG
interface
```

### LLM

A sigla pode ter usos distintos em áreas específicas. Recomenda-se combiná-la com:

```text
language model
generative AI
transformer
NLP
```

## 18. Processo de triagem

A triagem será realizada em etapas:

1. identificação dos registros;
2. remoção de duplicatas;
3. leitura de título;
4. leitura de resumo;
5. classificação temática;
6. atribuição de prioridade;
7. leitura integral dos estudos selecionados;
8. extração dos campos analíticos;
9. registro da decisão de inclusão ou exclusão.

## 19. Registro das buscas

Cada busca deverá registrar:

| Campo | Descrição |
|---|---|
| Data | Data de execução |
| Fonte | OpenAlex, Crossref, Scholar, IEEE etc. |
| Query | String utilizada |
| Camada | BMI/BCI, LLM, vieses, segurança etc. |
| Filtros | Ano, idioma, venue ou tipo |
| Quantidade recuperada | Total retornado |
| Quantidade exportada | Total salvo no pipeline |
| Candidatos relevantes | Quantidade após triagem inicial |
| Observações | Ruído, limitações ou ajustes necessários |

## 20. Avaliação da qualidade da busca

A estratégia deverá ser revisada considerando:

- quantidade de falsos positivos;
- quantidade de duplicatas;
- cobertura de trabalhos conhecidos;
- equilíbrio entre precisão e abrangência;
- distribuição por área;
- distribuição por ano;
- presença de artigos centrais;
- ausência de subtemas importantes.

## 21. Limitações do protocolo

- As APIs possuem coberturas diferentes.
- Alguns registros não apresentam resumo.
- As siglas BMI e BCI produzem falsos positivos.
- A terminologia varia entre comunidades científicas.
- Muitos trabalhos relevantes podem não utilizar explicitamente o termo LLM.
- Trabalhos recentes podem existir apenas como preprints.
- A classificação automática não substitui a avaliação humana.
- A lista de venues não é exaustiva.
- O protocolo poderá ser refinado após a busca piloto.

## 22. Produtos esperados

O levantamento deverá produzir:

1. matriz consolidada de artigos;
2. lista de trabalhos prioritários;
3. mapa de correntes de pesquisa;
4. taxonomia inicial de temas;
5. identificação de aplicações BMI–LLM;
6. identificação de riscos e vulnerabilidades;
7. catálogo de estratégias de mitigação;
8. lista preliminar de lacunas;
9. estrutura organizada no Zotero;
10. base para refinamento da questão de pesquisa.

## 23. Regra de cautela conceitual

O protocolo deve evitar formulações que tratem LLMs como agentes portadores de vieses cognitivos humanos.

São preferíveis expressões como:

- padrões enviesados produzidos pelo sistema;
- distorções introduzidas na cadeia de processamento;
- efeitos análogos a vieses;
- amplificação de padrões dos dados;
- influência sobre julgamento e interpretação humana;
- confiança excessiva na saída do sistema;
- vulnerabilidades sociotécnicas;
- riscos na interação entre sistema, usuário e contexto.
