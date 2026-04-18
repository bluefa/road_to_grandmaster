# Plan: 풀이 제출 자동화 (AtCoder / Codeforces)

## 목표

현재 열려 있는 `workspace/main.cpp`를 한 단축키로 해당 문제에 제출하고, verdict(AC/WA/TLE/…)를 VSCode 안에서 즉시 확인한다.

**핵심 결정 포인트 (이 계획의 근거)**
- 제출은 **인증·폼·verdict 폴링**이 얽힌 고위험 작업이라 직접 스크래핑보다 검증된 라이브러리를 래핑하는 쪽이 유지보수 측면에서 압도적으로 유리
- 1순위 권장: `oj` (online-judge-tools) CLI 래핑 — CF/AtCoder 양쪽 battle-tested
- 2순위(비상): `oj` 설치 불가 시 직접 구현 — **비권장**, 이 계획에서는 스펙 명시까지만 하고 구현은 스코프 밖

---

## 1. 제출에 필요한 항목 — 공통

| 항목 | 설명 |
|------|------|
| 인증된 세션 | 쿠키 + CSRF 토큰이 살아있는 상태 |
| 문제 식별자 | URL에서 파싱 가능 (`problem.yaml`에 이미 저장됨) |
| 소스 파일 | `workspace/main.cpp` |
| 언어 ID | 플랫폼별 정수 ID (C++17/C++20 등을 숫자로 지정) |
| verdict 조회 경로 | 제출 직후 ~30초 내 결과 반영, 폴링 필요 |

---

## 2. Codeforces 제출 스펙

### 2.1 인증

- 방식: **handle + password** 웹 로그인 (`/enter`)
- 2FA 없음
- Cloudflare 챌린지: 문제 페이지와 동일하게 urllib 그대로는 막힘 → curl/브라우저 레벨 헤더 필요
- 세션 쿠키: `JSESSIONID`, 만료까지 주 단위 지속 (oj가 `~/.config/online-judge-tools/cookie.jar`로 자동 관리)

### 2.2 제출 폼 (`/problemset/submit`)

| 필드 | 값 | 비고 |
|------|----|----|
| `csrf_token` | 해당 페이지 HTML에서 스크랩 | 세션마다 재발급됨 |
| `action` | `submitSolutionFormSubmitted` | 고정 |
| `submittedProblemCode` | 예: `1168C` | `contest_id + index` |
| `programTypeId` | 정수 언어 ID | 아래 표 |
| `source` | `main.cpp` 내용 | 최대 65536 바이트 |
| `ftaa`, `bfaa` | 브라우저 핑거프린트 토큰 | JavaScript로 생성됨 — oj가 내부적으로 처리 |

### 2.3 주요 언어 ID (CF)

```
50  = GNU G++14        (C++14)
54  = GNU G++17        (C++17, 대부분의 PS 유저)
89  = GNU G++17 (64)   (윈도우 64비트 빌드, 가끔 TLE 회피용)
73  = GNU G++20        (C++20)
91  = GNU G++23        (C++23 최신)
```

기본값으로 **89 (G++17 64)**  또는 **73 (G++20)** 권장. `problem.yaml`의 `workflow.language: cpp17`에서 유추.

### 2.4 Verdict 조회

- 공식 API: `https://codeforces.com/api/user.status?handle=<handle>&from=1&count=1`
- 응답의 `submissions[0].verdict` 필드: `OK`, `WRONG_ANSWER`, `TIME_LIMIT_EXCEEDED`, `MEMORY_LIMIT_EXCEEDED`, `RUNTIME_ERROR`, `COMPILATION_ERROR`, `TESTING`, `SKIPPED`, `PRESENTATION_ERROR`
- 평균 대기 10-30초, 1-2초 간격으로 폴링

### 2.5 Rate Limit

- 같은 문제 재제출은 **10초 간격** 강제
- 너무 자주 폴링하면 `CALL_LIMIT_EXCEEDED` — 2초 이상 간격 권장

---

## 3. AtCoder 제출 스펙

### 3.1 인증

- 방식: **username + password** 웹 로그인 (`/login`)
- 2FA 없음
- Cloudflare 없음 (상대적으로 덜 까다로움)
- 세션 쿠키: `REVEL_SESSION`, 수 주 지속

### 3.2 제출 폼 (`/contests/<contest>/submit`)

