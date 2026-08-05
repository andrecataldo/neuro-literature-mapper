# Recuperação estruturada de resumos

## 1. Objetivo

O fluxo de recuperação de resumos organiza a busca, o registro da fonte,
a validação e a futura incorporação de resumos ausentes na matriz de
triagem.

O processo foi criado para os registros centrais da v4.3f que não
possuem resumo disponível.

A implementação foi dividida em duas fases:

```text
v4.5.2a — preparação e controle da fila
v4.5.2b — validação e aplicação dos resumos recuperados
```

A fase de preparação não consulta serviços externos e não altera a
matriz de triagem.

## 2. Componentes

Componente implementado na fase v4.5.2a:

```text
scripts/prepare_abstract_recovery.py
```

Testes:

```text
tests/test_prepare_abstract_recovery.py
```

Componentes previstos para a fase v4.5.2b:

```text
scripts/validate_abstract_recovery.py
scripts/apply_abstract_recovery.py
tests/test_validate_abstract_recovery.py
tests/test_apply_abstract_recovery.py
```

Os nomes da fase v4.5.2b são provisórios até a definição final do
contrato de validação e aplicação.

## 3. Princípios

### 3.1 Preservação da matriz

A fonte de verdade permanece:

```text
outputs/matriz_triagem_neuro_v4_3f.csv
```

O script de preparação:

- lê a matriz;
- valida sua estrutura mínima;
- seleciona os registros sem resumo;
- cria uma fila derivada;
- calcula checksums;
- confirma que a matriz não mudou durante a execução.

Ele não escreve na matriz de triagem.

### 3.2 Separação entre busca e aplicação

A recuperação de um texto não implica sua aplicação automática.

O processo separa:

```text
localizar o resumo
registrar a fonte
revisar o conteúdo
validar a fila
aplicar na matriz
executar nova validação
congelar um snapshot da sessão
```

Essa separação reduz o risco de incorporar conteúdo incorreto,
parafraseado ou associado ao registro errado.

### 3.3 Rastreabilidade da fonte

Todo resumo recuperado deve indicar de onde foi obtido.

O registro da fonte deve permitir que outra pessoa:

- encontre novamente a publicação;
- confirme que o resumo pertence ao registro;
- compare o conteúdo aplicado;
- identifique quando e por quem a recuperação foi realizada.

### 3.4 Nenhum resumo gerado por IA

O campo `recovered_abstract` deve conter o resumo publicado pela fonte
consultada.

Não deve conter:

- resumo produzido por modelo de linguagem;
- paráfrase do artigo;
- síntese criada pelo pesquisador;
- tradução automática apresentada como texto original;
- reconstrução baseada apenas no título;
- conteúdo inferido a partir de citações de terceiros.

Quando o resumo original não for encontrado, utilizar:

```text
recovery_status = Not found
```

### 3.5 Segunda revisão preservada

A recuperação do resumo não remove automaticamente:

```text
second_review_required = true
```

O novo conteúdo deve ser revisado antes de qualquer decisão sobre a
necessidade de segunda revisão.

## 4. Entrada

Entrada padrão:

```text
outputs/matriz_triagem_neuro_v4_3f.csv
```

A matriz deve possuir as 22 colunas do workflow de triagem.

Antes da preparação, recomenda-se executar:

```bash
python scripts/validate_screening_matrix.py
```

## 5. Regra de seleção

Um registro entra na fila quando:

```text
abstract_available = false
```

e o campo `abstract` contém um marcador reconhecido de ausência.

Entre os marcadores aceitos estão:

```text
vazio
N/A
NA
NaN
None
Null
Not available
Not informed
No abstract
No abstract available
Sem resumo
Resumo indisponível
```

A comparação:

- ignora diferenças entre maiúsculas e minúsculas;
- normaliza espaços;
- remove acentos para avaliar os marcadores.

Um campo que contenha texto científico válido não é tratado como resumo
ausente.

## 6. Baseline da v4.3f

O `dry-run` no corpus real identificou:

```text
Registros da matriz: 254
Registros sem resumo: 40
Pendentes de recuperação: 40
```

Distribuição:

```text
A1-central-integracao-llm: 10
A2-central-decoding-linguagem: 16
A3-central-riscos-governanca: 14
```

A soma das três categorias corresponde aos 40 registros.

Entre esses registros:

```text
Candidatos a duplicata: 0
```

Os quatro candidatos a duplicata do corpus central possuem resumo e,
por isso, não aparecem nessa fila.

## 7. Artefatos

A preparação gera:

