# Matriz analítica — BMI/BCI, modelos de linguagem, riscos e governança

## 1. Objetivo

Este documento define a estrutura da matriz analítica utilizada para:

- revisar os estudos classificados como centrais;
- registrar decisões de inclusão e exclusão;
- preservar a classificação automática e a adjudicação humana;
- extrair evidências técnicas, metodológicas e sociotécnicas;
- apoiar análises descritivas;
- identificar padrões, lacunas e oportunidades de pesquisa;
- produzir sínteses reproduzíveis.

A matriz complementa:

- `docs/protocolo_neuro.md`;
- `docs/decisoes_conceituais.md`;
- `config/taxonomy_neuro.yaml`;
- `docs/releases/v4.3f.md`.

## 2. Corpus inicial

A matriz será aplicada inicialmente ao corpus adjudicado da versão v4.3f.

```text
Corpus total recuperado: 864 registros
Corpus central automatizado: 255 registros
Corpus central adjudicado: 254 registros
A1 — Integração BMI/BCI e modelos de linguagem: 71
A2 — Decodificação neural de linguagem: 120
A3 — Riscos e governança: 63
```

Os 254 registros constituem um conjunto candidato à triagem humana. Eles não representam automaticamente o conjunto final de estudos incluídos.

## 3. Unidade de análise

A unidade principal de análise é uma publicação científica ou técnica individual.

Exemplos:

- artigo de periódico;
- artigo de conferência;
- preprint;
- revisão;
- survey;
- tese ou dissertação;
- documento normativo;
- relatório técnico relevante.

Quando várias publicações apresentarem o mesmo estudo, deverá ser priorizada a versão mais completa, revisada ou final.

## 4. Princípios de preenchimento

A matriz deverá seguir os seguintes princípios:

1. preservar os dados originais recuperados;
2. separar valores automáticos de decisões humanas;
3. não inferir informações ausentes;
4. registrar evidências para decisões relevantes;
5. utilizar vocabulários controlados sempre que possível;
6. permitir múltiplos valores em campos compatíveis;
7. distinguir `não informado` de `não aplicável`;
8. manter rastreabilidade entre registro, fonte e decisão;
9. registrar alterações de classificação como adjudicações;
10. preservar a data e o responsável por cada revisão.

## 5. Etapas representadas na matriz

```text
Metadados recuperados
    ↓
Higienização e deduplicação
    ↓
Classificação automática
    ↓
Adjudicação da classificação
    ↓
Triagem de título e resumo
    ↓
Recuperação do texto completo
    ↓
Triagem de texto completo
    ↓
Extração de evidências
    ↓
Avaliação metodológica
    ↓
Síntese e análise
```

## 6. Estrutura dos campos

### 6.1 Identificação e rastreabilidade

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `record_id` | texto | sim | Identificador interno e estável do registro |
| `source_record_id` | texto | não | Identificador utilizado pela fonte de origem |
| `source` | categoria | sim | Fonte principal do registro |
| `sources` | lista | não | Todas as fontes em que o registro foi localizado |
| `query_layer` | categoria | não | Camada ou grupo de consulta que recuperou o registro |
| `query_text` | texto | não | Query responsável pela recuperação |
| `search_date` | data | não | Data da busca |
| `pipeline_version` | texto | sim | Versão do pipeline utilizada |
| `taxonomy_version` | texto | sim | Versão da taxonomia utilizada |
| `duplicate_group` | texto | não | Identificador do grupo de duplicatas |
| `canonical_record` | booleano | sim | Indica se o registro é a versão canônica |

### 6.2 Metadados bibliográficos

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `title` | texto | sim | Título da publicação |
| `normalized_title` | texto | sim | Título normalizado pelo pipeline |
| `authors` | texto | não | Lista de autores |
| `year` | inteiro | não | Ano de publicação |
| `venue` | texto | não | Periódico, conferência ou repositório |
| `publisher` | texto | não | Editora ou instituição |
| `publication_type` | categoria | não | Artigo, conferência, preprint, revisão etc. |
| `doi` | texto | não | DOI normalizado |
| `url` | texto | não | Endereço principal da publicação |
| `language` | categoria | não | Idioma principal |
| `abstract_available` | booleano | sim | Indica disponibilidade do resumo |
| `full_text_available` | booleano | não | Indica disponibilidade do texto completo |
| `open_access` | booleano | não | Indica acesso aberto |
| `citation_count` | inteiro | não | Número de citações no momento da coleta |