| 필드 | 값 | 비고 |
|------|----|----|
| `csrf_token` | 제출 페이지 HTML `<meta name="csrf-token">`에서 스크랩 | |
| `data.TaskScreenName` | 예: `abc436_g` | `problem.yaml.problem.problem_id` 그대로 |
| `data.LanguageId` | 정수 언어 ID | 아래 표 |
| `sourceCode` | `main.cpp` 내용 | 최대 512 KB |

### 3.3 주요 언어 ID (AtCoder 2023+ 기준)

```
5001 = C++ 17 (gcc 12.2)
5028 = C++ 20 (gcc 12.2)    ← 일반적 기본값
5029 = C++ 23 (gcc 12.2)
```

**주의**: AtCoder는 **콘테스트마다 언어 테이블이 고정**됨. 진행 중인 콘테스트 시점에 사용 가능하던 ID만 유효. 오래된 콘테스트 문제에 최신 ID로 제출하면 거부당할 수 있음 — 문제 페이지에서 허용 언어 목록 확인 필요.

### 3.4 Verdict 조회

- 페이지: `/contests/<contest>/submissions/me` 스크랩
- 내부 테이블의 `<td>` 상태 문자열: `AC`, `WA`, `TLE`, `MLE`, `RE`, `CE`, `QLE`, `OLE`, `IE`, `WJ`(채점 중), `X/Y`(진행률)
- 또는 WebSocket `/contests/<contest>/submissions/me`로 푸시 수신 (oj는 이쪽 사용)
- 평균 5-20초

### 3.5 Rate Limit

- 공식 수치 없음. 관례상 **5초 이상 간격** 권장
- 진행 중 콘테스트에선 서버 부하로 verdict 지연 가능

---

## 4. 구현 방식 — oj 래핑 vs 직접 구현

### 4.1 oj 래핑 (권장)

**장점**
- CSRF / ftaa / bfaa / Cloudflare / WebSocket / 쿠키 만료 — 모두 처리됨
- 유지보수 제로 (사이트 개편 시 oj 업데이트만 받으면 됨)
- `oj login` 한 번이면 쿠키가 `~/.config/online-judge-tools/cookie.jar`에 저장되어 수 주간 재로그인 불필요
- `--wait`로 verdict까지 대기하는 모드 내장

**단점**
- `pip install online-judge-tools` 의존성 추가 (하지만 CLI 툴 하나, 프로젝트 코드엔 영향 없음)
- verdict 출력 포맷을 우리 스크립트에서 파싱해야 함

**사용 예**
```bash
oj login https://codeforces.com/    # 1회 (handle/password 입력)
oj login https://atcoder.jp/        # 1회

oj submit -w --yes \
  --language 89 \
  https://codeforces.com/contest/1168/problem/C \
  workspace/main.cpp
```

### 4.2 직접 구현 (비권장, 참고용)

문제 스크래퍼를 직접 쓴 선례(`init_problem.py`)가 있으나 **제출은 난이도가 한 차원 높음**:

- **쿠키 저장**: macOS Keychain 또는 `.netrc` 필요 (평문 저장은 지양)
- **Cloudflare**: curl 폴백으로 page 가져오기 → 쿠키는 자동 저장되지 않음. requests+cookie jar 수동 구현 필요
- **CSRF 로테이션**: 로그인·제출·재제출마다 새 토큰
- **ftaa/bfaa**: 브라우저 핑거프린트 JS를 에뮬레이트해야 함 (이 부분이 가장 fragile)
- **verdict 폴링**: CF API는 공식이라 안정, AtCoder는 HTML 파싱 or WebSocket
- **로그인 실패 리트라이, 비밀번호 재입력 UX** 등

대략 **700+ LOC** 예상, oj 래퍼는 **~150 LOC**. 투자 대비 이득 없음.

**결론: oj 래핑으로 진행. 대안 경로는 이 섹션에서 명시만 하고 구현하지 않음.**

---

## 5. 자격 증명(credentials) 저장 전략

oj가 쿠키를 자동 관리하므로 **리포에는 비밀정보 절대 저장하지 않는다**.

| 항목 | 위치 | 우리 코드와의 관계 |
|------|------|---------------------|
| CF/AtCoder 쿠키 | `~/.config/online-judge-tools/cookie.jar` | 직접 읽지 않음, oj가 관리 |
| handle/password | 사용자가 `oj login` 인터랙티브 입력 | 우리 코드는 절대 접근 안 함 |
| 쿠키 만료 감지 | `oj submit` 실행 시 oj가 자동 감지·에러 출력 | 에러 메시지를 사용자에게 전달만 함 |

