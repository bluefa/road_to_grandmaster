# Plan: VSCode에서 현재 문제 바로 빌드·테스트

## 목표

`workspace/main.cpp`를 편집하다가 키 하나로 해당 문제의 빌드 + 샘플 테스트를 돌리고, 결과(PASS/FAIL, 컴파일 에러, 실제 출력, diff)를 VSCode 안에서 즉시 볼 수 있게 한다.

**한 줄 요약**: `.vscode/tasks.json`을 리포에 커밋하고, 사용자 개인 `keybindings.json`에 단축키 한 줄을 추가한다. 별도 확장은 설치하지 않는다.

---

## 현재 상태

- `scripts/run_tests.sh <problem-dir>`가 이미 전부 해줌:
  - g++ 빌드 → 샘플 실행 → 터미널에 PASS/FAIL(colored) → `workspace/summary.md` → 실패 케이스는 `workspace/.debug/`에 input/my_output/diff 덤프
  - 인자로 `problems/<plat>/<slug>` 또는 `.../workspace` 둘 다 수용
  - exit 0 (전부 통과) / 1 (빌드 실패 또는 테스트 실패) / 2 (사용법 오류)
- VSCode 설정 없음 (`.vscode/` 디렉터리 부재)

즉 **스크립트는 이미 충분하고, VSCode 측 배선만 하면 된다.**

---

## 설계 결정

| 결정 | 선택 | 이유 |
|------|------|------|
| 실행 매커니즘 | VSCode Task (`tasks.json`) | 기본 내장. 확장 불필요. 키바인딩, Problems 패널, 터미널 연동 모두 무료. |
| "현재 문제"를 어떻게 알 것인가 | `${fileDirname}`을 그대로 run_tests.sh에 전달 | run_tests.sh가 workspace 또는 problem 디렉터리 둘 다 받으므로 파일이 `workspace/main.cpp`든 `statement.md`든 `problem.yaml`이든 다 동작 |
| 결과 표시 | 터미널(주) + Problems 패널(컴파일 에러만) + summary.md(온디맨드) | 이미 컬러 출력/diff가 터미널에 다 찍힘. 파일 열어야 하는 건 fail debug 뿐 |
| tasks.json 위치 | 리포 커밋 (`/.vscode/tasks.json`) | 이 리포 전용 워크플로우라서 개인 workspace 설정이 아닌 리포 설정이 맞음 |
| 키바인딩 위치 | 개인 `~/Library/Application Support/Code/User/keybindings.json` | VSCode는 프로젝트 단위 키바인딩을 지원하지 않음. README에 1회 추가 가이드만 기술 |
| Auto-run-on-save | **하지 않음** | PS 워크플로우는 명시적 실행 선호. 저장마다 빌드 돌면 집중 깨짐 |

---

## 정의할 Tasks (`.vscode/tasks.json`)

### 1. `Test: current problem` (주력)

- **Command**: `${workspaceFolder}/scripts/run_tests.sh ${fileDirname}`
- **Group**: `test`, `isDefault: true`
- **presentation**: dedicated 터미널, 매 실행마다 clear, reveal always
- **problemMatcher**: `$gcc` — 컴파일 에러가 Problems 패널에 찍히고 줄번호 클릭으로 점프
- 기대 동작: main.cpp 어느 파일이든 열린 채로 이 태스크 실행 → 올바른 문제의 run_tests.sh 호출

### 2. `Build: current problem (no tests)` (부차)

- **Command**: `g++ -std=c++17 -O2 -Wall -o ${fileDirname}/.solution ${fileDirname}/main.cpp` (주의: `${fileDirname}`이 workspace 아닐 때 실패 — Test 태스크 쪽이 더 견고)
- **Group**: `build`, `isDefault: true` → `cmd+shift+b`로 즉시 호출
- 용도: 샘플 없이 컴파일만 빨리 돌리고 싶을 때. 실전에선 쓸 일 적지만 관용적으로 제공

### 3. `Open: test summary` (보조)

- **Command**: `code ${fileDirname}/summary.md`
- 팔레트 호출 전용 (기본 키 없음). `Test: current problem` 실행 후 터미널 말고 정리된 표로 보고 싶을 때.

### 4. (선택) `Refresh CF cache`

- **Command**: `${workspaceFolder}/scripts/refresh_codeforces_problems.py`
- 리포 규모 워크플로우에 어울리는 "one-click" 보조. 필수 아님.

---

## 키바인딩

VSCode는 프로젝트 keybindings.json이 없음. 사용자가 본인 `keybindings.json`에 아래 한 줄을 추가:

```jsonc
// ~/Library/Application Support/Code/User/keybindings.json
{ "key": "cmd+shift+t",
  "command": "workbench.action.tasks.runTask",
  "args": "Test: current problem" }
```

대안 (자연스러운 매핑):
- `cmd+shift+b` (기본): Build 태스크 → `.solution`만 컴파일 (tasks.json에서 `isDefault` 설정)
- `cmd+shift+p` → "Run Test Task" 팔레트 경로 (키바인딩 등록 없이도 사용 가능)

**커밋하지 않는다** — 리포에 넣을 수 없고, 개인 설정 영역.

---

## 결과 보기 경로

