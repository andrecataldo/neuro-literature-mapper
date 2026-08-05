# Controle de sessões e snapshots da triagem

## 1. Objetivo

O controle de sessões registra a evolução humana da triagem por título
e resumo sem alterar ou substituir a matriz de trabalho.

O componente responsável é:

```text
scripts/snapshot_screening_session.py
```

Cada execução pode:

- congelar uma cópia exata da matriz;
- comparar a matriz atual com uma sessão anterior;
- identificar alterações no nível de campo;
- registrar alertas para mudanças estruturais ou bibliográficas;
- produzir um manifesto com metadados e checksums;
- preservar uma cadeia auditável das sessões de triagem.

O script não preenche decisões, não corrige registros e não modifica a
matriz utilizada como entrada.

## 2. Princípios

### 2.1 Matriz de trabalho preservada

A matriz principal permanece em:

```text
outputs/matriz_triagem_neuro_v4_3f.csv
```

O script calcula seu checksum antes e depois da criação do snapshot.

A operação é interrompida quando o arquivo muda durante a execução.

### 2.2 Snapshots imutáveis

Cada sessão possui um diretório próprio:

```text
outputs/screening_sessions/SESSION_ID/
```

O script não oferece a opção `--force`.

Quando o diretório já existe, a execução é rejeitada:

```text
ERROR: Snapshot directory already exists:
outputs/screening_sessions/SESSION_ID
```

Um snapshot existente não deve ser sobrescrito, editado ou reutilizado
para representar outra sessão.

### 2.3 Comparação explícita

A comparação com uma sessão anterior somente ocorre quando o argumento:

```text
--previous
```

é informado.

O script não escolhe automaticamente o snapshot mais recente. Essa
decisão permanece explícita no comando executado pelo pesquisador.

### 2.4 Artefatos fora do Git

Os snapshots são artefatos locais derivados e permanecem ignorados por:

```text
outputs/screening_sessions/
```

O código, os testes e a documentação permanecem versionados no Git.

## 3. Estrutura dos artefatos

Cada sessão contém:

```text
outputs/screening_sessions/
└── SESSION_ID/
    ├── matriz_triagem.csv
    ├── alteracoes.csv
    └── manifesto.json
```

### 3.1 `matriz_triagem.csv`

É uma cópia binariamente idêntica da matriz no momento da sessão.

O arquivo é criado com cópia direta, sem reescrita por `pandas`.

O checksum do snapshot deve ser igual ao checksum da matriz de entrada.

### 3.2 `alteracoes.csv`

Registra uma linha para cada campo alterado entre a sessão anterior e a
sessão atual.

Colunas:

```text
session_id
previous_session_id
record_id
change_type
field
old_value
new_value
severity
```

No snapshot baseline, o arquivo contém apenas o cabeçalho, pois não
existe sessão anterior para comparação.

### 3.3 `manifesto.json`

Registra:

```text
schema_version
session_id
created_at
reviewer
note
baseline_snapshot
input
previous_snapshot
snapshot
screening_decisions
changes
structure
```

O horário em `created_at` utiliza ISO 8601 em UTC.

## 4. Identificador da sessão

O parâmetro obrigatório:

```text
--session-id
```

aceita apenas:

```text
letras
números
ponto
sublinhado
hífen
```

Exemplos válidos:

```text
baseline_v4_3f
20260805_a1_pilot_01
a1_session-02
v4.5.1
```

Exemplos inválidos:

```text
sessão 01
../session
session/01
session:01
```

Recomenda-se utilizar identificadores cronológicos e descritivos:

```text
YYYYMMDD_ETAPA_SEQUENCIA
```

Exemplo:

```text
20260805_a1_pilot_01
```

O identificador deve permanecer estável depois que o snapshot for
criado.

## 5. Responsável pela sessão

O parâmetro:

```text
--reviewer
```

é obrigatório.

Exemplo:

```bash
--reviewer "Andre Cataldo"
```

O valor representa a pessoa responsável pelo estado da matriz no
momento do snapshot.

Ele não substitui o campo `screened_by` de cada registro. O manifesto
identifica o responsável pela sessão, enquanto `screened_by` identifica
quem realizou a decisão de triagem daquele registro.

## 6. Nota da sessão

O parâmetro opcional:

```text
--note
```

registra uma descrição breve no manifesto.

Exemplo:

```bash
--note "Primeira sessão do piloto A1."
```

A nota pode registrar:

- etapa executada;
- lote analisado;
- objetivo da sessão;
- evento metodológico;
- limitações conhecidas;
- motivo de interrupção;
- relação com uma revisão anterior.

## 7. Snapshot baseline

O primeiro snapshot representa o estado anterior às alterações humanas
da triagem.

Execução de teste:

