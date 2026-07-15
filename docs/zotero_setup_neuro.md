# Configuração do Zotero — BMI/BCI, LLMs, Neurotecnologia e Vieses

## 1. Objetivo

Este documento define uma estrutura inicial para organizar, classificar e revisar a literatura utilizada no projeto **Neuro Literature Mapper**.

A organização proposta deve apoiar:

- triagem de artigos;
- identificação de temas centrais;
- separação entre estudos técnicos, humanos e normativos;
- registro de decisões de inclusão e exclusão;
- preparação da matriz analítica;
- recuperação rápida das referências;
- exportação posterior para escrita acadêmica.

A estrutura poderá ser refinada depois da primeira busca piloto.

---

## 2. Biblioteca principal

Nome sugerido da biblioteca ou coleção principal:

```text
BMI-BCI, LLMs, Neurotecnologia e Vieses
```

Estrutura recomendada:

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
├── 13 - Métodos, Métricas e Benchmarks
├── 90 - Metodologia
├── 91 - Fundamentos e Clássicos
├── 92 - Apoio / Áreas Vizinhas
└── 99 - Descartados
```

Um mesmo item pode estar em mais de uma coleção sem duplicação do registro.

---

## 3. Descrição das coleções

### 00 - Inbox / Triagem

Ponto inicial para todos os registros importados.

Usar para:

- itens ainda não avaliados;
- importações automáticas;
- resultados de APIs;
- artigos salvos durante buscas manuais;
- registros com metadados incompletos.

O item deve sair desta coleção somente após a triagem inicial.

### 01 - BMI e BCI

Trabalhos gerais sobre:

- Brain-Computer Interfaces;
- Brain-Machine Interfaces;
- interfaces neurais;
- arquiteturas de BCI/BMI;
- sistemas invasivos e não invasivos;
- dispositivos e plataformas.

### 02 - Aquisição e Processamento de Sinais Neurais

Trabalhos sobre:

- EEG;
- ECoG;
- fMRI;
- implantes intracorticais;
- pré-processamento;
- filtragem;
- extração de características;
- qualidade do sinal;
- ruído e artefatos.

### 03 - Decodificação Neural

Trabalhos sobre:

- neural decoding;
- semantic decoding;
- speech decoding;
- imagined speech;
- attempted speech;
- reconstrução de sinais;
- predição de intenção;
- interpretação de representações neurais.

### 04 - Brain-to-Text e Comunicação

Trabalhos relacionados a:

- brain-to-text;
- comunicação assistiva;
- próteses de fala;
- geração de texto a partir de sinais neurais;
- reconstrução de fala;
- comunicação para pessoas com limitações motoras ou de fala.

### 05 - LLMs e Processamento de Linguagem

Trabalhos sobre:

- Large Language Models;
- modelos de linguagem;
- transformers;
- NLP;
- geração de linguagem;
- correção e expansão textual;
- predição linguística;
- modelos multimodais.

### 06 - Integração BMI-LLM

Coleção central do projeto.

Incluir estudos que combinem diretamente:

- BMI/BCI;
- sinais ou dados neurais;
- decodificação;
- modelos de linguagem;
- geração ou interpretação de conteúdo;
- interfaces conversacionais;
- apoio à comunicação ou decisão.

### 07 - Interação Humano-IA

Trabalhos sobre:

- interação usuário-sistema;
- confiança;
- reliance;
- overreliance;
- supervisão;
- validação humana;
- experiência do usuário;
- interpretação de saídas;
- tomada de decisão mediada por IA.

### 08 - Vieses e Vulnerabilidades

Trabalhos sobre:

- vieses nos dados;
- vieses algorítmicos;
- vieses cognitivos do usuário;
- distorções de julgamento;
- propagação de erros;
- amplificação de padrões;
- alucinações;
- incerteza;
- vulnerabilidades sociotécnicas.

### 09 - Segurança e Privacidade Neural

Trabalhos sobre:

- neural privacy;
- proteção de dados neurais;
- ataques adversariais;
- uso indevido de sinais neurais;
- segurança de dispositivos;
- integridade dos dados;
- confidencialidade;
- controle de acesso;
- vazamento de informações sensíveis.

### 10 - Neuroética e Governança

Trabalhos sobre:

- neuroética;
- autonomia;
- consentimento;
- responsabilidade;
- explicabilidade;
- accountability;
- governança;
- rastreabilidade;
- direitos neurais;
- limites de uso;
- regulamentação.

### 11 - Aplicações Clínicas e Assistivas

Trabalhos sobre:

- reabilitação;
- comunicação assistiva;
- aplicações clínicas;
- pacientes com paralisia;
- doenças neurodegenerativas;
- lesões medulares;
- suporte terapêutico;
- tecnologias assistivas.

### 12 - Revisões e Surveys

Incluir:

- revisões sistemáticas;
- scoping reviews;
- surveys;
- revisões narrativas;
- roadmaps;
- position papers;
- estudos de estado da arte.

### 13 - Métodos, Métricas e Benchmarks

Trabalhos focados em:

- acurácia;
- Word Error Rate — WER;
- Information Transfer Rate — ITR;
- latência;
- robustez;
- generalização;
- avaliação de usabilidade;
- avaliação de confiança;
- benchmarks e datasets.

### 90 - Metodologia

Materiais sobre:

- revisão de literatura;
- protocolos de busca;
- snowballing;
- triagem;
- análise temática;
- qualidade metodológica;
- Zotero;
- organização bibliográfica.

### 91 - Fundamentos e Clássicos

Trabalhos fundacionais sobre:

- BCI/BMI;
- neuroengenharia;
- NLP;
- transformers;
- confiança em automação;
- vieses;
- interação humano-computador;
- ética em neurotecnologia.

### 92 - Apoio / Áreas Vizinhas

Trabalhos relevantes, mas não centrais, sobre:

- neurociência;
- ciência cognitiva;
- robótica;
- filosofia da mente;
- direito;
- bioética;
- sistemas sociotécnicos;
- ciência de dados.

### 99 - Descartados

Itens excluídos da análise principal.

Manter nesta coleção apenas quando for útil registrar o motivo do descarte.

Exemplos:

- falso positivo;
- duplicata;
- sem relação com o tema;
- metadados insuficientes;
- versão substituída;
- BMI com significado de Body Mass Index.

---

## 4. Sistema de tags

Usar tags curtas, padronizadas e preferencialmente em inglês para facilitar a correspondência com títulos e resumos.

### 4.1 Tags de status

```text
status:inbox
status:screened
status:full-text
status:included
status:excluded
status:duplicate
status:needs-review
```

### 4.2 Tags de prioridade

```text
priority:high
priority:medium
priority:low
```

### 4.3 Tags de decisão

```text
decision:read
decision:cite
decision:support
decision:exclude
```

### 4.4 Tags do domínio neural

```text
domain:bci
domain:bmi
domain:neurotechnology
domain:neuroengineering
domain:neural-interface
```

### 4.5 Tags de modalidade neural

```text
signal:eeg
signal:ecog
signal:fmri
signal:intracortical
signal:meg
signal:fnirs
signal:multimodal
```

### 4.6 Tags de invasividade

```text
invasiveness:invasive
invasiveness:partially-invasive
invasiveness:non-invasive
```

### 4.7 Tags de decodificação

```text
decoding:neural
decoding:speech
decoding:semantic
decoding:imagined-speech
decoding:attempted-speech
decoding:brain-to-text
```

### 4.8 Tags de IA e linguagem

```text
ai:llm
ai:generative-ai
ai:nlp
ai:transformer
ai:language-model
ai:multimodal
```

### 4.9 Tags de interação humana

```text
human:interaction
human:trust
human:reliance
human:overreliance
human:validation
human:oversight
human:decision-making
human:usability
```

### 4.10 Tags de vieses e vulnerabilidades

```text
risk:bias
risk:cognitive-bias
risk:algorithmic-bias
risk:confirmation-bias
risk:anchoring
risk:hallucination
risk:uncertainty
risk:error-propagation
risk:automation-bias
```

### 4.11 Tags de segurança e governança

```text
governance:privacy
governance:neural-privacy
governance:security
governance:neuroethics
governance:consent
governance:autonomy
governance:accountability
governance:explainability
governance:traceability
governance:regulation
```

### 4.12 Tags de aplicação

```text
application:assistive-communication
application:clinical
application:rehabilitation
application:speech-prosthesis
application:decision-support
application:research
```

### 4.13 Tags de tipo de estudo

```text
study:experimental
study:empirical
study:theoretical
study:survey
study:review
study:systematic-review
study:scoping-review
study:case-study
study:position-paper
study:preprint
```

---

## 5. Uso de cores nas tags

O Zotero permite destacar até nove tags com cores.

Sugestão:

| Cor | Tag | Uso |
|---|---|---|
| 1 | `priority:high` | Trabalho central |
| 2 | `priority:medium` | Trabalho relevante |
| 3 | `status:needs-review` | Requer revisão |
| 4 | `status:full-text` | Texto integral obtido |
| 5 | `status:included` | Incluído na análise |
| 6 | `status:excluded` | Excluído |
| 7 | `domain:bci` | BCI/BMI |
| 8 | `ai:llm` | LLM/NLP |
| 9 | `governance:neuroethics` | Ética e governança |

As cores devem ser usadas apenas para sinalização rápida. A informação principal deve continuar registrada na tag textual.

---

## 6. Fluxo de triagem no Zotero

### Etapa 1 — Importação

Ao importar um item:

1. adicionar à coleção `00 - Inbox / Triagem`;
2. aplicar `status:inbox`;
3. verificar título, autores, ano e DOI;
4. anexar o PDF, quando disponível;
5. corrigir metadados básicos.

### Etapa 2 — Triagem por título e resumo

Avaliar:

- relação com BMI/BCI;
- relação com sinais neurais;
- relação com linguagem;
- presença de LLM, NLP ou modelos de linguagem;
- riscos, vieses, segurança, privacidade ou governança;
- utilidade para o problema de pesquisa.

Depois:

- aplicar prioridade;
- adicionar coleções temáticas;
- adicionar tags;
- registrar uma nota breve;
- retirar `status:inbox`;
- aplicar `status:screened`.

### Etapa 3 — Leitura integral

Para itens prioritários:

1. obter e anexar o texto integral;
2. aplicar `status:full-text`;
3. criar nota de leitura;
4. extrair contribuição, método, resultados e limitações;
5. relacionar o estudo às subquestões do protocolo;
6. decidir pela inclusão ou exclusão.

### Etapa 4 — Decisão

Para itens incluídos:

```text
status:included
decision:cite
```

Para itens de apoio:

```text
status:included
decision:support
```

Para itens excluídos:

```text
status:excluded
decision:exclude
```

Mover os excluídos para `99 - Descartados` apenas quando for útil preservar o registro.

---

## 7. Modelo de nota de triagem

Criar uma nota filha com o título:

```text
Triagem
```

Modelo:

```markdown
## Relevância preliminar