### 6.3 Classificação automatizada

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `suggested_priority` | categoria | sim | Prioridade atribuída automaticamente |
| `suggested_stream` | categoria | sim | Corrente temática sugerida |
| `suggested_tags` | lista | não | Tags atribuídas automaticamente |
| `classification_version` | texto | sim | Versão das regras de classificação |
| `classification_evidence` | texto | não | Síntese das evidências detectadas |
| `classification_confidence` | categoria | não | Alta, média ou baixa |
| `classification_warning` | texto | não | Ambiguidade ou limitação identificada |

Valores válidos para `suggested_priority`:

```text
A1-central-integracao-llm
A2-central-decoding-linguagem
A3-central-riscos-governanca
B-apoio
D-descartar
```

### 6.4 Adjudicação da classificação

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `adjudication_required` | booleano | sim | Indica necessidade de revisão da prioridade |
| `adjudicated_priority` | categoria | não | Prioridade definida após revisão humana |
| `final_priority` | categoria | sim | Prioridade final utilizada na análise |
| `adjudication_reason` | texto | não | Justificativa da alteração |
| `adjudication_source` | texto | não | Fonte utilizada na revisão |
| `adjudicated_by` | texto | não | Responsável pela decisão |
| `adjudication_date` | data | não | Data da adjudicação |

Regra:

```text
Sem adjudicação:
final_priority = suggested_priority

Com adjudicação:
final_priority = adjudicated_priority
```

### 6.5 Triagem por título e resumo

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `screening_decision` | categoria | sim | Decisão da triagem inicial |
| `screening_reason_code` | categoria | não | Código padronizado da justificativa |
| `screening_reason` | texto | não | Justificativa complementar |
| `screening_evidence` | texto | não | Evidência resumida que fundamenta a decisão |
| `screened_by` | texto | sim | Responsável pela triagem |
| `screening_date` | data | sim | Data da triagem |
| `second_review_required` | booleano | sim | Indica necessidade de segunda avaliação |
| `screening_conflict` | booleano | não | Indica divergência entre revisores |
| `screening_notes` | texto | não | Observações adicionais |

Valores válidos para `screening_decision`:

```text
Include
Exclude
Uncertain
```

### 6.6 Triagem por texto completo

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `full_text_decision` | categoria | não | Decisão após leitura integral |
| `full_text_reason_code` | categoria | não | Código da justificativa |
| `full_text_reason` | texto | não | Justificativa complementar |
| `full_text_reviewed_by` | texto | não | Responsável pela leitura |
| `full_text_review_date` | data | não | Data da leitura |
| `final_inclusion` | booleano | não | Indica inclusão no conjunto final |
| `exclusion_stage` | categoria | não | Título/resumo ou texto completo |
| `exclusion_reason` | texto | não | Motivo final da exclusão |

Valores válidos para `full_text_decision`:

```text
Include
Exclude
Uncertain
Not reviewed
```

## 7. Códigos de inclusão e exclusão

### 7.1 Inclusão

| Código | Descrição |
|---|---|
| `I01` | Integra operacionalmente BMI/BCI e modelo de linguagem |
| `I02` | Realiza decodificação neural de fala, texto ou linguagem |
| `I03` | Investiga riscos, privacidade, ética ou governança de BMI/BCI |
| `I04` | Apresenta evidência técnica relevante para arquitetura integrada |
| `I05` | Avalia aspectos humanos, confiança, autonomia ou supervisão |
| `I06` | Propõe mitigação, segurança ou governança aplicável ao tema |
| `I07` | Estudo fundacional necessário para compreender o domínio |
| `I08` | Revisão central para uma das correntes investigadas |

### 7.2 Exclusão

