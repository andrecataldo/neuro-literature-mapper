# Fluxo de triagem — Neuro Literature Mapper

## 1. Objetivo

Este documento descreve o fluxo operacional de triagem por título e resumo dos estudos classificados como centrais pelo projeto `neuro-literature-mapper`.

O processo tem como objetivos:

- transformar o corpus adjudicado em uma matriz de triagem;
- preservar a classificação automatizada e as adjudicações humanas;
- registrar decisões de inclusão, exclusão ou incerteza;
- identificar registros que exigem recuperação adicional de metadados;
- controlar possíveis duplicatas;
- preparar o conjunto de estudos para leitura integral;
- manter rastreabilidade entre corpus, classificação e decisão humana.

A triagem é uma etapa intermediária entre a classificação automática e a extração estruturada de evidências.

```text
Busca e consolidação
    ↓
Classificação automática
    ↓
Adjudicação da prioridade
    ↓
Triagem por título e resumo
    ↓
Recuperação de texto completo
    ↓
Triagem por texto completo
    ↓
Extração de evidências
```

## 2. Documentos relacionados

Este fluxo deve ser interpretado em conjunto com:

- `docs/protocolo_neuro.md`;
- `docs/decisoes_conceituais.md`;
- `docs/matriz_analitica_neuro.md`;
- `docs/releases/v4.3f.md`;
- `config/taxonomy_neuro.yaml`.

## 3. Baseline utilizado

A primeira matriz de triagem é derivada do corpus adjudicado da versão v4.3f.

| Indicador | Quantidade |
|---|---:|
| Corpus total | 864 |
| Corpus central automatizado | 255 |
| Corpus central adjudicado | 254 |
| A1 — Integração BMI/BCI e modelos de linguagem | 71 |
| A2 — Decodificação neural de linguagem | 120 |
| A3 — Riscos e governança | 63 |
| B — Literatura de apoio | 564 |
| D — Descartar | 46 |

A matriz de triagem contém apenas os 254 registros classificados como A1, A2 ou A3 após adjudicação.

Esses registros constituem candidatos à triagem. Eles não representam automaticamente os estudos finais incluídos na pesquisa.

## 4. Arquivos do fluxo

### 4.1 Entradas

Corpus adjudicado:

```text
outputs/resultados_neuro_v4_3f_union_p5_p10_adjudicado.csv
```

Corpus automatizado anterior à adjudicação:

```text
outputs/resultados_neuro_v4_3f_union_p5_p10.csv
```

O corpus automatizado é utilizado para preservar a categoria originalmente atribuída pelo classificador.

### 4.2 Script

```text
scripts/init_screening_matrix.py
```

### 4.3 Saída

```text
outputs/matriz_triagem_neuro_v4_3f.csv
```

O arquivo de saída contém resumos e decisões humanas. Ele deve permanecer fora do Git.

### 4.4 Testes

```text
tests/test_screening_matrix.py
```

## 5. Inicialização da matriz

A matriz é criada com:

```bash
python scripts/init_screening_matrix.py
```

A execução deve produzir:

```text
Central records:            254
A1 records:                 71
A3 records:                 63
A2 records:                 120
```

A quantidade de registros sem resumo pode variar conforme a versão dos metadados. No baseline inicial da v4.3f foram identificados:

```text
40 registros sem resumo
```

## 6. Proteção contra sobrescrita

Por padrão, o script não sobrescreve uma matriz existente.

Quando o arquivo já existir, a execução será interrompida.

```text
ERROR: output already exists
```

O parâmetro `--force` somente deve ser utilizado antes do início da triagem manual ou após a criação de uma cópia de segurança.

```bash
python scripts/init_screening_matrix.py --force
```

Depois que decisões humanas forem registradas, a matriz não deve ser recriada diretamente.

## 7. Cópia de segurança

Antes de qualquer operação que possa substituir ou modificar o arquivo em massa, deve ser criada uma cópia.

Exemplo:

```bash
cp \
  outputs/matriz_triagem_neuro_v4_3f.csv \
  "outputs/matriz_triagem_neuro_v4_3f_backup_$(date +%Y%m%d_%H%M%S).csv"
```

Conferência:

```bash
ls -lh outputs/matriz_triagem_neuro_v4_3f*
```

## 8. Estrutura da matriz

A matriz inicial contém 22 campos.

| Campo | Origem | Descrição |
|---|---|---|
| `record_id` | gerado ou recuperado | Identificador único utilizado na triagem |
| `source_record_id` | corpus | Identificador original, quando disponível |
| `duplicate_group` | gerado | Identificador compartilhado por candidatos a duplicata |
| `title` | corpus | Título da publicação |
| `authors` | corpus | Autores |
| `year` | corpus | Ano de publicação |
| `venue` | corpus | Periódico, conferência ou repositório |
| `doi` | corpus | DOI normalizado |
| `url` | corpus | Endereço da publicação |
| `abstract` | corpus | Resumo utilizado na triagem |
| `abstract_available` | gerado | Indica presença de resumo |
| `suggested_priority` | classificação automática | Categoria atribuída antes da adjudicação |
| `adjudicated_priority` | comparação | Categoria alterada por revisão humana |
| `final_priority` | corpus adjudicado | Categoria utilizada na triagem |
| `screening_decision` | pesquisador | Include, Exclude ou Uncertain |
| `screening_reason_code` | pesquisador | Código da justificativa |
| `screening_reason` | pesquisador | Justificativa complementar |
| `screening_evidence` | pesquisador | Evidência que sustenta a decisão |
| `screened_by` | pesquisador | Responsável pela triagem |
| `screening_date` | pesquisador | Data da decisão |
| `second_review_required` | gerado ou pesquisador | Indica necessidade de segunda revisão |
| `screening_notes` | gerado ou pesquisador | Observações adicionais |