```text
outputs/matriz_recuperacao_resumos_v4_3f.csv
outputs/manifesto_preparacao_recuperacao_resumos_v4_3f.json
```

Esses arquivos são derivados e permanecem fora do Git.

## 8. Estrutura da fila

A fila possui 26 colunas:

```text
record_id
source_record_id
matrix_row
duplicate_group
suggested_priority
adjudicated_priority
final_priority
title
authors
year
venue
doi
url
original_abstract
original_abstract_available
screening_decision
second_review_required
original_screening_notes
recovery_status
recovery_source_type
recovery_source_name
recovery_source_url
recovery_date
recovered_by
recovered_abstract
recovery_notes
```

## 9. Campos de identificação e contexto

### `record_id`

Identificador estável do registro na matriz.

A associação entre a fila e a matriz deve utilizar esse campo.

### `source_record_id`

Identificador do registro no corpus que originou a matriz.

### `matrix_row`

Número da linha no arquivo CSV original, considerando o cabeçalho como
primeira linha.

Exemplo:

```text
matrix_row = 3
```

indica que o registro está na terceira linha física do CSV.

Esse campo é informativo. A futura aplicação deverá utilizar
`record_id`, e não a posição da linha, para localizar o registro.

### `duplicate_group`

Grupo candidato a duplicata, quando aplicável.

No baseline dos 40 registros sem resumo, esse campo está vazio para
todos os registros.

## 10. Campos de prioridade

A fila preserva:

```text
suggested_priority
adjudicated_priority
final_priority
```

Esses campos servem para organizar a busca e não devem ser alterados
durante a recuperação.

A ordem operacional recomendada continua:

```text
A1 → A3 → A2
```

A ordem física da fila preserva a ordem original da matriz.

## 11. Campos bibliográficos

Os campos abaixo são copiados da matriz:

```text
title
authors
year
venue
doi
url
```

Eles auxiliam na identificação da publicação.

Durante a recuperação, esses campos devem ser tratados como somente
leitura.

Uma inconsistência bibliográfica encontrada durante a busca deve ser
descrita em:

```text
recovery_notes
```

Ela não deve ser corrigida diretamente na fila nem aplicada
automaticamente à matriz.

## 12. Estado original do resumo e da triagem

A fila preserva:

```text
original_abstract
original_abstract_available
screening_decision
second_review_required
original_screening_notes
```

Esses campos permitem verificar o estado do registro no momento em que a
fila foi preparada.

Eles devem ser tratados como somente leitura.

## 13. Campos editáveis

Os campos destinados ao trabalho de recuperação são:

```text
recovery_status
recovery_source_type
recovery_source_name
recovery_source_url
recovery_date
recovered_by
recovered_abstract
recovery_notes
```

Nenhum outro campo deve ser editado durante essa atividade.

## 14. Status da recuperação

Valores controlados:

```text
Pending
In progress
Recovered
Not found
```

### 14.1 `Pending`

O registro ainda não foi pesquisado.

Estado inicial de todos os registros da fila.

Campos de recuperação devem permanecer vazios.

### 14.2 `In progress`

A busca foi iniciada, mas ainda não existe resultado conclusivo.

Utilizar quando:

- algumas fontes já foram consultadas;
- existe uma possível correspondência ainda não confirmada;
- o texto completo precisa ser verificado;
- há dúvida sobre a versão correta da publicação;
- a busca será retomada em outra sessão.

As fontes já consultadas devem ser registradas em `recovery_notes`.

### 14.3 `Recovered`

O resumo foi encontrado e sua associação com o registro foi confirmada.

Deve possuir:

```text
recovery_source_type
recovery_source_name
recovery_source_url
recovery_date
recovered_by
recovered_abstract
```

O campo `recovery_notes` pode registrar detalhes adicionais.

### 14.4 `Not found`

A busca foi concluída sem localizar um resumo verificável.

Deve possuir:

```text
recovery_date
recovered_by
recovery_notes
```

`recovery_notes` deve listar as fontes consultadas e explicar por que a
busca foi encerrada.

O campo `recovered_abstract` deve permanecer vazio.

## 15. Tipos de fonte

O campo:

```text
recovery_source_type
```

ainda não possui validação técnica na fase v4.5.2a.

Valores recomendados:

```text
Publisher
Proceedings
Repository
Index
Full text
Author page
Institutional page
Other
```

Esses valores poderão ser formalizados como vocabulário controlado na
fase v4.5.2b.

## 16. Hierarquia recomendada de fontes