`.gitignore` 확인 필요한 파일 없음 (oj 경로는 리포 밖).

---

## 6. 구성 요소 설계

### 6.1 `scripts/submit.py` (신규)

입력:
- 인자 1: 문제 디렉터리 또는 workspace 디렉터리 (`run_tests.sh`와 동일 컨벤션)
- 플래그: `--language <id>`, `--yes`(확인 스킵), `--no-wait`, `--dry-run`

동작:
1. `problem.yaml`에서 `url`, `platform` 읽음
2. 기본 언어 ID 결정:
   - `problem.yaml.workflow.language` → 플랫폼별 기본 ID 매핑 테이블 조회
   - `--language` 플래그로 오버라이드 가능
3. **사전 안전장치**:
   - `workspace/main.cpp`가 존재하는가
   - 마지막으로 `run_tests.sh`를 실행했을 때 결과는 PASS였는가? (`summary.md` 확인 — 선택적, 실패 시 경고만)
   - rate limit: 같은 문제에 대한 마지막 제출이 10초(CF)/5초(AtCoder) 이내인가? (`.last_submit` 파일)
4. `oj submit -w --yes --language <id> <url> workspace/main.cpp` 호출
5. 종료 코드 / verdict 파싱 후 표준 포맷으로 출력:
   ```
   [SUBMIT] cf 1168C language=89 (G++17 64)
   [SUBMIT] waiting for verdict...
   [VERDICT] WRONG_ANSWER on test 5
   [SUBMIT] id=123456789  url=https://codeforces.com/contest/1168/submission/123456789
   ```
6. `attempts/{attempt_id}/` 아래 submission 메타 기록 (submission_id, verdict, timestamp) — 선택적, 이후 `build_review.py`와 연동

### 6.2 `.vscode/tasks.json`에 태스크 추가

```jsonc
{
  "label": "Submit: current problem",
  "type": "shell",
  "command": "${workspaceFolder}/scripts/submit.py",
  "args": ["${fileDirname}"],
  "group": "none",
  "presentation": {
    "reveal": "always",
    "panel": "dedicated",
    "clear": true,
    "focus": true
  },
  "problemMatcher": []
}
```

Focus를 true로 설정 — 제출 확인 프롬프트에 키 입력이 필요하므로 터미널에 포커스가 가야 함.

### 6.3 키바인딩 (개인 `keybindings.json`)

`Cmd+R`은 이미 Test에 사용 중. 제출은 더 파괴적이므로 **실수 방지 차원에서 chord** 권장:

```jsonc
{ "key": "cmd+r cmd+s",
  "command": "workbench.action.tasks.runTask",
  "args": "Submit: current problem" }
```

`Cmd+R` 누르고 잠깐 뒤 `Cmd+S` — 의도적이어야 발동됨.

---

## 7. 안전장치 (제출은 되돌릴 수 없음)

| 장치 | 동작 |
|------|------|
| **확인 프롬프트** | `--yes` 없으면 `submit.py`가 "Submit <slug> to <platform>? [y/N]" 대기 |
| **rate-limit 가드** | 마지막 제출 시각을 `workspace/.last_submit`에 기록, 최소 간격 미달 시 거부 |
| **pre-flight test** | `--require-local-pass` 플래그: 직전 `summary.md`가 "전부 PASS" 아니면 거부 |
| **dry-run** | `--dry-run`: 실제 제출 안 하고 어떤 URL·언어 ID로 보낼지만 출력 |
| **언어 고정** | `problem.yaml.workflow.language`에서 결정된 언어를 명시 표시. 실수 방지 |
| **세션 만료 감지** | oj가 로그인 만료 시 에러 — 그대로 상위로 전달, 사용자가 `oj login` 재실행 |
| **소스 길이 체크** | CF 65536 바이트, AtCoder 512 KB 초과 여부 사전 검사 |
| **VSCode 태스크 focus** | 자동 실행 방지, 사용자가 프롬프트에 답하도록 포커스 전환 |

---

## 8. VSCode 통합 요약