| Código | Descrição |
|---|---|
| `E01` | Fora do escopo temático |
| `E02` | Coincidência terminológica |
| `E03` | BMI significa Body Mass Index |
| `E04` | BCI possui significado diferente de Brain-Computer Interface |
| `E05` | Decodificação neural sem relação com linguagem ou comunicação |
| `E06` | Uso de IA ou LLM sem relação operacional com sinais neurais |
| `E07` | Estudo comparativo cérebro–modelo sem integração operacional |
| `E08` | Aplicação de autenticação ou identificação sem contribuição de risco ou governança |
| `E09` | Revisão ou tutorial excessivamente amplo |
| `E10` | Registro duplicado |
| `E11` | Versão substituída por publicação mais completa |
| `E12` | Metadados insuficientes |
| `E13` | Conteúdo editorial, errata, figura ou material suplementar |
| `E14` | Texto completo indisponível após tentativas de recuperação |
| `E15` | Tipo de publicação não elegível |
| `E16` | Não apresenta contribuição utilizável para as questões de pesquisa |

## 8. Caracterização técnica do estudo

### 8.1 Desenho e natureza da pesquisa

| Campo | Tipo | Descrição |
|---|---|---|
| `study_type` | categoria | Experimental, observacional, revisão, teórico etc. |
| `research_area` | lista | Neuroengenharia, NLP, HCI, ética, segurança etc. |
| `research_stream` | categoria | A1, A2, A3 ou corrente complementar |
| `research_questions` | texto | Questões investigadas pelo estudo |
| `study_objective` | texto | Objetivo principal |
| `study_context` | texto | Contexto clínico, assistivo, laboratorial ou social |

Valores sugeridos para `study_type`:

```text
Experimental
Observational
Technical validation
Prototype evaluation
User study
Clinical study
Systematic review
Scoping review
Narrative review
Survey
Tutorial
Conceptual
Normative
Policy analysis
Dataset paper
Benchmark
Other
```

### 8.2 Modalidade neural

| Campo | Tipo | Descrição |
|---|---|---|
| `neural_modality` | lista | Modalidade de aquisição neural |
| `invasiveness` | categoria | Grau de invasividade |
| `signal_source` | texto | Região, tecido ou origem fisiológica |
| `acquisition_device` | texto | Dispositivo utilizado |
| `channel_count` | inteiro | Quantidade de canais ou eletrodos |
| `sampling_rate` | número | Taxa de amostragem |
| `signal_preprocessing` | texto | Etapas de pré-processamento |
| `neural_features` | texto | Representações extraídas |

Valores sugeridos para `neural_modality`:

```text
EEG
ECoG
fMRI
fNIRS
MEG
Intracortical
sEEG
Depth electrodes
EMG
Hybrid
Simulated
Not informed
Other
```

Valores válidos para `invasiveness`:

```text
Invasive
Partially invasive
Non-invasive
Hybrid
Not applicable
Not informed
```

### 8.3 Participantes e dados

| Campo | Tipo | Descrição |
|---|---|---|
| `participant_count` | inteiro | Número de participantes |
| `participant_group` | categoria | Pessoas saudáveis, pacientes etc. |
| `clinical_condition` | texto | Condição clínica investigada |
| `age_range` | texto | Faixa etária |
| `sex_gender_information` | texto | Informação reportada pelo estudo |
| `dataset_name` | texto | Nome do conjunto de dados |
| `dataset_public` | booleano | Indica disponibilidade pública |
| `dataset_size` | texto | Dimensão do conjunto |
| `subjects_train` | inteiro | Participantes usados no treinamento |
| `subjects_test` | inteiro | Participantes usados no teste |
| `cross_subject` | booleano | Avaliação entre participantes |
| `cross_session` | booleano | Avaliação entre sessões |
| `cross_language` | booleano | Avaliação entre idiomas |

### 8.4 Tarefa, entrada e saída

| Campo | Tipo | Descrição |
|---|---|---|
| `task` | lista | Tarefa principal |
| `neural_input` | texto | Entrada neural utilizada |
| `stimulus_input` | texto | Estímulo apresentado ao participante |
| `system_output` | lista | Saída produzida pelo sistema |
| `output_granularity` | categoria | Fonema, palavra, sentença, texto etc. |
| `communication_mode` | categoria | Fala, escrita, speller, comando etc. |
| `real_time` | booleano | Indica operação em tempo real |
| `closed_loop` | booleano | Indica interação em ciclo fechado |
| `online_evaluation` | booleano | Indica avaliação online |