## 9. Classificação preservada

A matriz separa três conceitos.

### 9.1 Prioridade sugerida

```text
suggested_priority
```

Representa a classificação produzida automaticamente.

### 9.2 Prioridade adjudicada

```text
adjudicated_priority
```

É preenchida quando a classificação final difere da sugestão automática.

### 9.3 Prioridade final

```text
final_priority
```

Representa a categoria utilizada para ordenar e iniciar a triagem.

Regra:

```text
Sem adjudicação:
final_priority = suggested_priority

Com adjudicação:
final_priority = adjudicated_priority
```

A decisão de triagem não deve sobrescrever esses campos.

## 10. Categorias temáticas

### A1 — Integração BMI/BCI e modelos de linguagem

Estudos em que modelos de linguagem ou componentes linguísticos participam operacionalmente do sistema neural.

Exemplos:

- EEG-to-text com LLM;
- modelo de linguagem utilizado como decoder;
- predição de palavras em BCI;
- geração textual condicionada por sinais neurais;
- correção linguística em spellers;
- recuperação semântica seguida de geração.

### A2 — Decodificação neural de linguagem

Estudos que transformam sinais neurais em saídas linguísticas ou comunicacionais sem uma integração operacional dominante de modelo de linguagem.

Exemplos:

- brain-to-text;
- speech decoding;
- imagined speech;
- attempted speech;
- silent speech;
- soletração neural;
- reconstrução de palavras ou sentenças;
- neuropróteses de fala.

### A3 — Riscos e governança

Estudos cuja contribuição central aborda:

- privacidade neural;
- privacidade mental;
- neuroética;
- segurança de dados neurais;
- autonomia;
- consentimento;
- responsabilidade;
- direitos neurais;
- governança;
- modelos de ameaça;
- uso indevido da neurotecnologia.

## 11. Ordem da triagem

A matriz é organizada nesta ordem:

```text
1. A1
2. A3
3. A2
```

Dentro de cada categoria:

```text
1. registros sem resumo;
2. ano mais recente para o mais antigo;
3. título em ordem alfabética.
```

A ordenação tem como finalidade:

- começar pela interseção central BMI/BCI–modelo de linguagem;
- identificar cedo os casos sem resumo;
- revisar em seguida riscos e governança;
- triagem posterior do conjunto mais amplo de decodificação neural.

A ordem não representa grau de qualidade metodológica.

## 12. Decisões de triagem

O campo `screening_decision` aceita:

```text
Include
Exclude
Uncertain
```

### 12.1 Include

Utilizar quando o título e o resumo apresentam evidência suficiente de aderência ao escopo.

A decisão significa:

```text
Encaminhar para recuperação e leitura do texto completo
```

Não significa inclusão definitiva na síntese final.

### 12.2 Exclude

Utilizar quando o registro apresenta evidência suficiente de exclusão.

A decisão deve incluir:

- código;
- justificativa;
- evidência;
- responsável;
- data.

### 12.3 Uncertain

Utilizar quando título e resumo não permitem uma decisão segura.

Exemplos:

- resumo ausente;
- resumo excessivamente curto;
- ambiguidade sobre o papel do modelo de linguagem;
- dúvida sobre existência de saída linguística;
- risco ou governança apenas mencionados superficialmente;
- possível duplicata;
- diferença entre preprint e publicação final;
- metadados conflitantes.

Registros `Uncertain` devem ser encaminhados para segunda revisão ou recuperação do texto completo.

## 13. Códigos de inclusão

| Código | Descrição |
|---|---|
| `I01` | Integra operacionalmente BMI/BCI e modelo de linguagem |
| `I02` | Realiza decodificação neural de fala, texto ou linguagem |
| `I03` | Investiga riscos, privacidade, ética ou governança de BMI/BCI |
| `I04` | Apresenta evidência técnica relevante para arquitetura integrada |
| `I05` | Avalia aspectos humanos, confiança, autonomia ou supervisão |
| `I06` | Propõe mecanismo de mitigação, segurança ou governança |
| `I07` | Estudo fundacional necessário para compreender o domínio |
| `I08` | Revisão central para uma das correntes investigadas |

## 14. Códigos de exclusão

| Código | Descrição |
|---|---|
| `E01` | Fora do escopo temático |
| `E02` | Coincidência terminológica |
| `E03` | BMI significa Body Mass Index |
| `E04` | BCI possui outro significado |
| `E05` | Decodificação neural sem relação com linguagem ou comunicação |
| `E06` | Uso de IA ou LLM sem relação operacional com sinais neurais |
| `E07` | Comparação cérebro–modelo sem integração operacional |
| `E08` | Autenticação ou identificação sem contribuição de risco ou governança |
| `E09` | Revisão ou tutorial excessivamente amplo |
| `E10` | Registro duplicado |
| `E11` | Versão substituída por publicação mais completa |
| `E12` | Metadados insuficientes |
| `E13` | Conteúdo editorial, errata, figura ou material suplementar |
| `E14` | Texto completo indisponível após tentativas de recuperação |
| `E15` | Tipo de publicação não elegível |
| `E16` | Não apresenta contribuição utilizável para as questões de pesquisa |

