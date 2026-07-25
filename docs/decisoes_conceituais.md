# Decisões conceituais — Neuro Literature Mapper

## 1. Objetivo

Este documento registra as principais decisões conceituais e metodológicas adotadas no projeto `neuro-literature-mapper`.

Seu objetivo é preservar:

- a justificativa das regras de classificação;
- os limites entre as categorias temáticas;
- as decisões tomadas durante a auditoria dos resultados;
- os critérios usados para reduzir falsos positivos;
- as situações que exigem adjudicação humana;
- a evolução conceitual do pipeline.

Este documento complementa:

- `docs/protocolo_neuro.md`;
- `docs/matriz_analitica_neuro.md`;
- `config/taxonomy_neuro.yaml`;
- `docs/releases/v4.3f.md`.

## 2. Contexto da consolidação

As decisões abaixo foram consolidadas durante o desenvolvimento da versão v4.3f.

```text
Versão do pipeline: v4.3f
Versão da taxonomia: 1.6
Corpus analisado: 864 registros
Corpus central automatizado: 255 registros
Corpus central adjudicado: 254 registros
Casos de regressão específicos da v4.3f: 28
```

## 3. Categorias de classificação

| Código | Categoria |
|---|---|
| A1 | Integração BMI/BCI e modelos de linguagem |
| A2 | Decodificação neural de linguagem |
| A3 | Riscos e governança em BMI/BCI |
| B | Literatura de apoio |
| D | Descartar |

---

## DEC-001 — Não atribuir vieses cognitivos humanos aos LLMs

**Status:** adotada

**Decisão:** o projeto não deve afirmar que modelos de linguagem possuem vieses cognitivos humanos.

**Justificativa:** vieses cognitivos são conceitos relacionados a processos humanos de julgamento, percepção e tomada de decisão. Um modelo computacional não deve ser descrito automaticamente como possuidor desses mesmos processos.

**Formulações preferidas:**

- padrões enviesados produzidos pelo sistema;
- distorções reproduzidas ou amplificadas;
- efeitos análogos a vieses;
- influência sobre o julgamento humano;
- confiança excessiva na saída do sistema;
- vulnerabilidades sociotécnicas;
- padrões decorrentes dos dados, treinamento ou arquitetura.

**Impacto:** essa cautela deve ser aplicada no protocolo, na matriz analítica, nas publicações e na interpretação dos resultados.

---

## DEC-002 — A1 exige integração operacional

**Status:** adotada

**Decisão:** um estudo somente deve ser classificado como A1 quando o modelo de linguagem ou a tecnologia linguística participar operacionalmente do sistema neural.

**Exemplos de participação operacional:**

- o modelo de linguagem recebe representações derivadas de EEG, ECoG, fMRI ou sinais intracorticais;
- o modelo gera texto a partir de pistas neurais ou semânticas;
- o modelo corrige, completa ou prediz palavras em uma BCI;
- o modelo atua como decoder, gerador ou componente de recuperação semântica;
- o modelo é condicionado por sinais ou representações neurais;
- a saída neural é utilizada para gerar linguagem por meio do modelo.

**Não é suficiente:**

- mencionar LLM no resumo;
- citar modelos de linguagem em trabalhos relacionados;
- comparar o cérebro com representações de modelos;
- utilizar a palavra `transformer`;
- afirmar que a arquitetura foi inspirada em NLP.

---

## DEC-003 — Menção a tecnologia linguística não implica A1

**Status:** adotada

**Decisão:** termos como os seguintes não são evidência suficiente de integração BMI/BCI–LLM:

```text
LLM
large language model
language model
transformer
generative AI
NLP
natural language processing
text generation
```

**Justificativa:** esses termos podem aparecer como:

- referências a estudos anteriores;
- descrição de arquiteturas;
- comparação metodológica;
- contextualização;
- possibilidade de trabalho futuro;
- tecnologia externa ao objeto principal do estudo.

**Impacto:** a classificação deve buscar evidência de relação operacional entre tecnologia linguística e domínio neural.

---

## DEC-004 — Comparações cérebro–modelo permanecem em B

**Status:** adotada

**Decisão:** estudos que comparam representações internas de modelos com representações cerebrais devem permanecer em B quando não apresentam uma integração operacional BMI/BCI–LLM.

**Exemplos:**

- alinhamento entre ativações cerebrais e embeddings;
- similaridade representacional entre cérebro e LLM;
- convergência de hierarquias de representação;
- investigação sobre modelos que espelham processamento linguístico humano;
- análise de representações visuais cerebrais alinhadas a modelos.