Valores sugeridos para `task`:

```text
Speech decoding
Semantic decoding
Brain-to-text
EEG-to-text
Speech synthesis
Imagined speech
Attempted speech
Silent speech
Spelling
Word prediction
Sentence generation
Communication assistance
Visual description decoding
Clinical interpretation
Classification
Control
Other
```

Valores sugeridos para `system_output`:

```text
Speech
Text
Word
Sentence
Phoneme
Semantic representation
Keyword
Spelling selection
Command
Image
Clinical report
Classification label
Other
```

## 9. Modelos e arquitetura computacional

| Campo | Tipo | Descrição |
|---|---|---|
| `model_family` | lista | Família do modelo utilizado |
| `language_model` | texto | Nome do modelo de linguagem |
| `language_model_type` | categoria | Estatístico, transformer, LLM etc. |
| `pretrained_model` | booleano | Indica uso de modelo pré-treinado |
| `foundation_model` | booleano | Indica uso de foundation model |
| `model_role` | lista | Papel do modelo no sistema |
| `integration_architecture` | texto | Arquitetura de integração |
| `neural_encoder` | texto | Modelo usado para sinais neurais |
| `language_decoder` | texto | Modelo usado para gerar linguagem |
| `fusion_method` | texto | Método de fusão entre modalidades |
| `prompting_strategy` | texto | Estratégia de prompting |
| `retrieval_component` | texto | Componente de recuperação |
| `fine_tuning` | categoria | Tipo de ajuste realizado |
| `parameter_count` | texto | Número de parâmetros |
| `training_strategy` | texto | Estratégia de treinamento |
| `baseline_models` | texto | Modelos usados como comparação |

Valores sugeridos para `language_model_type`:

```text
Statistical n-gram
Neural language model
Transformer
Pretrained language model
Large language model
Encoder-decoder
Retrieval-augmented model
No language model
Not informed
Other
```

Valores sugeridos para `model_role`:

```text
Decoder
Generator
Text completion
Word prediction
Error correction
Semantic retrieval
Feature extraction
Representation alignment
Prompt conditioning
Reranking
Classification
Clinical interpretation
Interface
Baseline
Other
```

## 10. Integração BMI/BCI–modelo de linguagem

| Campo | Tipo | Descrição |
|---|---|---|
| `operational_integration` | booleano | Indica integração operacional |
| `integration_stage` | lista | Estágio em que o modelo participa |
| `neural_to_language_flow` | texto | Descrição resumida do fluxo |
| `shared_representation` | texto | Representação intermediária |
| `model_receives_neural_data` | booleano | Indica contato direto com dados neurais |
| `model_receives_derived_cues` | booleano | Indica uso de pistas derivadas |
| `raw_neural_data_local` | booleano | Indica permanência local dos dados |
| `human_validation_stage` | texto | Ponto de validação humana |
| `integration_limitations` | texto | Limitações da integração |

Valores sugeridos para `integration_stage`:

```text
Preprocessing
Feature extraction
Semantic mapping
Decoding
Retrieval
Prompt construction
Text generation
Error correction
Reranking
User interface
Post-processing
Other
```

## 11. Avaliação e resultados

| Campo | Tipo | Descrição |
|---|---|---|
| `evaluation_design` | texto | Desenho da avaliação |
| `validation_strategy` | texto | Holdout, cross-validation etc. |
| `metrics` | lista | Métricas utilizadas |
| `primary_metric` | texto | Métrica principal |
| `primary_result` | texto | Resultado principal |
| `baseline_result` | texto | Resultado do baseline |
| `statistical_test` | texto | Teste estatístico aplicado |
| `statistical_significance` | texto | Significância reportada |
| `generalization_result` | texto | Resultado de generalização |
| `latency` | texto | Latência reportada |
| `computational_cost` | texto | Custo computacional |
| `main_findings` | texto | Síntese dos achados |
| `authors_limitations` | texto | Limitações reconhecidas pelos autores |
| `reviewer_limitations` | texto | Limitações identificadas na revisão |