```bash
python scripts/snapshot_screening_session.py \
  --session-id baseline_v4_3f \
  --reviewer "Andre Cataldo" \
  --note "Baseline anterior ao início da triagem manual." \
  --dry-run
```

Criação:

```bash
python scripts/snapshot_screening_session.py \
  --session-id baseline_v4_3f \
  --reviewer "Andre Cataldo" \
  --note "Baseline anterior ao início da triagem manual."
```

O baseline possui:

```text
baseline_snapshot = true
previous_snapshot = null
changes.total_changes = 0
changes.changed_records = 0
```

Estrutura:

```text
outputs/screening_sessions/baseline_v4_3f/
├── matriz_triagem.csv
├── alteracoes.csv
└── manifesto.json
```

O baseline real da v4.3f registra:

```text
total de registros: 254
Include: 0
Exclude: 0
Uncertain: 0
Pending: 254
```

## 8. Snapshot de uma sessão posterior

Após uma sessão de triagem, indicar explicitamente o snapshot anterior:

```bash
python scripts/snapshot_screening_session.py \
  --session-id 20260805_a1_pilot_01 \
  --reviewer "Andre Cataldo" \
  --previous \
    outputs/screening_sessions/baseline_v4_3f \
  --note "Primeira sessão do piloto de triagem A1."
```

O novo manifesto registrará:

```text
baseline_snapshot = false
previous_snapshot.session_id = baseline_v4_3f
previous_snapshot.directory
previous_snapshot.matrix_sha256
```

A sessão seguinte deve apontar para a anterior:

```bash
python scripts/snapshot_screening_session.py \
  --session-id 20260806_a1_pilot_02 \
  --reviewer "Andre Cataldo" \
  --previous \
    outputs/screening_sessions/20260805_a1_pilot_01 \
  --note "Continuação do piloto de triagem A1."
```

A cadeia operacional será:

```text
baseline_v4_3f
    ↓
20260805_a1_pilot_01
    ↓
20260806_a1_pilot_02
    ↓
snapshot posterior
```

## 9. Simulação antes da escrita

O parâmetro:

```text
--dry-run
```

executa:

- leitura da matriz;
- validação estrutural mínima;
- leitura e validação do snapshot anterior;
- comparação dos registros;
- classificação das alterações;
- cálculo das contagens;
- apresentação do resumo.

Nenhum diretório é criado.

Exemplo:

```bash
python scripts/snapshot_screening_session.py \
  --session-id 20260805_a1_pilot_01 \
  --reviewer "Andre Cataldo" \
  --previous \
    outputs/screening_sessions/baseline_v4_3f \
  --dry-run
```

O modo `--dry-run` também respeita a imutabilidade. Um identificador já
existente continua sendo rejeitado.

## 10. Modelo de comparação

A associação entre as sessões utiliza:

```text
record_id
```

Para cada `record_id` compartilhado, o script compara todas as colunas
presentes nas duas matrizes, exceto o próprio identificador.

A comparação preserva o conteúdo literal das células. Mudanças de
espaçamento, pontuação ou capitalização podem ser registradas como
alterações.

### 10.1 Registro adicionado

Quando um identificador existe apenas na matriz atual:

```text
change_type = record_added
severity = warning
```

### 10.2 Registro removido

Quando um identificador existe apenas na sessão anterior:

```text
change_type = record_removed
severity = warning
```

Uma alteração de `record_id` aparece como uma remoção seguida por uma
adição. O identificador não é tratado como campo editável comum.

### 10.3 Ordem das linhas

Mudanças na ordem dos registros não geram linhas em `alteracoes.csv`.

Elas são registradas no manifesto:

```text
structure.row_order_changed
```

### 10.4 Colunas adicionadas ou removidas

Mudanças de esquema são registradas no manifesto:

```text
structure.columns_added
structure.columns_removed
```

A validação mínima continua exigindo as 22 colunas obrigatórias.

## 11. Classificação das alterações

### 11.1 Decisões

| Situação | `change_type` | Severidade |
|---|---|---|
| decisão vazia recebe valor | `decision_added` | `info` |
| decisão existente é alterada | `decision_changed` | `info` |
| decisão existente é apagada | `decision_cleared` | `warning` |

Uma decisão adicionada pode produzir várias linhas, pois também são
alterados código, justificativa, evidência, responsável e data.

### 11.2 Fundamentação da triagem

| Campo | `change_type` | Severidade |
|---|---|---|
| `screening_reason_code` | `reason_code_changed` | `info` |
| `screening_reason` | `reason_changed` | `info` |
| `screening_evidence` | `evidence_changed` | `info` |
| `screened_by` | `reviewer_changed` | `info` |
| `screening_date` | `screening_date_changed` | `info` |
| `second_review_required` | `review_flag_changed` | `info` |
| `screening_notes` | `notes_changed` | `info` |