**Justificativa:** esses estudos podem ser relevantes para a fundamentação teórica, mas não implementam necessariamente um sistema integrado.

---

## DEC-005 — Transferência de arquitetura de NLP não caracteriza A1

**Status:** adotada

**Decisão:** o uso de uma arquitetura frequentemente utilizada em NLP não significa que o estudo utilize um modelo de linguagem.

**Exemplos:**

- transformer aplicado à classificação de EEG;
- mecanismo de atenção aplicado a sinais neurais;
- encoder originalmente criado para texto e reutilizado em outro domínio;
- modelo descrito como amplamente utilizado em tarefas de NLP.

**Justificativa:** uma arquitetura computacional pode ser transferida para outro domínio sem manter função linguística.

**Classificação esperada:** B, salvo quando houver evidência adicional de integração operacional com linguagem.

---

## DEC-006 — A2 exige decodificação neural de linguagem

**Status:** adotada

**Decisão:** A2 deve ser utilizada quando a contribuição central transforma sinais neurais em uma saída linguística ou comunicacional.

**Saídas consideradas linguísticas:**

- fala;
- texto;
- palavras;
- sentenças;
- fonemas;
- soletração;
- escrita;
- linguagem imaginada;
- linguagem tentada;
- reconstrução semântica;
- comunicação assistiva.

**Exemplos de tarefas compatíveis:**

```text
brain-to-text
EEG-to-text
speech decoding
semantic decoding
language decoding
imagined speech
attempted speech
silent speech
speech neuroprosthesis
neural speech prosthesis
```

---

## DEC-007 — A1 tem precedência quando o modelo de linguagem é operacional

**Status:** adotada

**Decisão:** quando um estudo realiza decodificação neural para texto ou fala e também integra operacionalmente um modelo de linguagem, a classificação principal será A1.

**Exemplo conceitual:**

```text
Sinal neural
    ↓
Extração de representação ou palavras-chave
    ↓
Modelo de linguagem
    ↓
Texto gerado
```

**Justificativa:** embora o estudo também pertença ao domínio de decodificação neural de linguagem, sua característica distintiva para o projeto é a integração com o modelo de linguagem.

**Exemplos auditados:**

- sistema EEG-to-text construído sobre modelo de linguagem;
- modelo de linguagem usado como decoder;
- geração por LLM condicionada por palavras ou pistas extraídas de EEG;
- recuperação semântica neural seguida de geração linguística.

---

## DEC-008 — Decodificação neural genérica permanece em B

**Status:** adotada

**Decisão:** estudos de decodificação neural sem uma saída linguística ou comunicacional permanecem em B.

**Exemplos:**

- reconstrução de imagens;
- decodificação de música;
- classificação motora;
- identificação de atividades;
- reconstrução de cenas;
- detecção de emoções;
- previsão de variáveis comportamentais;
- análise genérica de arquiteturas de neural decoding.

**Justificativa:** o projeto possui foco específico em linguagem, integração com modelos linguísticos e dimensões de risco e governança.

---

## DEC-009 — Geração de descrições textuais pode ser A2

**Status:** adotada

**Decisão:** um estudo pode ser classificado como A2 quando decodifica atividades neurais em descrições textuais coerentes, mesmo que a tarefa original envolva estímulos visuais.

**Condição:** a contribuição deve incluir efetivamente a produção ou reconstrução de conteúdo textual a partir das atividades neurais.

**Limite:** reconstrução apenas visual, sem saída linguística, permanece em B.

---

## DEC-010 — A3 exige contribuição central sobre riscos ou governança

**Status:** adotada

**Decisão:** a presença de termos como `privacy`, `security`, `ethics` ou `governance` não é suficiente para classificar um estudo como A3.

A3 exige que a contribuição central trate de temas como:

- privacidade neural;
- privacidade mental;
- neurorights;
- autonomia;
- consentimento;
- neuroética;
- segurança de dados neurais;
- ameaças ou vulnerabilidades de BCI;
- governança;
- responsabilidade;
- uso indevido de neurotecnologia;
- proteção de dados cerebrais.

**Exemplos de contribuição central:**

- análise estruturada de riscos;
- proposta de framework de governança;
- investigação de privacidade mental;
- modelo de ameaças para BCI;
- discussão específica de direitos neurais;
- estudo de riscos éticos ou sociais da neurotecnologia.

---

## DEC-011 — Segurança de aplicação não implica A3

**Status:** adotada