Métricas frequentes:

```text
Accuracy
Precision
Recall
F1-score
AUC
WER
CER
BLEU
ROUGE
METEOR
BERTScore
Semantic similarity
Information transfer rate
Latency
User satisfaction
Task completion
Calibration
Trust
Error rate
Other
```

## 12. Dimensão humana e interação

| Campo | Tipo | Descrição |
|---|---|---|
| `human_in_the_loop` | booleano | Indica participação humana no ciclo |
| `human_role` | lista | Papel do participante ou operador |
| `user_control` | texto | Mecanismos de controle do usuário |
| `human_validation` | texto | Processo de revisão humana |
| `feedback_mechanism` | texto | Forma de feedback |
| `uncertainty_communication` | texto | Comunicação da incerteza |
| `explainability` | texto | Recursos explicativos |
| `trust_evaluated` | booleano | Indica avaliação de confiança |
| `trust_measure` | texto | Instrumento ou métrica |
| `reliance_evaluated` | booleano | Indica avaliação de reliance |
| `overreliance_risk` | texto | Evidência ou discussão de dependência excessiva |
| `user_experience` | texto | Aspectos de experiência do usuário |
| `accessibility` | texto | Recursos de acessibilidade |
| `agency_autonomy` | texto | Efeitos sobre agência e autonomia |

Valores sugeridos para `human_role`:

```text
Signal producer
System operator
Message author
Message recipient
Clinician
Caregiver
Researcher
Data annotator
Decision maker
Reviewer
No human evaluation
Other
```

## 13. Vieses, erros e vulnerabilidades

| Campo | Tipo | Descrição |
|---|---|---|
| `bias_discussed` | booleano | Indica discussão de viés ou distorção |
| `bias_type` | lista | Tipo de viés ou efeito |
| `bias_stage` | lista | Estágio em que pode ocorrer |
| `error_source` | lista | Fonte do erro |
| `uncertainty_source` | lista | Fonte da incerteza |
| `hallucination_risk` | texto | Risco de geração não sustentada |
| `misinterpretation_risk` | texto | Risco de interpretação inadequada |
| `amplification_risk` | texto | Risco de amplificação de distorções |
| `evaluation_of_bias` | texto | Forma de avaliação |
| `mitigation_of_bias` | texto | Estratégia de mitigação |
| `residual_risk` | texto | Risco remanescente |

Valores sugeridos para `bias_type`:

```text
Dataset imbalance
Selection bias
Representation bias
Measurement bias
Calibration bias
Language bias
Demographic bias
Cross-subject bias
Cross-language bias
Confirmation-like effect
Anchoring-like effect
Automation bias
Overreliance
Interpretation bias
Not evaluated
Other
```

Valores sugeridos para `bias_stage`:

```text
Data collection
Signal acquisition
Preprocessing
Feature extraction
Neural decoding
Semantic mapping
Language generation
Interface presentation
Human interpretation
Decision making
Deployment
Other
```

## 14. Privacidade, segurança, ética e governança

| Campo | Tipo | Descrição |
|---|---|---|
| `risk_governance_central` | booleano | Indica centralidade do tema |
| `privacy_risk` | lista | Riscos de privacidade |
| `security_risk` | lista | Riscos de segurança |
| `ethical_risk` | lista | Riscos éticos |
| `neural_data_sensitivity` | texto | Caracterização da sensibilidade |
| `mental_privacy` | texto | Discussão sobre privacidade mental |
| `informed_consent` | texto | Tratamento do consentimento |
| `data_governance` | texto | Governança de dados |
| `data_locality` | texto | Local de processamento dos dados |
| `data_sharing` | texto | Política ou prática de compartilhamento |
| `attack_model` | texto | Modelo de ameaça |
| `misuse_scenario` | texto | Possível uso indevido |
| `autonomy_risk` | texto | Risco para autonomia |
| `neurorights` | texto | Discussão sobre direitos neurais |
| `accountability` | texto | Responsabilidade por decisões |
| `regulatory_framework` | texto | Norma, lei ou framework citado |
| `governance_mechanism` | lista | Mecanismo proposto |
| `risk_mitigation` | texto | Estratégias de mitigação |