O código `E14` normalmente pertence à etapa de texto completo, e não à primeira triagem.

## 15. Preenchimento da evidência

O campo `screening_evidence` deve registrar de forma resumida a informação que sustenta a decisão.

Exemplo de inclusão:

```text
O resumo descreve um pipeline EEG → extração semântica → LLM
para produção de texto.
```

Exemplo de exclusão:

```text
O transformer é utilizado somente para classificar sinais EEG;
não há fala, texto ou saída comunicacional.
```

Exemplo de incerteza:

```text
O título indica brain-to-text, mas o resumo não está disponível
e não foi possível confirmar a contribuição técnica.
```

A evidência deve:

- ser concisa;
- indicar o elemento decisivo;
- distinguir descrição dos autores de interpretação do pesquisador;
- evitar copiar grandes trechos do resumo;
- não inventar informações ausentes.

## 16. Preenchimento da data e responsável

O campo `screened_by` deve utilizar um identificador consistente.

Exemplo:

```text
Andre Cataldo
```

O campo `screening_date` deve utilizar o padrão ISO:

```text
YYYY-MM-DD
```

Exemplo:

```text
2026-07-25
```

## 17. Segunda revisão

O campo `second_review_required` deve ser marcado como `true` quando:

- o resumo estiver ausente;
- a decisão for `Uncertain`;
- houver possível duplicata;
- houver conflito entre título e resumo;
- houver dúvida entre A1 e A2;
- risco ou governança aparecerem de forma ambígua;
- houver conflito entre versões da publicação;
- a decisão depender de conhecimento não disponível no registro;
- o pesquisador considerar necessária uma nova avaliação.

Valores válidos:

```text
true
false
```

A matriz inicial marca automaticamente como `true` os registros sem resumo e os candidatos a duplicata.

## 18. Tratamento de possíveis duplicatas

O script não remove automaticamente registros que compartilham o mesmo identificador.

Esses registros recebem:

- `record_id` exclusivo;
- valor comum em `duplicate_group`;
- `second_review_required = true`;
- aviso em `screening_notes`.

Baseline inicial:

```text
2 grupos candidatos a duplicata
4 registros envolvidos
```

### 18.1 ChatBCI-Assist

```text
NLM-775CA1200FD1-01
NLM-775CA1200FD1-02
```

Os títulos indicam uma publicação principal e uma possível versão editorial de edição especial.

### 18.2 Miniaturized Brain-Machine Interface

```text
NLM-C1132BC60F49-01
NLM-C1132BC60F49-02
```

Os títulos diferem principalmente pela presença de marcação HTML em `mm²`.

### 18.3 Procedimento de decisão

Para cada grupo:

1. comparar título;
2. comparar autores;
3. comparar DOI;
4. comparar venue;
5. comparar ano;
6. comparar resumo;
7. localizar a versão publicada;
8. identificar se existe publicação principal, versão editorial ou duplicata de metadados;
9. preservar a versão canônica;
10. marcar a outra como `Exclude`;
11. utilizar o código `E10` ou `E11`;
12. registrar a justificativa em `screening_reason`.

Exemplo:

```text
screening_decision: Exclude
screening_reason_code: E10
screening_reason: Registro duplicado da publicação canônica NLM-...
```

A exclusão não deve ser feita somente pela semelhança do título.

## 19. Registros sem resumo

O baseline contém 40 registros com:

```text
abstract_available = false
```

Esses registros aparecem antes dos demais dentro de cada classe.

Procedimento recomendado:

1. verificar DOI;
2. acessar a página da publicação;
3. procurar resumo no venue;
4. buscar a versão no repositório institucional;
5. verificar preprint correspondente;
6. procurar versão indexada em outra fonte;
7. atualizar localmente o resumo quando encontrado;
8. registrar a origem do resumo;
9. realizar a triagem;
10. manter `Uncertain` quando não houver evidência suficiente.

A inclusão ou exclusão não deve ser decidida somente pelo título quando houver ambiguidade relevante.

## 20. Atualização manual de resumos

Quando um resumo ausente for recuperado, deve-se preservar sua origem.

A versão atual da matriz não possui um campo específico para a fonte do resumo. Enquanto esse campo não for adicionado, utilizar:

```text
screening_notes
```

Exemplo:

```text
Abstract recovered from publisher page on 2026-07-25.
```

Após inserir o resumo:

```text
abstract_available = true
```

A alteração deve ser realizada somente no arquivo de triagem, não no corpus original da v4.3f.

A correção permanente de metadados deverá ocorrer em um fluxo separado.

## 21. Recomendações para edição

A matriz pode ser editada em:

- LibreOffice Calc;
- Microsoft Excel;
- editor de CSV;
- aplicação específica de triagem;
- futura interface do projeto.

Cuidados:

- manter codificação UTF-8;
- não alterar os nomes das colunas;
- não remover `record_id`;
- não reordenar manualmente os identificadores;
- não converter DOI em formato numérico;
- não alterar valores A1, A2 e A3;
- não usar vírgulas como separador interno de campos multivalorados;
- utilizar `;` para múltiplos códigos;
- salvar datas no padrão ISO;
- criar backup antes de operações em massa.