### 11.3 Resumos

| Situação | `change_type` | Severidade |
|---|---|---|
| resumo vazio recebe conteúdo | `abstract_recovered` | `info` |
| resumo existente é alterado | `abstract_changed` | `info` |
| resumo existente é removido | `abstract_removed` | `warning` |
| flag de disponibilidade muda | `abstract_availability_changed` | `info` |

A recuperação de um resumo deve continuar sendo documentada em
`screening_notes`, conforme o protocolo da triagem.

### 11.4 Campos bibliográficos

Os campos protegidos são:

```text
source_record_id
title
authors
year
venue
doi
url
```

Alterações nesses campos recebem:

```text
change_type = bibliographic_field_changed
severity = warning
```

O snapshot não bloqueia a alteração. Ele a torna visível para revisão.

Uma mudança bibliográfica somente deve ser mantida quando houver fonte,
justificativa e rastreabilidade.

### 11.5 Prioridades

Alterações em:

```text
suggested_priority
adjudicated_priority
final_priority
```

recebem:

```text
change_type = priority_changed
severity = warning
```

Esses campos representam decisões consolidadas antes da triagem e não
devem ser modificados durante a operação normal.

### 11.6 Grupos de duplicatas

Alterações em:

```text
duplicate_group
```

recebem:

```text
change_type = duplicate_group_changed
severity = warning
```

A resolução de uma duplicata deve ocorrer por decisão de triagem e
justificativa, sem apagar o histórico do grupo.

## 12. Severidades

### `info`

Representa alterações esperadas durante a triagem:

```text
decisão adicionada
evidência revisada
nota adicionada
resumo recuperado
flag de revisão alterada
```

### `warning`

Representa uma alteração que exige verificação:

```text
decisão apagada
resumo removido
campo bibliográfico alterado
prioridade alterada
grupo de duplicata alterado
registro adicionado
registro removido
```

Um `warning` não interrompe automaticamente o snapshot.

Ele deve ser revisado antes que a sessão seja aceita como referência
para a próxima etapa.

## 13. Resumo das alterações no manifesto

O objeto:

```text
changes
```

contém:

```text
total_changes
changed_records
by_type
by_field
by_severity
```

Exemplo:

```json
{
  "total_changes": 8,
  "changed_records": 2,
  "by_type": {
    "decision_added": 1,
    "evidence_changed": 1,
    "reason_changed": 1
  },
  "by_field": {
    "screening_decision": 1,
    "screening_evidence": 1,
    "screening_reason": 1
  },
  "by_severity": {
    "info": 8
  }
}
```

As contagens do exemplo são ilustrativas.

## 14. Contagens de decisão

Cada manifesto registra o estado completo da matriz:

```text
screening_decisions.include
screening_decisions.exclude
screening_decisions.uncertain
screening_decisions.pending
```

Essas contagens permitem acompanhar a evolução entre sessões sem
depender apenas do arquivo de progresso.

O snapshot não substitui:

```text
scripts/screening_progress.py
```

O relatório de progresso apresenta a visão operacional agregada. O
snapshot registra a história entre dois estados.

## 15. Integridade do snapshot anterior

Antes da comparação, o script verifica:

```text
diretório existente
matriz presente
manifesto presente
JSON válido
session_id presente
checksum da matriz presente
checksum da matriz compatível
```

Quando o arquivo anterior foi alterado depois de sua criação:

```text
ERROR: Previous snapshot matrix checksum does not match its manifest.
```

O script atualmente valida o checksum da matriz anterior.

O checksum de `alteracoes.csv` permanece registrado no manifesto, mas
não é utilizado como condição para abrir a sessão anterior.

## 16. Escrita atômica

A sessão é inicialmente criada em um diretório temporário dentro de:

```text
outputs/screening_sessions/
```

Somente depois que os arquivos e checksums são concluídos, o diretório
temporário é renomeado para o identificador definitivo.

Em caso de erro:

- o diretório temporário é removido;
- o diretório final não é criado;
- a matriz de entrada permanece preservada.

## 17. Campos do manifesto

### 17.1 Identificação

```text
schema_version
session_id
created_at
reviewer
note
baseline_snapshot
```

### 17.2 Entrada

```text
input.path
input.sha256
input.rows
```

### 17.3 Sessão anterior

Para sessões posteriores ao baseline:

```text
previous_snapshot.session_id
previous_snapshot.directory
previous_snapshot.matrix_sha256
```

No baseline:

```text
previous_snapshot = null
```

### 17.4 Artefatos gerados

```text
snapshot.matrix.path
snapshot.matrix.rows
snapshot.matrix.sha256

snapshot.changes.path
snapshot.changes.rows
snapshot.changes.sha256
```

### 17.5 Estrutura

```text
structure.row_order_changed
structure.columns_added
structure.columns_removed
```

