# Plan: C++ 빌드 / 실행 / 검증 스크립트

## 목표

`workspace/main.cpp`를 빌드하고 샘플 입출력으로 exact matching 검증 후, 간단한 `summary.md`를 생성한다.

---

## 디렉토리 구조

```
problems/atc/atc-abc436_g/
└── workspace/
    ├── main.cpp                ← 유저가 구현
    ├── testcases/              ← sample 파일 (유저가 직접 추가 가능)
    │   ├── sample_input_1.txt
    │   ├── sample_output_1.txt
    │   ├── sample_input_2.txt
    │   └── sample_output_2.txt
    ├── .solution               ← 바이너리 (git-ignored, 매 빌드마다 덮어씀)
    └── summary.md              ← 결과 (매 실행마다 덮어씀)
```

- `results/` 디렉토리 없음. 출력/에러/diff는 **터미널에만** 표시.
- `summary.md`는 pass/fail 기록만 남기는 최소 파일.

---

## 사용법

```bash
./scripts/run_tests.sh problems/atc/atc-abc436_g
```

---

## 실행 흐름

```
1. Validate
   ├─ 경로/main.cpp 없음 → 에러 메시지, exit 1
   └─ testcases/ 없으면 자동 생성

2. Build
   ├─ g++ -std=c++17 -O2 -o workspace/.solution workspace/main.cpp
   ├─ 성공 → 계속
   └─ 실패 → 컴파일 에러를 터미널에 출력, summary.md에 "Build: FAIL" 기록, exit 1

3. Test (sample_input_*.txt 각각)
   ├─ timeout 5s ./.solution < sample_input_N.txt
   ├─ trailing whitespace 제거 후 diff
   └─ 결과를 터미널 + summary.md에 기록

4. 종료
   └─ 전체 통과 시 exit 0, 하나라도 실패 시 exit 1
```

---

## 터미널 출력 예시

```
[BUILD] OK
[TEST 1] sample_1 ... PASS
[TEST 2] sample_2 ... FAIL
  expected: 7
  got:      6
[TEST 3] sample_3 ... PASS

2/3 passed
```

실패 시 expected/got 첫 줄을 바로 보여준다.
RTE 발생 시: `[TEST 2] sample_2 ... FAIL (exit 139: segfault)` — 별도 상태 없이 FAIL에 사유 표시.
TLE 발생 시: `[TEST 2] sample_2 ... FAIL (timeout 5s)` — 동일하게 FAIL 처리.

---

## summary.md 포맷

```markdown
# Test Summary

Build: PASS

| # | Test Case | Result |
|---|-----------|--------|
| 1 | sample_1  | PASS   |
| 2 | sample_2  | FAIL   |
| 3 | sample_3  | PASS   |

2/3 passed
```

- 상태는 **PASS / FAIL** 두 가지만.
- 타이밍, 에러 상세, diff는 summary에 넣지 않음 (터미널에서 확인).

---

## 멱등성 (Idempotent)

스크립트를 몇 번이든 다시 실행해도 동일한 결과:

| 대상 | 동작 |
|------|------|
| `.solution` 바이너리 | 매번 덮어씀 |
| `summary.md` | 매번 새로 씀 (append 아님) |
| `testcases/` | 읽기만 함, 절대 수정하지 않음 |
| 터미널 출력 | 매번 동일 |

**부수효과 없음**: testcases 파일을 건드리지 않으므로 유저 데이터 손실 위험 없음.

---

## 유저가 테스트케이스를 추가하는 방법

```bash
# 직접 파일 생성
vi workspace/testcases/sample_input_3.txt
vi workspace/testcases/sample_output_3.txt
```

번호만 맞추면 스크립트가 자동 인식. `sample_output_N.txt`가 없는 input은 무시한다.

---

## .gitignore 추가 항목

```
.solution
```

---

## 구현 작업

| # | 작업 |
|---|------|
| 1 | `scripts/run_tests.sh` 작성 (~40-50줄) |
| 2 | `.gitignore`에 `.solution` 추가 |
| 3 | (이후) problem-intake 스킬에서 `testcases/` 자동 생성 연동 |