A busca deve priorizar fontes que permitam confirmar a identidade e o
conteúdo da publicação.

Ordem recomendada:

```text
1. página oficial do editor ou do evento
2. registro associado ao DOI
3. repositório institucional ou temático
4. base bibliográfica que apresente o resumo integral
5. texto completo da publicação
6. página institucional ou pessoal do autor
7. outra fonte verificável
```

Um agregador pode ajudar a localizar a publicação, mas o resumo deve ser
confirmado, quando possível, em uma fonte primária ou institucional.

## 17. Validação da identidade da publicação

Antes de registrar um resumo como recuperado, comparar:

```text
título
autores
ano
venue
DOI
URL
```

Não é necessário que todos os campos estejam disponíveis, mas a
correspondência deve ser suficiente para evitar associação com outro
trabalho de título semelhante.

Casos que exigem atenção:

- preprint e versão final;
- resumo de conferência e artigo completo;
- capítulo e artigo com título semelhante;
- versão traduzida do título;
- publicação corrigida;
- registros com ano online e ano de edição diferentes;
- trabalhos homônimos;
- página que exibe apenas trechos do resumo.

Quando houver dúvida, manter:

```text
recovery_status = In progress
```

e registrar a questão em `recovery_notes`.

## 18. Registro do conteúdo recuperado

O campo:

```text
recovered_abstract
```

deve preservar o conteúdo publicado.

São permitidas apenas alterações de apresentação, como:

- remoção de quebras de linha artificiais;
- normalização de espaços consecutivos;
- união de parágrafos separados pelo formato da página.

Não devem ser alterados:

- palavras;
- ordem das frases;
- idioma;
- terminologia;
- números;
- resultados;
- conclusões;
- negações;
- limitações.

Quando a fonte apresentar seções como `Background`, `Methods` e
`Results`, os rótulos podem ser preservados.

## 19. Idioma

O resumo deve ser registrado no idioma em que aparece na fonte.

Uma tradução pode ser armazenada futuramente em campo separado, mas não
deve substituir o texto original em:

```text
recovered_abstract
```

## 20. Registro da fonte

### `recovery_source_name`

Nome legível da fonte.

Exemplos:

```text
IEEE Xplore
ACM Digital Library
PubMed
arXiv
Site oficial do evento
Repositório institucional
```

### `recovery_source_url`

URL específica utilizada para recuperar ou confirmar o resumo.

Deve apontar, sempre que possível, para a página do registro ou do
documento, e não para uma página genérica da plataforma.

### `recovery_date`

Data da recuperação no formato:

```text
YYYY-MM-DD
```

### `recovered_by`

Nome da pessoa que realizou e registrou a recuperação.

## 21. Preparação em modo seguro

Executar:

```bash
python scripts/prepare_abstract_recovery.py \
  --dry-run
```

O comando:

- valida a matriz;
- conta os registros sem resumo;
- monta a fila em memória;
- valida o esquema da fila;
- mostra a distribuição;
- não cria arquivos.

Resultado esperado para a v4.3f:

```text
Input rows:          254
Missing abstracts:   40
Pending recovery:    40
```

## 22. Geração oficial da fila

A geração somente deve ocorrer depois de:

```text
testes específicos aprovados
suíte completa aprovada
documentação revisada
dry-run com 40 registros
confirmação de que não existem artefatos anteriores
```

Comando:

```bash
python scripts/prepare_abstract_recovery.py
```

O script protege arquivos existentes.

Quando um dos destinos já existe:

```text
ERROR: Recovery artifacts already exist.
Use --force to overwrite.
```

## 23. Uso de `--force`

A opção:

```text
--force
```

substitui deliberadamente os artefatos existentes.

Ela não deve ser utilizada depois que a fila começar a ser preenchida.

Uma fila com trabalho humano deve ser preservada e receber um novo nome
ou cópia antes de qualquer regeneração.

Para preparar outro conjunto sem substituir o anterior, utilizar um
novo rótulo:

```bash
python scripts/prepare_abstract_recovery.py \
  --label v4_3f_recovery_02
```

## 24. Contagem esperada

O parâmetro padrão exige:

```text
40 registros sem resumo
```

Outra contagem pode ser informada:

```bash
python scripts/prepare_abstract_recovery.py \
  --expected-count 25
```

A verificação pode ser desativada com valor negativo:

```bash
python scripts/prepare_abstract_recovery.py \
  --expected-count -1
```

A desativação deve ser utilizada apenas em testes, experimentos ou
novas versões do corpus cuja contagem já tenha sido verificada por outro
meio.