## 22. Validação da matriz

A estrutura pode ser validada com:

```bash
python - <<'PY'
import pandas as pd

path = "outputs/matriz_triagem_neuro_v4_3f.csv"

df = pd.read_csv(
    path,
    dtype=str,
    keep_default_na=False,
)

required_columns = {
    "record_id",
    "source_record_id",
    "duplicate_group",
    "title",
    "abstract",
    "abstract_available",
    "suggested_priority",
    "adjudicated_priority",
    "final_priority",
    "screening_decision",
    "screening_reason_code",
    "screening_reason",
    "screening_evidence",
    "screened_by",
    "screening_date",
    "second_review_required",
    "screening_notes",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise SystemExit(
        f"Missing columns: {sorted(missing_columns)}"
    )

if not df["record_id"].is_unique:
    raise SystemExit("record_id is not unique")

valid_decisions = {
    "",
    "Include",
    "Exclude",
    "Uncertain",
}

invalid_decisions = sorted(
    set(df["screening_decision"]) - valid_decisions
)

if invalid_decisions:
    raise SystemExit(
        f"Invalid decisions: {invalid_decisions}"
    )

valid_booleans = {
    "true",
    "false",
}

invalid_abstract_values = sorted(
    set(df["abstract_available"]) - valid_booleans
)

if invalid_abstract_values:
    raise SystemExit(
        "Invalid abstract_available values: "
        f"{invalid_abstract_values}"
    )

invalid_second_review_values = sorted(
    set(df["second_review_required"])
    - valid_booleans
)

if invalid_second_review_values:
    raise SystemExit(
        "Invalid second_review_required values: "
        f"{invalid_second_review_values}"
    )

print("Rows:", len(df))
print("Unique IDs:", df["record_id"].is_unique)
print()
print("Screening decisions:")
print(df["screening_decision"].value_counts())
print()
print("Second review required:")
print(df["second_review_required"].value_counts())
print()
print("Validation completed successfully.")
PY
```

## 23. Acompanhamento operacional do progresso

O acompanhamento da triagem é realizado por:

```text
scripts/screening_progress.py
```

O script é somente leitura. Ele não altera a matriz, não preenche
decisões e não modifica prioridades.

Antes de consultar o progresso, recomenda-se validar a matriz:

```bash
python scripts/validate_screening_matrix.py
python scripts/screening_progress.py
```

A execução padrão é:

```bash
python scripts/screening_progress.py
```

O relatório apresenta:

- total de registros;
- registros triados e pendentes;
- percentual de conclusão;
- distribuição entre `Include`, `Exclude`, `Uncertain` e `Pending`;
- progresso por A1, A3 e A2;
- cobertura de resumos;
- estado dos grupos candidatos a duplicata;
- registros marcados para segunda revisão.

No baseline inicial da v4.3f, a saída esperada é:

```text
Total:      254
Completed:  0
Pending:    254
Progress:   0.0%

A1: 71 registros
A3: 63 registros
A2: 120 registros

Available abstracts: 214
Missing abstracts: 40

Potential duplicate groups: 2
Potential duplicate records: 4

Second-review flags: 44
```

### 23.1 Definição de registro triado

Um registro é contabilizado como triado quando
`screening_decision` contém um dos valores:

```text
Include
Exclude
Uncertain
```

Um registro `Uncertain` conta como concluído na primeira triagem,
mas permanece sujeito a recuperação de informações ou segunda revisão.

Registros com `screening_decision` vazio são contabilizados como
`Pending`.

### 23.2 Progresso por prioridade

O relatório preserva a ordem operacional da matriz:

```text
A1 → A3 → A2
```

Para cada prioridade são apresentados:

```text
total
completed
pending
include
exclude
uncertain
progress_percent
```

Esse detalhamento permite acompanhar se a triagem está avançando na
ordem definida pelo protocolo.

### 23.3 Cobertura de resumos

O relatório distingue:

```text
available_total
missing_total
missing_pending
missing_screened
missing_uncertain
```

A recuperação de um resumo deve ser registrada conforme a seção 20
deste documento.

### 23.4 Grupos candidatos a duplicata

Para os registros com `duplicate_group`, o relatório apresenta:

```text
groups_total
records_total
groups_pending
groups_resolved
groups_ambiguous
records_pending
```

Um grupo é considerado resolvido pelo relatório quando:

```text
não há registros pendentes
e
existe exatamente um registro marcado como Include
```

Grupos com decisões completas, mas sem exatamente uma inclusão, são
apresentados como ambíguos. A validação metodológica da decisão continua
sendo responsabilidade de `validate_screening_matrix.py`.

### 23.5 Segunda revisão

O relatório apresenta:

```text
flagged_total
awaiting_initial_screening
screened_but_still_flagged
uncertain_flagged
```

A matriz atual possui o campo:

```text
second_review_required
```

mas ainda não possui:

```text
second_review_completed
```

Por esse motivo, o relatório não afirma que uma segunda revisão foi
concluída. Ele apenas informa que o registro continua marcado para essa
etapa.

### 23.6 Listagem de pendências

Para exibir os primeiros registros pendentes na ordem da matriz:

```bash
python scripts/screening_progress.py \
  --pending-limit 10
```

Cada linha apresenta:

```text
record_id | prioridade | ano | título
```

O parâmetro deve receber zero ou um número inteiro positivo.