| 액션 | 키바인딩 | 동작 |
|------|----------|------|
| 로컬 샘플 테스트 | `Cmd+R` (이미 있음) | `run_tests.sh` |
| **제출** | `Cmd+R Cmd+S` (제안, 개인 키바인딩) | `submit.py` → oj 호출 → verdict 표시 |
| 제출 내역 조회(브라우저) | 팔레트에서 `Open submission URL` 태스크 수동 호출 | `open <url>` (macOS) |

결과는 모두 **터미널 패널**에서 확인 (팝업 없음, run_tests와 동일).

---

## 9. 구현 단계

| # | 작업 | 검증 |
|---|------|------|
| 1 | `oj` 설치 가이드 문서화 (`docs/submission-setup.md`) + `oj login` 절차 | 사용자 handle로 로그인 성공 |
| 2 | 언어 ID 매핑 테이블 작성 (`data/language_ids.json`) — CF/AtCoder 각각 | 잘못된 키 조회 시 명확한 에러 |
| 3 | `scripts/submit.py` 작성 — dry-run 모드부터 | `--dry-run`으로 올바른 oj 커맨드가 구성되는가 |
| 4 | 안전장치 구현 (확인 프롬프트, rate-limit, 소스 길이) | 각 가드 단위로 수동 트리거 |
| 5 | 실제 제출 E2E — AtCoder 쉬운 문제 1건 (이미 풀이 있는 것으로) | AC verdict 수신, attempts/ 기록 |
| 6 | CF 동일 E2E | 동일 |
| 7 | `.vscode/tasks.json`에 Submit 태스크 추가 | VSCode에서 실행, verdict 확인 |
| 8 | 개인 키바인딩 가이드 문서화 | |

각 단계 독립적으로 커밋 가능. 5·6은 실제 계정 사용이라 사용자 수동 확인 필요.

---

## 10. 스코프 밖 (이번엔 안 함)

- **브라우저 자동 open** — verdict URL을 `open` 하는 기능은 nice-to-have. 필요하면 `submit.py`에 `--open` 플래그로 추후 추가
- **다중 언어 프로파일** — Python, Rust 등. 현재 `workflow.language: cpp17` 고정이므로 불필요
- **제출 후 에디토리얼/랭커 자동 수집** — 별도 `reference-collector` 스킬 영역
- **재제출 diff (resubmit with changes)** — `--force` 플래그로 rate-limit 우회는 넣지 않음, 의도적으로 번거롭게 유지
- **CF Gym 제출** — Gym은 다른 엔드포인트. 스코프 밖
- **AtCoder 진행 중 콘테스트 제출** — 작동은 하지만 테스트 시나리오에 넣지 않음 (실수 위험)
- **oj 없이 직접 구현** — 섹션 4.2 참조. 스펙만 명시, 코드 안 씀

---

## 11. 의존성

- Python 3.10+
- `online-judge-tools` (`pip install online-judge-tools`) — CLI `oj`
- macOS 기준, `curl` 사전 설치 (이미 있음)

---

## 12. 오픈 질문 (사용자 결정 필요)

1. **언어 기본값** — C++17(89) vs C++20(73/5028) 중 어느 쪽을 `workflow.language: cpp17` → 실제 ID로 매핑하는 기본값으로 할지? (현재 main.cpp 템플릿은 `std=c++17`로 컴파일되지만 `<ranges>` 사용으로 실제론 C++20 필요)
2. **pre-flight test 강제 여부** — `summary.md`에 FAIL이 있으면 제출 거부할지, 경고만 할지? (실전에서는 실패한 채로 일부러 제출하는 경우도 있음 — 디버깅 목적)
3. **쿠키 만료 시 동작** — 에러 후 그냥 종료할지, 인터랙티브하게 `oj login`을 스크립트에서 재호출할지?
4. **attempts 디렉터리 기록 깊이** — submission_id/verdict만 저장할지, 소스 스냅샷도 같이 복사할지?

---

## 성공 기준

1. VSCode에서 `main.cpp` 편집 후 한 키 조합(`Cmd+R Cmd+S`)으로 제출 → 터미널에 verdict까지 30초 이내 표시
2. 인증 상태는 `oj login` 한 번으로 수 주 유지, 매번 비밀번호 입력 없음
3. `--dry-run`이 실제 제출 없이 URL/언어 ID를 정확히 출력
4. rate-limit 가드가 10초(CF)/5초(AtCoder) 이내 재제출을 거부
5. CF/AtCoder 각 1문제씩 실제 제출 성공, verdict 로깅 확인