Valores sugeridos para `privacy_risk`:

```text
Mental privacy
Neural data exposure
Identity inference
Sensitive attribute inference
Unauthorized decoding
Re-identification
Secondary use
Data leakage
Model inversion
Not evaluated
Other
```

Valores sugeridos para `governance_mechanism`:

```text
Consent
Access control
Encryption
On-device processing
Data minimization
Audit logging
Human oversight
Transparency
Explainability
Uncertainty disclosure
Independent review
Regulatory compliance
Neurorights protection
Risk assessment
Other
```

## 15. Qualidade metodológica

| Campo | Tipo | Descrição |
|---|---|---|
| `quality_assessed` | booleano | Indica realização da avaliação |
| `objective_clear` | categoria | Clareza dos objetivos |
| `method_adequate` | categoria | Adequação do método |
| `sample_adequate` | categoria | Adequação da amostra |
| `dataset_described` | categoria | Qualidade da descrição dos dados |
| `baseline_adequate` | categoria | Adequação dos baselines |
| `evaluation_reproducible` | categoria | Reprodutibilidade da avaliação |
| `limitations_reported` | categoria | Qualidade do relato de limitações |
| `code_available` | booleano | Código disponível |
| `data_available` | booleano | Dados disponíveis |
| `conflict_of_interest` | texto | Conflitos declarados |
| `funding_source` | texto | Fonte de financiamento |
| `quality_score` | número | Pontuação opcional |
| `quality_notes` | texto | Observações metodológicas |

Valores sugeridos para avaliações qualitativas:

```text
Yes
Partially
No
Unclear
Not applicable
```

A qualidade metodológica não deve ser utilizada isoladamente para excluir um estudo sem que o protocolo defina previamente essa regra.

## 16. Relação com as questões de pesquisa

| Campo | Tipo | Descrição |
|---|---|---|
| `addresses_sq01` | booleano | Arquiteturas e integração |
| `addresses_sq02` | booleano | Modalidades neurais |
| `addresses_sq03` | booleano | Papel dos modelos de linguagem |
| `addresses_sq04` | booleano | Erros, vieses e vulnerabilidades |
| `addresses_sq05` | booleano | Confiança e supervisão |
| `addresses_sq06` | booleano | Segurança, privacidade e autonomia |
| `addresses_sq07` | booleano | Mitigação e governança |
| `addresses_sq08` | booleano | Lacunas da literatura |
| `relevance_to_project` | categoria | Relevância geral |
| `contribution_to_project` | texto | Contribuição específica |
| `evidence_summary` | texto | Síntese da evidência extraída |
| `research_gap` | texto | Lacuna identificada |
| `future_work` | texto | Trabalho futuro proposto |

Valores válidos para `relevance_to_project`:

```text
Core
High
Moderate
Supporting
Low
```

## 17. Síntese e uso acadêmico

| Campo | Tipo | Descrição |
|---|---|---|
| `use_in_literature_review` | booleano | Utilização na fundamentação |
| `use_in_methodology` | booleano | Utilização metodológica |
| `use_in_discussion` | booleano | Utilização na discussão |
| `use_as_case` | booleano | Utilização como caso ou exemplo |
| `use_as_background` | booleano | Utilização como apoio |
| `citation_priority` | categoria | Prioridade de citação |
| `key_message` | texto | Mensagem principal |
| `reviewer_interpretation` | texto | Interpretação do pesquisador |
| `reviewer_notes` | texto | Notas adicionais |
| `zotero_collection` | texto | Coleção no Zotero |
| `zotero_tags` | lista | Tags atribuídas no Zotero |

Valores sugeridos para `citation_priority`:

```text
Essential
High
Medium
Low
Do not cite
```

## 18. Convenções de preenchimento

### 18.1 Valores ausentes

Utilizar:

```text
Not informed
```

quando o estudo não apresenta a informação.

Utilizar:

```text
Not applicable
```

quando o campo não se aplica ao estudo.

Não utilizar valores vazios quando a ausência já tiver sido confirmada durante a leitura integral.

### 18.2 Campos multivalorados

Campos que aceitam vários valores devem utilizar:

```text
valor 1; valor 2; valor 3
```

O caractere `;` será o separador padrão.

### 18.3 Datas

Datas devem utilizar o padrão ISO:

```text
YYYY-MM-DD
```

### 18.4 Booleanos

Valores booleanos devem ser armazenados como:

```text
true
false
```

### 18.5 Evidências

Os campos de evidência devem:

- resumir a informação;
- evitar copiar passagens longas;
- indicar página, seção, figura ou tabela quando possível;
- distinguir informação dos autores de interpretação do revisor;
- não apresentar inferências como fatos reportados.

### 18.6 Normalização

Sempre que necessário, devem coexistir:

```text
campo_original
campo_normalizado
```

Exemplo:

```text
venue_original
venue_normalized
```

O valor original não deverá ser sobrescrito.

## 19. Conjunto mínimo para triagem inicial

A primeira rodada de triagem dos 254 registros exige apenas os seguintes campos:

```text
record_id
title
authors
year
venue
doi
url
abstract_available
suggested_priority
suggested_stream
suggested_tags
final_priority
screening_decision
screening_reason_code
screening_reason
screening_evidence
screened_by
screening_date
second_review_required
screening_notes
```

Essa etapa não exige preencher todos os campos técnicos.

## 20. Conjunto mínimo para leitura integral

Os estudos incluídos ou incertos deverão receber:

```text
full_text_available
full_text_decision
full_text_reason_code
full_text_reason
full_text_reviewed_by
full_text_review_date
final_inclusion
study_type
research_stream
neural_modality
invasiveness
participant_count
dataset_name
task
neural_input
system_output
language_model
model_role
operational_integration
metrics
main_findings
authors_limitations
human_in_the_loop
bias_discussed
privacy_risk
security_risk
ethical_risk
governance_mechanism
relevance_to_project
evidence_summary
research_gap
```

## 21. Ordem recomendada de triagem

A triagem deverá ocorrer nesta ordem:

```text
1. A1 — 71 registros
2. A3 — 63 registros
3. A2 — 120 registros
```

Justificativa:

- A1 representa a interseção mais direta entre interfaces neurais e modelos de linguagem;
- A3 concentra riscos, ética e governança;
- A2 possui maior volume e deverá ser triada após a consolidação dos critérios dos dois primeiros grupos.

## 22. Controle de qualidade

A matriz deverá ser verificada periodicamente quanto a:

- identificadores duplicados;
- decisões sem justificativa;
- prioridades inválidas;
- datas fora do padrão;
- campos obrigatórios vazios;
- uso inconsistente de vocabulário;
- estudos incluídos sem texto completo;
- alterações manuais sem adjudicação;
- divergências entre `final_priority` e decisão documentada;
- múltiplos valores com separadores diferentes;
- registros sem responsável pela revisão.

## 23. Versionamento

Cada versão consolidada da matriz deverá registrar:

```text
matrix_version
pipeline_version
taxonomy_version
protocol_version
corpus_version
created_at
updated_at
reviewer
record_count
included_count
excluded_count
uncertain_count
```

Nomes sugeridos:

```text
matriz_triagem_neuro_v4_3f.csv
matriz_texto_completo_neuro_v4_3f.csv
matriz_evidencias_neuro_v4_4.csv
```

## 24. Artefatos esperados

A aplicação desta matriz deverá produzir:

1. corpus triado por título e resumo;
2. lista de estudos excluídos e respectivas justificativas;
3. lista de registros incertos;
4. corpus selecionado para leitura integral;
5. matriz de extração de evidências;
6. catálogo de arquiteturas BMI/BCI–modelo de linguagem;
7. mapa de modalidades neurais;
8. catálogo de riscos e mecanismos de governança;
9. síntese das métricas e resultados;
10. mapa de lacunas de pesquisa.

## 25. Evolução prevista

```text
v4.3f
    Classificação e adjudicação do corpus

Triagem manual
    Título e resumo dos 254 estudos centrais

Leitura integral
    Decisão final de inclusão

v4.4
    Extração estruturada de evidências

v4.5
    Análises descritivas e mapas de lacunas

v5.0
    Síntese acadêmica consolidada
```