### 23.7 Relatórios estruturados

Relatório JSON:

```bash
python scripts/screening_progress.py \
  --json-output outputs/progresso_triagem_v4_3f.json
```

Relatório CSV em formato longo:

```bash
python scripts/screening_progress.py \
  --csv-output outputs/progresso_triagem_v4_3f.csv
```

Os dois formatos podem ser gerados na mesma execução:

```bash
python scripts/screening_progress.py \
  --json-output outputs/progresso_triagem_v4_3f.json \
  --csv-output outputs/progresso_triagem_v4_3f.csv
```

Esses arquivos são derivados da matriz e permanecem fora do Git.

### 23.8 Uso após cada sessão

Ao final de cada sessão de triagem, executar:

```bash
python scripts/validate_screening_matrix.py

python scripts/screening_progress.py \
  --json-output outputs/progresso_triagem_v4_3f.json \
  --csv-output outputs/progresso_triagem_v4_3f.csv
```

O primeiro comando verifica integridade. O segundo registra o estado
operacional da triagem.

## 24. Critérios mínimos de completude

Um registro com decisão diferente de vazio deve possuir:

```text
screening_decision
screening_reason_code
screening_reason
screening_evidence
screened_by
screening_date
second_review_required
```

Exceções devem ser justificadas em `screening_notes`.

## 25. Encerramento da triagem

A triagem por título e resumo será considerada concluída quando:

- todos os 254 registros tiverem decisão;
- todos os excluídos tiverem código e justificativa;
- todos os registros sem resumo tiverem sido revisados;
- todos os candidatos a duplicata tiverem decisão;
- todos os registros `Uncertain` tiverem segunda revisão;
- todos os registros incluídos estiverem preparados para recuperação do texto completo;
- não houver IDs duplicados;
- não houver valores inválidos nas colunas controladas;
- uma cópia congelada da matriz tiver sido gerada.

## 26. Artefatos de exportação

A matriz de triagem permanece como fonte de verdade:

```text
outputs/matriz_triagem_neuro_v4_3f.csv
```

O exportador gera conjuntos derivados conforme o valor de
`screening_decision`.

Os nomes utilizam um rótulo configurável:

```text
{label}
```

Com o rótulo padrão `v4_3f`, os artefatos são:

```text
outputs/estudos_incluidos_titulo_resumo_v4_3f.csv
outputs/estudos_excluidos_titulo_resumo_v4_3f.csv
outputs/estudos_incertos_titulo_resumo_v4_3f.csv
outputs/estudos_pendentes_titulo_resumo_v4_3f.csv
outputs/estudos_para_texto_completo_v4_3f.csv
outputs/manifesto_exportacao_triagem_v4_3f.json
```

Quando não existem registros pendentes, também é gerado:

```text
outputs/matriz_triagem_neuro_v4_3f_concluida.csv
```

O snapshot concluído não é criado durante uma exportação parcial.

Todos esses arquivos são derivados da matriz e permanecem fora do Git.

## 27. Exportação e consolidação dos resultados

A exportação é realizada por:

```text
scripts/export_screening_results.py
```

O script:

- lê a matriz sem modificá-la;
- verifica a estrutura mínima necessária;
- separa os registros por decisão;
- preserva todas as colunas e a ordem original;
- calcula contagens;
- gera arquivos CSV com escrita atômica;
- calcula checksums SHA-256;
- gera um manifesto de auditoria;
- protege arquivos existentes contra sobrescrita;
- verifica se o checksum da matriz permaneceu inalterado.

### 27.1 Conjuntos exportados

As regras de separação são:

```text
Include
    screening_decision = Include

Exclude
    screening_decision = Exclude

Uncertain
    screening_decision = Uncertain

Pending
    screening_decision vazio

Full text
    screening_decision = Include ou Uncertain
```

O conjunto para texto completo utiliza uma regra conservadora:

```text
Include + Uncertain
```

Registros `Uncertain` não são tratados como inclusões definitivas. Eles
são preservados para recuperação de informação, segunda revisão ou
leitura do texto completo.

### 27.2 Simulação segura

Para validar contagens e nomes de arquivos sem escrever artefatos:

```bash
python scripts/export_screening_results.py \
  --dry-run
```

No baseline inicial da v4.3f, a saída esperada é:

```text
Total:       254
Completed:   0
Include:     0
Exclude:     0
Uncertain:   0
Pending:     254
Full text:   0

Complete:    no
Completed matrix snapshot: not generated
```

Durante a triagem em andamento, esse é o modo padrão recomendado para
consultar o comportamento do exportador.

### 27.3 Exportação parcial

Uma exportação parcial ocorre quando ainda existem registros com:

```text
screening_decision vazio
```

Ela pode ser utilizada para:

- revisar o trabalho já realizado;
- compartilhar um snapshot operacional;
- analisar provisoriamente as decisões;
- preparar uma sessão de segunda revisão;
- verificar os registros ainda pendentes.

Na exportação parcial:

```text
pending > 0
screening_complete = false
```

São gerados:

```text
Include
Exclude
Uncertain
Pending
Full text
Manifesto
```

Não é gerado:

```text
completed_matrix
```

Uma exportação parcial não representa:

- encerramento da triagem;
- corpus final incluído;
- consolidação metodológica;
- conjunto congelado para síntese;
- resultado final da seleção.