**Decisão:** aplicações de segurança convencionais baseadas em EEG ou BCI não devem ser automaticamente classificadas como A3.

**Exemplos classificados como B:**

- autenticação de usuários;
- identificação biométrica por EEG;
- verificação de identidade;
- controle de acesso;
- segurança de dispositivos;
- detecção de fraude;
- reconhecimento de usuários.

**Justificativa:** nesses estudos, segurança é normalmente o objetivo da aplicação, e não uma análise dos riscos, implicações éticas ou governança da neurotecnologia.

---

## DEC-012 — Revisões amplas permanecem em B

**Status:** adotada

**Decisão:** surveys, revisões sistemáticas, tutoriais e panoramas gerais permanecem em B quando não possuem como contribuição central uma das categorias A1, A2 ou A3.

**Exemplos:**

- visão geral de BCI;
- revisão ampla de neural decoding;
- tutorial introdutório sobre interfaces cérebro-computador;
- survey sobre metaverso e BCI;
- revisão de sistemas de neuroreabilitação;
- panorama geral de arquiteturas.

**Justificativa:** essas publicações podem ser úteis como literatura de apoio, mas seu escopo amplo não implica aderência direta ao núcleo investigado.

---

## DEC-013 — Relatórios clínicos não equivalem automaticamente a brain-to-text

**Status:** adotada

**Decisão:** modelos que transformam EEG em narrativas, interpretações ou relatórios clínicos não devem ser automaticamente classificados como A2.

**Distinção:**

```text
Decodificação neural de linguagem:
sinal cerebral associado a intenção, fala ou conteúdo linguístico
    ↓
fala, palavra, sentença ou texto reconstruído

Interpretação clínica:
sinal fisiológico
    ↓
classificação, descrição ou relatório sobre o estado clínico
```

**Justificativa:** a produção de texto sobre um sinal não significa que o conteúdo linguístico tenha sido decodificado do cérebro.

**Classificação esperada:** B, salvo quando houver evidência explícita de reconstrução da linguagem neural.

---

## DEC-014 — BCI abreviada exige contexto neural válido

**Status:** adotada

**Decisão:** a sigla `BCI` não deve ser interpretada isoladamente como Brain-Computer Interface.

A sigla deve aparecer acompanhada de contexto como:

- brain;
- neural;
- EEG;
- ECoG;
- fMRI;
- P300;
- SSVEP;
- motor imagery;
- speller;
- spelling;
- word prediction;
- neurotechnology;
- neuroengineering.

**Justificativa:** a sigla pode aparecer com outros significados ou sem contexto suficiente.

---

## DEC-015 — Relações operacionais devem ser avaliadas por sentença

**Status:** adotada

**Decisão:** sempre que possível, a evidência de integração deve aparecer na mesma sentença que contém:

1. a tecnologia linguística;
2. o domínio neural ou uma interface válida;
3. uma relação operacional.

**Exemplos de relações operacionais:**

```text
uses
using
utilizes
utilizing
employs
integrates
incorporates
conditions
generates
decodes
built on
based on
```

**Justificativa:** analisar apenas o documento completo pode combinar menções não relacionadas que aparecem em partes diferentes do resumo.

---

## DEC-016 — Menções a trabalhos anteriores não contam como contribuição atual

**Status:** adotada

**Decisão:** uma sentença que afirma que estudos anteriores utilizaram modelos de linguagem não deve fazer o artigo atual ser classificado como A1.

**Exemplos de indicadores:**

- previous studies;
- prior work;
- earlier approaches;
- existing methods;
- past research;
- related work.

**Impacto:** o classificador deve diferenciar a tecnologia empregada pelo trabalho atual das tecnologias apenas citadas como antecedentes.

---

## DEC-017 — Resumos ausentes aumentam a necessidade de revisão humana

**Status:** adotada

**Decisão:** quando o resumo estiver ausente, a classificação baseada apenas no título deve ser tratada como preliminar.

**Consequências:**

- o título pode promover registros inadequadamente;
- estudos centrais podem permanecer em B;
- uma decisão final pode exigir recuperação externa do resumo;
- regras excessivamente específicas não devem ser criadas para corrigir um único registro sem contexto suficiente.

---

## DEC-018 — A classificação automática é pré-triagem

**Status:** adotada

**Decisão:** as categorias sugeridas pelo pipeline não constituem decisão final de inclusão acadêmica.

O processo correto é:

```text
Busca automatizada
    ↓
Higienização
    ↓
Deduplicação
    ↓
Classificação automática
    ↓
Auditoria
    ↓
Adjudicação humana
    ↓
Triagem de título e resumo
    ↓
Leitura integral
    ↓
Decisão final de inclusão
```