- Relação com BMI/BCI:
- Relação com decodificação neural:
- Relação com LLM/NLP:
- Relação com vieses ou riscos:
- Relação com interação humana:
- Relação com segurança, privacidade ou governança:

## Decisão

- Prioridade:
- Decisão:
- Motivo:

## Observações

-
```

---

## 8. Modelo de nota de leitura

Criar uma nota filha com o título:

```text
Nota de leitura
```

Modelo:

```markdown
## Referência

Autor, ano, título.

## Objetivo

-

## Problema investigado

-

## Método

-

## Modalidade neural

-

## Tecnologia ou arquitetura

-

## Papel do modelo de linguagem

-

## Principais resultados

-

## Vieses, erros ou vulnerabilidades

-

## Confiança e validação humana

-

## Segurança, privacidade e governança

-

## Estratégias de mitigação

-

## Limitações

-

## Relação com as subquestões

- SQ01:
- SQ02:
- SQ03:
- SQ04:
- SQ05:
- SQ06:
- SQ07:
- SQ08:

## Contribuição para a pesquisa

-

## Trechos relevantes

Registrar apenas pequenos trechos necessários, com página.

## Decisão final

- Citar:
- Usar como apoio:
- Descartar:
```

---

## 9. Critérios de prioridade

### Alta prioridade

Aplicar `priority:high` quando o trabalho combinar:

- BMI/BCI ou sinais neurais;
- decodificação ou reconstrução de linguagem;
- LLM, NLP ou modelo de linguagem;
- risco, interação humana, privacidade, segurança ou governança.

### Média prioridade

Aplicar `priority:medium` quando o trabalho abordar diretamente duas das seguintes dimensões:

- BMI/BCI;
- decodificação neural;
- linguagem;
- LLM/NLP;
- vieses;
- segurança;
- interação humana;
- neuroética.

### Baixa prioridade

Aplicar `priority:low` quando o trabalho:

- oferecer apenas contexto;
- abordar uma única dimensão;
- apresentar relação indireta;
- for útil como fundamento.

---

## 10. Critérios de descarte

Registrar o motivo com uma tag específica:

```text
exclude:false-positive
exclude:body-mass-index
exclude:wrong-bci
exclude:out-of-scope
exclude:duplicate
exclude:no-metadata
exclude:replaced-version
exclude:not-academic
```

Quando possível, adicionar uma nota curta explicando a decisão.

Exemplo:

```text
Excluído: BMI significa Body Mass Index e não Brain-Machine Interface.
```

---

## 11. Convenções de metadados

### Títulos

- manter o título original;
- evitar alterações manuais desnecessárias;
- corrigir somente problemas evidentes de capitalização ou codificação.

### Autores

- verificar ordem e separação dos nomes;
- evitar registros com todos os autores em um único campo;
- corrigir nomes institucionais quando necessário.

### DOI

- usar apenas o identificador;
- evitar prefixos duplicados;
- conferir se o DOI pertence à versão analisada.

Exemplo:

```text
10.1234/example.2026.001
```

### URL

- priorizar a página oficial da publicação;
- evitar URLs temporárias;
- manter o endereço do preprint quando essa for a versão analisada.

### Data

- confirmar o ano da versão efetivamente utilizada;
- distinguir preprint de publicação final.

### Venue

- preencher o nome completo do periódico ou conferência;
- evitar misturar editora, base de dados e venue no mesmo campo.

---

## 12. PDFs e anexos

Para cada item prioritário:

- anexar o PDF integral;
- usar o recurso de recuperação de metadados quando aplicável;
- verificar se o PDF corresponde ao registro;
- evitar anexar várias cópias idênticas;
- manter material suplementar como anexo separado.

Nome sugerido para PDFs exportados:

```text
Autor_Ano_TituloCurto.pdf
```

Exemplo:

```text
Silva_2026_NeuralSpeechDecoding.pdf
```

O Zotero normalmente administra os nomes internamente; a convenção é mais importante quando os arquivos são exportados.

---

## 13. Duplicatas e versões

Usar a área **Duplicate Items** do Zotero para combinar registros.

Antes de mesclar:

- conferir DOI;
- conferir título;
- conferir ano;
- conferir autores;
- preservar o registro com melhores metadados;
- preservar notas, tags e anexos.

Quando houver preprint e versão publicada:

- preferir a versão revisada e publicada;
- manter o preprint somente quando houver diferenças relevantes;
- relacionar os dois itens por meio de nota ou item relacionado;
- registrar `exclude:replaced-version` quando a versão preliminar for descartada.

---

## 14. Itens relacionados

Usar o recurso **Related** do Zotero para conectar:

- preprint e artigo publicado;
- artigo e dataset;
- artigo e material suplementar;
- artigo metodológico e aplicação;
- revisão e estudos centrais;
- trabalhos da mesma linha de pesquisa;
- estudo original e replicação.

---

## 15. Pesquisas salvas sugeridas

Criar pesquisas salvas para acompanhamento.

### Alta prioridade ainda não lida

Condições:

```text
Tag contém priority:high
Tag não contém status:full-text
```

### Incluídos sem nota de leitura

Condições:

```text
Tag contém status:included
Nota não contém Nota de leitura
```

### Itens sobre integração BMI-LLM

Condição:

```text
Coleção é 06 - Integração BMI-LLM
```

### Segurança e privacidade

Condições:

```text
Tag contém governance:privacy
OU
Tag contém governance:security
OU
Tag contém governance:neural-privacy
```

### Itens que precisam de revisão

Condição:

```text
Tag contém status:needs-review
```

### Preprints

Condição:

```text
Tag contém study:preprint
```

---

## 16. Importação dos resultados do pipeline

O pipeline poderá produzir arquivos CSV com resultados das APIs.

Fluxo recomendado:

1. abrir o CSV;
2. revisar falsos positivos;
3. ordenar por prioridade;
4. localizar os itens selecionados no Zotero Connector ou por DOI;
5. importar apenas registros relevantes;
6. adicionar à coleção `00 - Inbox / Triagem`;
7. aplicar tags temáticas;
8. registrar a origem da busca em uma nota.

Exemplo de nota:

```text
Origem: OpenAlex
Query: "brain-computer interface" AND "large language model"
Data da busca: AAAA-MM-DD
Camada: Integração BMI-LLM
```

---

## 17. Integração com a matriz analítica

As informações do Zotero devem apoiar o preenchimento de:

```text
docs/matriz_analitica_neuro.md
```

Campos prioritários:

- referência;
- ano;
- venue;
- tipo de estudo;
- modalidade neural;
- grau de invasividade;
- técnica de decodificação;
- modelo de linguagem;
- papel do LLM;
- aplicação;
- vieses e vulnerabilidades;
- confiança e validação humana;
- segurança e privacidade;
- governança e neuroética;
- mitigação;
- resultados;
- limitações;
- prioridade;
- decisão.

O Zotero organiza a literatura. A matriz consolida a análise comparativa.

---

## 18. Extensões opcionais

### Better BibTeX for Zotero

Pode ser usado para:

- gerar chaves de citação estáveis;
- exportar BibTeX ou BibLaTeX;
- manter arquivos bibliográficos atualizados;
- integrar Zotero com LaTeX, Markdown ou editores acadêmicos.

Padrão de chave sugerido:

```text
authEtAlYearShortTitle
```

Exemplo:

```text
silvaEtAl2026NeuralDecoding
```

### Zotero Connector

Usar o conector do navegador para:

- importar artigos;
- capturar DOI;
- salvar páginas de periódicos;
- anexar PDFs;
- recuperar metadados.

---

## 19. Cuidados com dados sensíveis

O Zotero deve armazenar apenas literatura e notas acadêmicas.

Não registrar:

- dados pessoais de participantes;
- sinais neurais identificáveis;
- informações clínicas privadas;
- credenciais;
- chaves de APIs;
- documentos protegidos sem autorização.

As notas devem evitar incluir dados sensíveis provenientes de estudos ou projetos em andamento.

---

## 20. Rotina de manutenção

### Após cada sessão de busca

- revisar novos itens;
- corrigir metadados;
- remover duplicatas;
- aplicar tags de status;
- registrar origem da busca.

### Semanalmente

- esvaziar ou reduzir a Inbox;
- revisar itens de alta prioridade;
- verificar PDFs ausentes;
- revisar `status:needs-review`;
- atualizar a matriz analítica.

### Antes da escrita acadêmica

- confirmar as versões citadas;
- verificar DOI, autores e ano;
- revisar notas;
- validar chaves de citação;
- remover referências que não serão utilizadas;
- exportar backup da biblioteca.

---

## 21. Backup

Manter cópias regulares:

- sincronização da biblioteca;
- exportação em formato Zotero RDF;
- exportação bibliográfica em BibTeX ou CSL JSON;
- cópia das notas e da matriz analítica;
- backup do diretório do projeto.

Não usar apenas o Git para armazenar a biblioteca completa do Zotero ou seus PDFs.

---

## 22. Regra de cautela conceitual

Na classificação e nas notas, evitar tratar LLMs como agentes que possuem vieses cognitivos humanos.

Preferir formulações como:

- padrões enviesados produzidos pelo sistema;
- vieses presentes nos dados;
- amplificação de distorções;
- erros de decodificação;
- efeitos análogos a vieses;
- influência sobre julgamento humano;
- confiança excessiva na saída;
- vulnerabilidades da interação;
- riscos sociotécnicos;
- falhas na cadeia BMI–LLM.

---

## 23. Resultado esperado

Ao final da organização, a biblioteca deverá permitir:

1. localizar rapidamente os estudos centrais;
2. distinguir trabalhos técnicos, humanos e normativos;
3. acompanhar o status de leitura;
4. identificar lacunas;
5. relacionar artigos às subquestões;
6. recuperar evidências para a escrita;
7. registrar decisões de inclusão e exclusão;
8. manter rastreabilidade entre busca, triagem, leitura e síntese.