Para evitar que um snapshot parcial seja confundido com a consolidação
oficial, utilizar um rótulo explícito:

```bash
PARTIAL_LABEL="v4_3f_partial_$(date +%Y%m%d_%H%M%S)"

python scripts/export_screening_results.py \
  --label "$PARTIAL_LABEL"
```

Exemplo de arquivo resultante:

```text
estudos_incluidos_titulo_resumo_v4_3f_partial_20260804_210000.csv
```

### 27.4 Consolidação final

A consolidação final deve ser executada somente depois do encerramento
metodológico descrito na seção 25.

Fluxo recomendado:

```bash
python scripts/validate_screening_matrix.py \
  --strict

python scripts/screening_progress.py

python scripts/export_screening_results.py \
  --require-complete \
  --label v4_3f
```

O parâmetro:

```text
--require-complete
```

interrompe a execução quando ainda existem registros pendentes.

Exemplo:

```text
ERROR: The matrix is incomplete:
254 pending records remain.
```

A consolidação com ausência de pendências produz:

```text
pending = 0
screening_complete = true
completed_matrix gerada
```

A ausência de registros pendentes representa completude operacional da
primeira decisão para todos os registros.

Ela não substitui a verificação metodológica de:

- justificativas e evidências;
- candidatos a duplicata;
- resumos ausentes;
- registros `Uncertain`;
- necessidade de segunda revisão;
- critérios de encerramento da seção 25.

O campo `screening_complete` do manifesto significa especificamente:

```text
não existem decisões vazias
```

Ele não deve ser interpretado isoladamente como confirmação de que todas
as etapas de revisão humana foram encerradas.

### 27.5 Snapshot da matriz concluída

O arquivo:

```text
matriz_triagem_neuro_{label}_concluida.csv
```

é gerado apenas quando:

```text
pending = 0
```

O snapshot:

- preserva todas as 22 colunas;
- preserva a ordem dos registros;
- registra o estado da matriz no momento da exportação;
- não substitui a matriz de trabalho;
- deve ser tratado como artefato congelado da etapa.

### 27.6 Manifesto de auditoria

Cada exportação escrita em disco gera:

```text
manifesto_exportacao_triagem_{label}.json
```

O manifesto registra:

```text
schema_version
generated_at
input.path
input.sha256
input.rows
screening_complete
counts
full_text_rule
outputs
```

Para cada CSV exportado, o manifesto contém:

```text
path
rows
sha256
```

As contagens incluem:

```text
total
completed
include
exclude
uncertain
pending
full_text
```

O manifesto permite verificar:

- qual matriz originou os arquivos;
- quantos registros foram exportados;
- quais arquivos foram produzidos;
- se os arquivos continuam íntegros;
- se a exportação foi parcial ou operacionalmente completa.

O manifesto não inclui o próprio checksum, pois ele é criado depois dos
demais arquivos exportados.

### 27.7 Proteção contra sobrescrita

Por padrão, o exportador não substitui arquivos existentes.

Quando qualquer destino planejado já existe:

```text
ERROR: Output files already exist.
Use --force to overwrite.
```

A opção:

```text
--force
```

somente deve ser utilizada quando:

- os arquivos anteriores já foram preservados;
- o rótulo utilizado está correto;
- a nova exportação deve substituir deliberadamente a anterior.

Preferir um novo rótulo para snapshots intermediários.

Exemplo:

```bash
python scripts/export_screening_results.py \
  --label v4_3f_partial_session_02
```

### 27.8 Rótulo dos arquivos

O parâmetro:

```text
--label
```

aceita apenas:

```text
letras
números
ponto
sublinhado
hífen
```

Exemplo válido:

```text
v4_3f-partial.1
```

Valores com espaços, barras ou caminhos relativos são rejeitados.

### 27.9 Diretório de saída

O diretório padrão é:

```text
outputs/
```

Um diretório alternativo pode ser informado:

```bash
python scripts/export_screening_results.py \
  --output-dir outputs/snapshots \
  --label v4_3f_partial_session_01
```

### 27.10 Sequência operacional recomendada

Durante a triagem:

```bash
python scripts/validate_screening_matrix.py

python scripts/screening_progress.py

python scripts/export_screening_results.py \
  --dry-run
```

Para um snapshot parcial deliberado:

```bash
PARTIAL_LABEL="v4_3f_partial_$(date +%Y%m%d_%H%M%S)"

python scripts/export_screening_results.py \
  --label "$PARTIAL_LABEL"
```

Para a consolidação final:

```bash
python scripts/validate_screening_matrix.py \
  --strict

python scripts/screening_progress.py

python scripts/export_screening_results.py \
  --require-complete \
  --label v4_3f
```

## 28. Testes automatizados

Executar os testes da inicialização da matriz:

```bash
python -m unittest \
  tests.test_screening_matrix \
  -v
```

Executar os testes do validador:

```bash
python -m unittest \
  tests.test_validate_screening_matrix \
  -v
```

Executar os testes do relatório de progresso:

```bash
python -m unittest \
  tests.test_screening_progress \
  -v
```

Executar os testes do exportador:

```bash
python -m unittest \
  tests.test_export_screening_results \
  -v
```

O exportador possui testes com matrizes sintéticas completas e
incompletas. Os arquivos são criados em diretórios temporários e
removidos automaticamente.

Os testes cobrem:

- validação do rótulo;
- colunas obrigatórias;
- IDs vazios ou duplicados;
- decisões inválidas;
- decisões preenchidas de forma incompleta;
- valores booleanos;
- separação dos subconjuntos;
- regra `Include + Uncertain`;
- exportação parcial;
- consolidação sem pendências;
- proteção contra sobrescrita;
- uso de `--force`;
- geração do snapshot concluído;
- manifesto JSON;
- contagens;
- checksums;
- preservação da matriz de entrada;
- modo `--dry-run`;
- proteção `--require-complete`.

Executar todos os testes do workflow de triagem:

```bash
python -m unittest \
  tests.test_screening_matrix \
  tests.test_validate_screening_matrix \
  tests.test_screening_progress \
  tests.test_export_screening_results \
  -v
```

Executar a suíte completa do projeto:

```bash
python -m unittest discover \
  -s tests \
  -p "test_*.py" \
  -v
```

Após a introdução do exportador, o baseline esperado é:

```text
Ran 69 tests

OK
```

## 29. Validação automatizada da matriz

A matriz deve ser validada antes e depois de cada sessão de triagem.

O validador está disponível em:

```text
scripts/validate_screening_matrix.py
```

Execução padrão:

```bash
python scripts/validate_screening_matrix.py
```

O validador verifica:

- presença das 22 colunas obrigatórias;
- identificadores vazios ou duplicados;
- distribuição do baseline da v4.3f;
- valores válidos de prioridade;
- consistência entre prioridade sugerida, adjudicada e final;
- consistência entre resumo e `abstract_available`;
- valores booleanos;
- completude das decisões humanas;
- compatibilidade dos códigos de inclusão e exclusão;
- datas no padrão ISO;
- necessidade de segunda revisão;
- grupos candidatos a duplicata;
- preservação dos campos bibliográficos do corpus adjudicado;
- alterações de resumo sem registro da fonte.

Registros ainda não triados são considerados válidos. As regras de
completude são aplicadas quando `screening_decision` recebe um valor.

Execução sem comparação com o corpus original:

```bash
python scripts/validate_screening_matrix.py \
  --skip-source-check
```

Esse modo deve ser utilizado somente em testes isolados.

Relatório JSON:

```bash
python scripts/validate_screening_matrix.py \
  --json-output outputs/validacao_triagem_v4_3f.json
```

O relatório JSON contém:

```text
record_count
error_count
warning_count
issues
```

Modo estrito:

```bash
python scripts/validate_screening_matrix.py \
  --strict
```

No modo padrão:

```text
erros → código de saída 1
avisos → código de saída 0
```

No modo estrito:

```text
erros → código de saída 1
avisos → código de saída 2
sem problemas → código de saída 0
```

O modo estrito é recomendado para validações finais e automações de CI.

## 30. Estado atual do workflow

```text
Versão do pipeline: v4.3f
Versão da taxonomia: 1.6
Versão do workflow: v4.4 — exportação e consolidação

Registros centrais: 254
A1: 71
A3: 63
A2: 120

Registros com resumo: 214
Registros sem resumo: 40

Grupos candidatos a duplicata: 2
Registros candidatos a duplicata: 4

Registros marcados para segunda revisão: 44
Decisões iniciais preenchidas: 0
Progresso inicial: 0.0%
```

Componentes implementados:

```text
scripts/init_screening_matrix.py
scripts/validate_screening_matrix.py
scripts/screening_progress.py
scripts/export_screening_results.py
```

Testes correspondentes:

```text
tests/test_screening_matrix.py
tests/test_validate_screening_matrix.py
tests/test_screening_progress.py
tests/test_export_screening_results.py
```

Responsabilidades:

```text
init_screening_matrix.py
    cria a matriz inicial

validate_screening_matrix.py
    verifica integridade estrutural e metodológica

screening_progress.py
    apresenta o estado operacional da triagem

export_screening_results.py
    gera subconjuntos, snapshot concluído e manifesto
```

O corpus real ainda não foi triado.

No estado atual:

```text
Include: 0
Exclude: 0
Uncertain: 0
Pending: 254
```

Por esse motivo, somente o modo `--dry-run` foi executado no corpus real.
Os testes de escrita utilizaram exclusivamente matrizes sintéticas em
diretórios temporários.

## 31. Roadmap

O roadmap separa a infraestrutura técnica da execução metodológica da
triagem, da avaliação por texto completo e da síntese das evidências.

### 31.1 v4.3f — Baseline bibliográfico e classificação

Status:

```text
Concluído
```

Entregas:

- consolidação de 864 registros;
- limpeza e deduplicação;
- taxonomia 1.6;
- classificação A1, A2, A3, B e D;
- adjudicação manual;
- corpus central com 254 registros;
- documentação metodológica;
- release reproduzível.

Baseline final:

```text
A1: 71
A2: 120
A3: 63
B: 564
D: 46
```

### 31.2 v4.4 — Infraestrutura da triagem

Status:

```text
Concluído
```

Entregas:

- inicialização reproduzível da matriz;
- preservação das classificações automática e adjudicada;
- identificação de registros sem resumo;
- identificação de candidatos a duplicata;
- validação estrutural e metodológica;
- acompanhamento operacional do progresso;
- exportação de Include, Exclude, Uncertain e Pending;
- preparação conservadora de candidatos ao texto completo;
- manifestos e checksums;
- 69 testes automatizados.

Componentes:

```text
scripts/init_screening_matrix.py
scripts/validate_screening_matrix.py
scripts/screening_progress.py
scripts/export_screening_results.py
```

Estado operacional inicial:

```text
Registros: 254
Triados: 0
Pendentes: 254
Sem resumo: 40
Candidatos a duplicata: 4
Marcados para segunda revisão: 44
```

### 31.3 v4.5 — Operação e rastreabilidade da triagem

Status:

```text
Próximo ciclo
```

#### 31.3.1 Controle de alterações humanas e snapshots

Componentes planejados:

```text
scripts/snapshot_screening_session.py
tests/test_snapshot_screening_session.py
docs/screening_sessions.md
```

Objetivos:

- congelar o estado da matriz após cada sessão;
- registrar o checksum da matriz;
- comparar a sessão atual com o snapshot anterior;
- identificar registros e campos alterados;
- registrar responsável, data e identificador da sessão;
- produzir histórico auditável;
- impedir sobrescrita silenciosa;
- não modificar a matriz de trabalho.

Artefatos previstos:

```text
outputs/screening_sessions/
└── SESSION_ID/
    ├── matriz_triagem.csv
    ├── alteracoes.csv
    └── manifesto.json
```

Tipos iniciais de alteração:

```text
decision_added
decision_changed
reason_code_changed
reason_changed
evidence_changed
review_flag_changed
notes_changed
abstract_recovered
abstract_changed
bibliographic_field_changed
```

#### 31.3.2 Recuperação de resumos

Objetivos:

- preparar o inventário dos 40 registros sem resumo;
- registrar fontes consultadas;
- identificar resumos recuperados;
- preservar a origem e a data da recuperação;
- manter rastreabilidade das alterações;
- separar ausência confirmada de busca ainda não realizada.

Componente provisório:

```text
scripts/prepare_abstract_recovery.py
```

#### 31.3.3 Resolução de candidatos a duplicata

Objetivos:

- comparar DOI, título, autores, ano e venue;
- identificar a versão canônica;
- distinguir duplicata, preprint e publicação final;
- registrar E10 ou E11;
- preservar as decisões no histórico.

Baseline:

```text
2 grupos
4 registros
```

#### 31.3.4 Piloto de triagem A1

Escopo inicial:

```text
10 a 15 registros A1
```

O piloto deverá avaliar:

- clareza dos critérios;
- adequação dos códigos I, E e U;
- qualidade das evidências;
- tempo médio por registro;
- frequência de incerteza;
- dúvidas entre A1 e A2;
- necessidade de novos códigos;
- regras de segunda revisão.

#### 31.3.5 Revisão do protocolo

Após o piloto:

- consolidar dificuldades;
- ajustar instruções;
- versionar mudanças nos critérios;
- revisar exemplos;
- congelar o protocolo para a triagem completa.

#### 31.3.6 Triagem completa

Ordem:

```text
A1 → A3 → A2
```

Etapas:

1. concluir A1;
2. revisar os casos incertos de A1;
3. concluir A3;
4. revisar os casos incertos de A3;
5. concluir A2;
6. revisar os casos incertos de A2;
7. resolver os candidatos a duplicata;
8. revisar os registros sem resumo;
9. executar segunda revisão;
10. consolidar os resultados.

#### 31.3.7 Encerramento da primeira triagem

Critérios:

```text
pending = 0
decisões completas
duplicatas resolvidas
registros sinalizados tratados
validação estrita concluída
snapshot final congelado
exportação executada com --require-complete
```

### 31.4 v4.6 — Triagem por texto completo

Objetivos:

- preparar a matriz de texto completo;
- controlar disponibilidade e origem dos documentos;
- aplicar critérios de elegibilidade;
- registrar motivos de exclusão;
- executar segunda revisão;
- acompanhar o progresso;
- consolidar o corpus final;
- gerar contagens do fluxo de seleção.

Componentes previstos:

```text
scripts/init_full_text_matrix.py
scripts/validate_full_text_matrix.py
scripts/full_text_progress.py
scripts/export_full_text_results.py
```

### 31.5 v4.7 — Extração estruturada de evidências

Objetivos:

- definir o esquema de extração;
- caracterizar tecnologia neural e modalidade de sinal;
- registrar tarefa e saída linguística;
- identificar o papel dos modelos de linguagem;
- caracterizar arquiteturas de integração;
- registrar participantes, métodos e métricas;
- extrair resultados e limitações;
- codificar riscos, privacidade e governança;
- registrar confiança, autonomia e supervisão;
- avaliar qualidade metodológica;
- preservar rastreabilidade entre evidência e fonte.

### 31.6 v4.8 — Análise e mapeamento

Análises previstas:

- evolução temporal;
- distribuição por venues;
- distribuição por A1, A2 e A3;
- modalidades neurais;
- tipos de saída linguística;
- papel dos modelos de linguagem;
- arquiteturas de integração;
- populações estudadas;
- métricas;
- riscos e mecanismos de mitigação;
- lacunas técnicas, humanas e de governança.

### 31.7 v5.0 — Síntese e publicação

Entregas previstas:

- corpus final congelado;
- síntese narrativa e temática;
- mapas de evidências;
- tabelas e figuras;
- fluxo de seleção dos estudos;
- pacote reproduzível;
- release pública compatível com direitos de redistribuição;
- material para artigo e dissertação;
- documentação das limitações.
