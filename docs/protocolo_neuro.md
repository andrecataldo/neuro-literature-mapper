# Protocolo leve para o trabalho de FSI

## Tipo de estudo

Levantamento exploratório estruturado da literatura de Sistemas de Informação, orientado por protocolo.

## Estratégia de busca

A busca foi organizada a partir de uma lógica de funil, com três blocos conceituais principais:

1. **Fonte de Sistemas de Informação**: periódicos, conferências e repositórios indicados na disciplina, incluindo AIS eLibrary, SBSI, iSys/SOL-SBC e periódicos internacionais de SI.

2. **Tecnologia investigada**: termos relacionados a IA generativa e modelos de linguagem, como `generative AI`, `large language models`, `ChatGPT` e `LLM`.

3. **Fenômeno investigado**: termos relacionados a julgamento, confiança, decisão e vieses, como `cognitive bias`, `trust`, `decision making`, `reliance`, `overreliance`, `algorithm aversion` e `algorithm appreciation`.

A string conceitual de referência foi:

`fonte de SI` AND (`generative AI` OR `large language models` OR `ChatGPT` OR `LLM`) AND (`cognitive bias` OR `trust` OR `decision making` OR `reliance` OR `overreliance` OR `algorithm aversion` OR `algorithm appreciation`)

Na execução prática, essa string ampla foi decomposta em buscas menores no Google Acadêmico, pois buscas booleanas longas com muitos operadores `OR` podem gerar resultados pouco controláveis. Cada busca foi registrada individualmente em CSV, com a query utilizada, a fonte pesquisada, o número aproximado de resultados, os artigos candidatos identificados e observações sobre relevância ou limitações.

Essa estratégia não teve como objetivo realizar uma revisão sistemática completa, mas sim um levantamento exploratório estruturado para posicionar o tema na literatura especializada de Sistemas de Informação.


## Tema

Vieses cognitivos e distorções de julgamento em Sistemas de Informação baseados em LLMs/IA generativa.

## Questão principal

Como a literatura de Sistemas de Informação tem tratado vieses cognitivos e distorções de julgamento em interações mediadas por LLMs e sistemas de IA generativa?

## Subquestões

| Código | Subquestão                                                                                                                                                                   |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SQ01   | Como a literatura de Sistemas de Informação tem abordado IA generativa, LLMs e ChatGPT como artefatos de SI?                                                                 |
| SQ02   | Quais correntes aparecem nos estudos encontrados: IA generativa em SI, interação humano-IA, confiança, decisão, qualidade informacional, governança ou vieses?               |
| SQ03   | Como os estudos relacionam LLMs/IA generativa com julgamento humano, tomada de decisão, confiança, reliance, overreliance, aversão algorítmica ou apreciação algorítmica?    |
| SQ04   | Quando o termo “viés” aparece na literatura de SI, ele é tratado como viés cognitivo, viés algorítmico, fairness, discriminação, erro decisório ou distorção de julgamento?  |
| SQ05   | Que lacuna preliminar pode ser identificada para justificar uma abordagem nova ou o aprimoramento de uma existente no estudo de vieses cognitivos em interações usuário–LLM? |


## Correntes analíticas

1. IA generativa/LLMs como Sistemas de Informação.
2. Interação humano-IA, confiança e dependência.
3. Vieses cognitivos e distorções de julgamento.
4. Qualidade informacional, decisão e governança.
5. Literatura brasileira de SI.

## Critérios de inclusão

| Código | Critério |
|---|---|
| CI1 | O estudo trata de LLMs, IA generativa ou sistemas inteligentes em contexto de SI. |
| CI2 | O estudo discute julgamento, decisão, confiança, interpretação ou uso da informação. |
| CI3 | O estudo aborda vieses cognitivos, distorções de julgamento, dependência, aversão ou apreciação algorítmica. |
| CI4 | O estudo foi publicado em periódico ou evento relevante de SI, ou em área vizinha útil como HCI/IR. |

## Critérios de exclusão

| Código | Critério |
|---|---|
| CE1 | Estudo puramente técnico sobre arquitetura ou benchmark de modelo, sem discussão de uso/interação. |
| CE2 | Estudo sobre viés algorítmico/demográfico sem relação com cognição, julgamento ou decisão do usuário. |
| CE3 | Estudo sem texto completo disponível. |
| CE4 | Duplicata ou versão preliminar substituída por versão publicada. |
| CE5 | Preprint sem revisão por pares, salvo como apoio exploratório. |
| CE6 | Estudo fora de SI, IHC, decisão, educação ou contexto sociotécnico. |

## Campos de extração

| Campo | Descrição |
|---|---|
| Referência | Autor, ano, título |
| Venue/Fonte | MISQ, ICIS, SBSI, iSys, ACM, SSRN etc. |
| Fonte indicada pelo professor? | Sim/Não |
| Categoria | A-central, B-apoio, C-cautela, D-descartar |
| Corrente | Uma das correntes analíticas |
| Tipo de estudo | Teórico, empírico, revisão, experimento, survey, estudo de caso |
| Contexto | Educação, organização, decisão, software, busca de informação etc. |
| Tecnologia | LLM, ChatGPT, GenAI, DSS, agente conversacional |
| Viés/distorção | Confirmação, ancoragem, disponibilidade, automação, overreliance etc. |
| Problema | Confiança excessiva, decisão enviesada, erro informacional etc. |
| Mitigação | Debiasing, revisão humana, explicabilidade, governança, treinamento |
| Relação com FSI | Como ajuda a posicionar o tema em SI |
| Relação com mestrado | Como pode ser útil depois |
| Decisão | Citar, ler melhor, apoio, descartar |