## 25. Manifesto da preparação

O arquivo:

```text
manifesto_preparacao_recuperacao_resumos_v4_3f.json
```

registra:

```text
schema_version
generated_at
input
selection_rule
counts
initial_status
queue
```

### Entrada

```text
input.path
input.sha256
input.rows
```

### Contagens

```text
counts.missing_abstracts
counts.by_final_priority
counts.duplicate_candidates
counts.pending_recovery
counts.recovered
counts.not_found
```

Na preparação inicial:

```text
pending_recovery = 40
recovered = 0
not_found = 0
```

### Fila

```text
queue.path
queue.rows
queue.columns
queue.sha256
```

O manifesto permite verificar qual matriz originou a fila e se o CSV
permaneceu íntegro desde sua criação.

## 26. Verificação dos artefatos

Depois da geração oficial:

```bash
sha256sum \
  outputs/matriz_triagem_neuro_v4_3f.csv \
  outputs/matriz_recuperacao_resumos_v4_3f.csv
```

Os hashes devem ser diferentes, pois são arquivos com estruturas
distintas.

O checksum da matriz deve permanecer:

```text
adff6ac701110eaafc5afb02b97100cc4853cfb5bc4060e0311d6588a7edefab
```

Validar o manifesto:

```bash
python - <<'PY'
import hashlib
import json
from pathlib import Path


manifest_path = Path(
    "outputs/"
    "manifesto_preparacao_recuperacao_"
    "resumos_v4_3f.json"
)

manifest = json.loads(
    manifest_path.read_text(
        encoding="utf-8"
    )
)

queue_path = Path(
    manifest["queue"]["path"]
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


assert queue_path.exists()

assert manifest["queue"]["rows"] == 40
assert manifest["queue"]["columns"] == 26

assert (
    manifest["queue"]["sha256"]
    == sha256(queue_path)
)

assert (
    manifest["input"]["sha256"]
    == sha256(
        Path(
            "outputs/"
            "matriz_triagem_neuro_v4_3f.csv"
        )
    )
)

print(
    "Manifesto da recuperação validado."
)
PY
```

## 27. Trabalho manual na fila

A fila pode ser editada em uma ferramenta que preserve CSV UTF-8.

Durante o preenchimento:

- não ordenar definitivamente o arquivo;
- não remover registros;
- não adicionar registros;
- não alterar `record_id`;
- não alterar colunas de contexto;
- não modificar o cabeçalho;
- não converter DOI ou identificadores em números;
- não substituir o arquivo por formato XLSX sem preservar o CSV;
- manter backup ou snapshot entre sessões.

Antes de iniciar uma sessão, recomenda-se copiar a fila:

```bash
cp \
  outputs/matriz_recuperacao_resumos_v4_3f.csv \
  outputs/matriz_recuperacao_resumos_v4_3f_backup.csv
```

Backups locais derivados permanecem fora do Git.

## 28. Fase v4.5.2b

A fase de aplicação deverá:

- validar as 26 colunas;
- confirmar a integridade dos campos de contexto;
- comparar a fila com a matriz;
- validar os valores de `recovery_status`;
- exigir os campos correspondentes a cada status;
- validar datas;
- rejeitar IDs desconhecidos ou duplicados;
- rejeitar resumos vazios com status `Recovered`;
- rejeitar conteúdo preenchido com status `Not found`;
- produzir relatório antes de qualquer escrita;
- oferecer modo `--dry-run`;
- preservar uma cópia da matriz anterior;
- aplicar alterações atomicamente;
- confirmar o checksum da entrada;
- gerar manifesto de aplicação.

A aplicação autorizada deverá alterar somente:

```text
abstract
abstract_available
screening_notes
```

## 29. Conteúdo de `screening_notes`

Para um resumo recuperado, a futura aplicação deve acrescentar uma nota
rastreável sem apagar notas anteriores.

Formato recomendado:

```text
Resumo recuperado em YYYY-MM-DD por NOME.
Fonte: TIPO — NOME DA FONTE — URL.
```

Exemplo:

```text
Resumo recuperado em 2026-08-05 por Andre Cataldo.
Fonte: Publisher — IEEE Xplore — URL registrada na fila.
```

A redação final será definida pelo componente de aplicação.

## 30. Validação após a aplicação

Depois que a fase v4.5.2b atualizar a matriz:

```bash
python scripts/validate_screening_matrix.py

python scripts/screening_progress.py
```

O validador atual verifica:

- correspondência entre `abstract` e `abstract_available`;
- preservação dos campos bibliográficos;
- registro da fonte em `screening_notes`;
- necessidade de segunda revisão.