**Impacto:** os 254 estudos centrais da v4.3f constituem o corpus candidato à triagem humana, não o conjunto definitivo de estudos incluídos.

---

## DEC-019 — Adjudicação manual deve ser registrada separadamente

**Status:** adotada

**Decisão:** alterações humanas realizadas após a classificação automática devem ser preservadas como adjudicações explícitas.

A adjudicação deve registrar:

- título do estudo;
- classificação automatizada;
- classificação final;
- justificativa;
- fonte utilizada na revisão;
- data da decisão;
- responsável pela decisão.

**Justificativa:** sobrescrever silenciosamente o resultado automatizado reduz a rastreabilidade e impede avaliar o desempenho real do classificador.

---

## DEC-020 — Adjudicação do estudo sobre decodificação entre idiomas

**Status:** adotada na v4.3f

**Estudo:**

```text
Brain decoding in multiple languages:
Can cross-language brain decoding work?
```

**Classificação automatizada:**

```text
A2-central-decoding-linguagem
```

**Classificação final:**

```text
B-apoio
```

**Justificativa:** o estudo foi tratado como uma visão geral sobre decodificação cerebral entre idiomas, sem apresentação de um novo sistema de decodificação neural de linguagem.

**Decisão de implementação:** não foi criada uma regra automática específica para esse título.

**Motivo:** uma regra baseada apenas em formulação interrogativa, ausência de resumo ou termos como `cross-language` poderia introduzir novos falsos negativos.

---

## DEC-021 — O corpus automatizado e o corpus adjudicado devem permanecer distintos

**Status:** adotada

**Decisão:** a documentação deve apresentar separadamente:

```text
Corpus central automatizado: 255
Corpus central adjudicado: 254
```

**Justificativa:** essa separação permite:

- medir o resultado real do classificador;
- identificar intervenções humanas;
- avaliar futuras versões;
- reproduzir a auditoria;
- evitar ocultar correções manuais.

---

## DEC-022 — Resultados públicos não devem incluir resumos integrais

**Status:** adotada

**Decisão:** o artefato público anexado à GitHub Release não contém a coluna `abstract`.

**Justificativa:**

- reduzir riscos relacionados à redistribuição de conteúdo;
- manter a release focada em metadados e resultados derivados;
- preservar localmente o conjunto utilizado na análise;
- permitir auditoria por título, DOI, URL, classificação e demais metadados.

**Artefato público:**

```text
resultados_neuro_v4_3f_union_p5_p10_adjudicado_publico.csv
```

---

## DEC-023 — Artefatos publicados devem possuir checksum

**Status:** adotada

**Decisão:** os artefatos anexados à release devem possuir hashes SHA-256.

**Arquivo de verificação:**

```text
checksums_v4_3f.sha256
```

**Justificativa:** os checksums permitem verificar integridade, reprodutibilidade e ausência de alterações posteriores.

---

## 4. Regras de precedência consolidadas

A classificação principal segue esta lógica conceitual:

```text
1. Registro inválido ou fora do escopo
   → D

2. Contribuição central sobre riscos, ética ou governança neural
   → A3

3. Modelo de linguagem operacionalmente integrado a sinais ou sistema neural
   → A1

4. Decodificação neural com saída linguística, sem integração operacional de modelo de linguagem
   → A2

5. Relação indireta, genérica, comparativa ou contextual
   → B
```

A ordem implementada no código pode conter verificações técnicas adicionais para evitar conflitos e falsos positivos. A interpretação metodológica deve respeitar as definições acima.

## 5. Política para novas decisões

Novas decisões conceituais devem ser registradas quando:

- uma regra alterar múltiplos registros;
- um falso positivo revelar ambiguidade recorrente;
- uma classe precisar ter sua definição modificada;
- houver mudança de precedência;
- uma adjudicação manual afetar o corpus final;
- uma nova versão da taxonomia for publicada.

Cada nova decisão deve incluir:

```text
Identificador
Status
Contexto
Decisão
Justificativa
Impacto
Exemplos
Versão de introdução
```

## 6. Histórico

| Versão | Mudança |
|---|---|
| v4.3 | Introdução das regras de higiene, deduplicação e regressão |
| v4.3d | Recalibração das regras semânticas |
| v4.3e | Refinamento da classificação central |
| v4.3e.1 | Correções pontuais de classificação |
| v4.3f | Consolidação das decisões A1, A2, A3, B e D e adjudicação final |