| 보고 싶은 것 | 어디서 보나 |
|--------------|-------------|
| 전체 PASS/FAIL 요약, 실행 로그 | VSCode 터미널 패널 (dedicated, 자동 포커스 없음) |
| 컴파일 에러 + 줄번호 클릭 점프 | Problems 패널 (`$gcc` matcher 자동 연동) |
| 테스트 실패 시 실제 출력 / 기대 출력 / diff | Explorer에서 `workspace/.debug/` 열기 |
| 정리된 PASS/FAIL 표 | `workspace/summary.md` (태스크 3로 열기) |
| 샘플 입력 / 기대 출력 원본 | Explorer에서 `workspace/testcases/` |

**핵심**: run_tests.sh가 이미 이 5가지를 전부 만들어 놓았음. VSCode 쪽은 그냥 연결만 해주면 됨.

---

## 엣지 케이스

| 상황 | 동작 |
|------|------|
| `main.cpp` 아닌 파일(`notes.md`, `statement.md`, `problem.yaml`) 편집 중 실행 | `${fileDirname}`가 workspace 또는 problem root — run_tests.sh가 양쪽 다 수용. 정상 동작 |
| 문제 디렉터리 밖(`docs/`, 루트 `plan-*.md`) 편집 중 실행 | run_tests.sh가 "main.cpp not found" 에러 + exit 2. VSCode는 터미널에 빨간 메시지 표시 |
| 파일이 열려있지 않음 | `${fileDirname}` 치환 실패 → 태스크 실행 불가. VSCode가 알림으로 고지 |
| `workspace/testcases/`에 샘플 0개 | run_tests.sh가 WARN 찍고 summary.md에 "No test cases found" 기록, exit 0 |
| AtCoder 문제에 사용자가 커스텀 테스트케이스 추가 | 기존 파일명 규칙(`sample_input_N.txt` / `sample_output_N.txt`) 그대로 따르면 자동 인식 |

---

## 구현 단계

| # | 작업 | 비고 |
|---|------|------|
| 1 | `/.vscode/tasks.json` 작성 (Task 1~3) | Task 4(CF refresh)는 선택 |
| 2 | `docs/daily-workflow.md` 또는 README에 "VSCode에서 빠르게 테스트" 절 추가 — 단축키 등록 스니펫 포함 | 사용자 환경 설정 가이드 |
| 3 | `/.vscode/settings.json`에 최소 권장 설정 — 예: `files.associations`, `C_Cpp.default.cppStandard: c++17` | 선택. 없어도 동작함 |
| 4 | 실제 환경에서 각 Task를 손으로 실행하여 단축키·매처·출력 확인 | 검증 |

각 단계 독립. 1만 해도 최소 기능 성립.

---

## 검증 계획

최소 테스트 (손으로):
- [ ] `main.cpp`를 연 상태에서 `cmd+shift+b` → `.solution` 빌드되고 Problems 패널에 에러 없음
- [ ] `cmd+shift+t`(또는 팔레트 `Tasks: Run Test Task`) → 터미널에 컬러 PASS/FAIL 출력, summary.md 갱신
- [ ] main.cpp에 의도적 컴파일 에러 삽입 → Problems 패널에 라인 번호 달린 에러 항목, 클릭 시 그 줄로 점프
- [ ] `notes.md` / `statement.md` / `problem.yaml` 각각 편집 중에 Test Task 실행 → 동일 문제의 run_tests.sh가 돌아감
- [ ] 문제 디렉터리 밖(`docs/conventions.md`) 편집 중 실행 → 명확한 에러 메시지, VSCode가 빨간 알림
- [ ] 샘플 실패 1건 발생 시 `workspace/.debug/diff_N.txt` 생성되어 Explorer에서 열림

회귀:
- [ ] 기존 `scripts/run_tests.sh` 단독 호출(`./scripts/run_tests.sh problems/atc/...`) 이전과 동일 동작
- [ ] 기존 문제 디렉터리 구조 미변경

---

## 스코프 밖 (이번엔 안 함)

- **launch.json / lldb 디버깅** — "샘플 입력을 stdin으로 넣고 중단점 잡기" 수요는 있으나 별도 플랜. 현재 task 기반 실행만으로 컴파일·런타임·WA 원인 추적은 충분
- **Auto-run-on-save** — 사용자 집중 해침. 필요 시 `Run On Save` 확장을 개인 설정으로 추가 가능
- **스트레스 테스트 태스크** (brute/gen 대비) — cp-training-system 로드맵에 있으나 아직 스크립트 자체가 없음. 스크립트 선행 필요
- **문제 인테이크(init_problem.py)용 태스크** — URL 입력 받아야 해서 task UX가 어색함. 터미널 호출이 더 자연스러움
- **다중 커서/스플릿 뷰 자동 배치** — Explorer로 열기만 해도 충분
- **사용자 키바인딩 파일 자동 생성** — VSCode 정책상 불가능/비권장

---

## 성공 기준

1. `main.cpp` 편집 → 한 단축키 → 5초 안에 터미널에서 PASS/FAIL 확인
2. 컴파일 에러가 Problems 패널에서 한 번에 점프 가능
3. FAIL 발생 시 debug 파일이 Explorer에서 즉시 열림
4. 추가 확장 설치 0개, 의존 도구 0개 (VSCode + run_tests.sh만)