A alteração de resumo sem referência à recuperação ou à fonte pode gerar:

```text
ABSTRACT_CHANGED_WITHOUT_SOURCE
```

## 31. Snapshot após aplicação

Após validar a matriz, criar um snapshot da sessão:

```bash
python scripts/snapshot_screening_session.py \
  --session-id SESSION_ID \
  --reviewer "Andre Cataldo" \
  --previous PREVIOUS_SESSION_DIRECTORY \
  --note "Aplicação dos resumos recuperados." \
  --dry-run
```

Depois de revisar as alterações:

```bash
python scripts/snapshot_screening_session.py \
  --session-id SESSION_ID \
  --reviewer "Andre Cataldo" \
  --previous PREVIOUS_SESSION_DIRECTORY \
  --note "Aplicação dos resumos recuperados."
```

O arquivo `alteracoes.csv` deverá registrar:

```text
abstract_recovered
abstract_availability_changed
notes_changed
```

## 32. Testes automatizados

Executar os testes específicos:

```bash
python -m unittest \
  tests.test_prepare_abstract_recovery \
  -v
```

O módulo possui 27 testes.

Resultado esperado:

```text
Ran 27 tests

OK
```

Executar a suíte completa:

```bash
python -m unittest discover \
  -s tests \
  -p "test_*.py" \
  -v
```

Baseline confirmado após a inclusão do componente:

```text
Ran 118 tests

OK
```

Os testes utilizam somente matrizes sintéticas e diretórios temporários.

## 33. Limitações atuais

A fase v4.5.2a:

- não pesquisa fontes automaticamente;
- não consulta APIs;
- não valida URLs;
- não controla os tipos de fonte;
- não valida o preenchimento humano da fila;
- não aplica resumos na matriz;
- não mantém histórico interno de cada tentativa de busca;
- não distingue várias fontes consultadas em campos separados;
- não verifica similaridade textual;
- não detecta resumos gerados ou parafraseados;
- não confirma automaticamente a identidade da publicação;
- não cria snapshots da fila durante o preenchimento;
- não substitui revisão humana.

Esses controles serão tratados pela fase v4.5.2b ou por componentes
posteriores.

## 34. Estado atual

```text
Fase: v4.5.2a
Componente: preparação e controle da fila
Status: Concluído

Registros selecionados: 40
Status inicial: Pending
Fila oficial: gerada
Manifesto de preparação: auditado
Aplicação na matriz: ainda não implementada
```

Artefatos oficiais:

```text
outputs/matriz_recuperacao_resumos_v4_3f.csv
outputs/manifesto_preparacao_recuperacao_resumos_v4_3f.json
```

Estado confirmado da fila:

```text
Registros: 40
Pending: 40
Recovered: 0
Not found: 0

A1-central-integracao-llm: 10
A2-central-decoding-linguagem: 16
A3-central-riscos-governanca: 14

Candidatos a duplicata: 0
```

A geração e a auditoria confirmaram que:

- os 40 registros correspondem ao subconjunto sem resumo da matriz;
- a ordem original da matriz foi preservada;
- os identificadores são únicos;
- todos os registros começam com `recovery_status = Pending`;
- os campos editáveis começam vazios;
- a distribuição por prioridade soma 40 registros;
- nenhum registro da fila pertence a grupo candidato a duplicata;
- o contexto bibliográfico e operacional foi preservado;
- a matriz de triagem não foi modificada;
- o manifesto contém as contagens e os checksums esperados;
- os artefatos derivados permanecem fora do Git.

Checksum da matriz de triagem:

```text
adff6ac701110eaafc5afb02b97100cc4853cfb5bc4060e0311d6588a7edefab
```

Checksum da fila de recuperação:

```text
7cf2a855997c8eab0edec65f9d340b5fc0d63b667e0e0c73741ad12774fb3ad5
```

Validação automatizada:

```text
Testes específicos: 27
Suíte completa: 118
Falhas: 0
Erros: 0
```

As regras de exclusão do Git foram confirmadas para:

```text
outputs/*.csv
outputs/*.json
```

A fase v4.5.2a está encerrada.

A próxima fase é:

```text
v4.5.2b — validação e aplicação dos resumos recuperados
```

Antes da aplicação na matriz, a fila deverá ser preenchida e revisada
humanamente.

A fase v4.5.2b deverá validar esse preenchimento, gerar um relatório de
simulação e aplicar somente os campos autorizados:

```text
abstract
abstract_available
screening_notes
```