## 18. Verificação manual de um snapshot

```bash
SESSION_DIR=outputs/screening_sessions/baseline_v4_3f

sha256sum \
  outputs/matriz_triagem_neuro_v4_3f.csv \
  "$SESSION_DIR/matriz_triagem.csv"
```

Para validar o manifesto:

```bash
python - <<'PY'
import hashlib
import json
from pathlib import Path


directory = Path(
    "outputs/screening_sessions/baseline_v4_3f"
)

manifest = json.loads(
    (
        directory / "manifesto.json"
    ).read_text(encoding="utf-8")
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


matrix_path = Path(
    manifest["snapshot"]["matrix"]["path"]
)

changes_path = Path(
    manifest["snapshot"]["changes"]["path"]
)

assert matrix_path.exists()
assert changes_path.exists()

assert (
    manifest["snapshot"]["matrix"]["sha256"]
    == sha256(matrix_path)
)

assert (
    manifest["snapshot"]["changes"]["sha256"]
    == sha256(changes_path)
)

print("Snapshot validado.")
PY
```

## 19. Fluxo após cada sessão de triagem

Sequência recomendada:

```bash
python scripts/validate_screening_matrix.py

python scripts/screening_progress.py

python scripts/snapshot_screening_session.py \
  --session-id SESSION_ID \
  --reviewer "Andre Cataldo" \
  --previous PREVIOUS_SESSION_DIRECTORY \
  --note "Descrição da sessão." \
  --dry-run
```

Depois da revisão da simulação:

```bash
python scripts/snapshot_screening_session.py \
  --session-id SESSION_ID \
  --reviewer "Andre Cataldo" \
  --previous PREVIOUS_SESSION_DIRECTORY \
  --note "Descrição da sessão."
```

Em seguida:

```bash
cat \
  outputs/screening_sessions/SESSION_ID/manifesto.json
```

E:

```bash
python - <<'PY'
import pandas as pd

path = (
    "outputs/screening_sessions/"
    "SESSION_ID/alteracoes.csv"
)

changes = pd.read_csv(
    path,
    dtype=str,
    keep_default_na=False,
)

print(changes["severity"].value_counts())
print()
print(changes["change_type"].value_counts())
PY
```

Substituir `SESSION_ID` e `PREVIOUS_SESSION_DIRECTORY` pelos valores da
sessão real.

## 20. Relação com os demais componentes

```text
validate_screening_matrix.py
    valida a integridade estrutural e metodológica

screening_progress.py
    apresenta o estado agregado da triagem

snapshot_screening_session.py
    registra a evolução entre duas sessões

export_screening_results.py
    separa e consolida os resultados por decisão
```

Fluxo:

```text
editar matriz
    ↓
validar
    ↓
acompanhar progresso
    ↓
simular snapshot
    ↓
revisar alterações e warnings
    ↓
criar snapshot
    ↓
prosseguir para a próxima sessão
```

## 21. Testes automatizados

Executar:

```bash
python -m unittest \
  tests.test_snapshot_screening_session \
  -v
```

Os testes utilizam matrizes sintéticas e diretórios temporários.

A cobertura inclui:

- validação de identificadores;
- validação mínima da matriz;
- criação do baseline;
- modo `--dry-run`;
- decisão adicionada;
- evidência alterada;
- resumo recuperado;
- mudança bibliográfica;
- registros adicionados e removidos;
- alteração da ordem;
- alteração de colunas;
- vínculo com a sessão anterior;
- checksums;
- caminhos registrados no manifesto;
- proteção contra sobrescrita;
- rejeição de snapshot anterior adulterado;
- preservação da matriz de entrada.

Executar a suíte completa:

```bash
python -m unittest discover \
  -s tests \
  -p "test_*.py" \
  -v
```

## 22. Limitações atuais

A implementação atual:

- não descobre automaticamente a última sessão;
- não possui índice global de sessões;
- não assina criptograficamente os manifestos;
- não impede alterações bibliográficas, apenas as sinaliza;
- não verifica o checksum de `alteracoes.csv` ao abrir a sessão anterior;
- não registra um checksum do próprio manifesto;
- não marca uma sessão como aprovada ou rejeitada;
- não possui campo específico para conclusão da segunda revisão;
- não substitui backups externos dos artefatos locais.

Esses pontos podem ser tratados em ciclos posteriores sem alterar o
formato básico dos snapshots existentes.

## 23. Estado inicial

O snapshot baseline da v4.3f foi criado em:

```text
outputs/screening_sessions/baseline_v4_3f/
```

O checksum da matriz de trabalho e do snapshot baseline é:

```text
adff6ac701110eaafc5afb02b97100cc4853cfb5bc4060e0311d6588a7edefab
```

Isso confirma que a matriz foi preservada integralmente no momento do
snapshot.
