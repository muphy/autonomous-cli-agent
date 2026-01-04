# Architecture

Autonomous CLI Agent의 아키텍처와 작동 방식을 설명합니다.

## 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.py                                  │
│                    (Entry Point)                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        agent.py                                 │
│                  (Agent Loop Manager)                           │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │  Session 1    │───▶│  Session 2    │───▶│  Session N    │   │
│  │ (Initializer) │    │   (Coding)    │    │   (Coding)    │   │
│  └───────────────┘    └───────────────┘    └───────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       client.py                                 │
│                  (Claude CLI Client)                            │
│                                                                 │
│    subprocess ──▶ claude -p "prompt" --output-format stream-json│
└─────────────────────────────────────────────────────────────────┘
```

## 핵심 컴포넌트

### 1. main.py (Entry Point)

프로그램 진입점으로 CLI 인자를 파싱하고 에이전트 루프를 시작합니다.

```python
python main.py --project-dir ./my_project --model sonnet --max-iterations 10
```

**주요 역할:**
- CLI 인자 파싱 (`--project-dir`, `--model`, `--max-iterations`)
- Claude CLI 설치 확인
- `agent.run_autonomous_agent()` 호출

### 2. agent.py (Agent Loop Manager)

세션 간 전환과 에이전트 루프를 관리합니다.

**주요 함수:**
- `run_autonomous_agent()`: 메인 루프, 세션 반복 실행
- `run_agent_session()`: 단일 세션 실행 및 응답 처리

### 3. client.py (Claude CLI Client)

Claude CLI를 subprocess로 실행하고 JSON 스트림을 파싱합니다.

**주요 함수:**
- `run_claude_cli()`: subprocess 실행 및 스트리밍
- `ClaudeCLIClient`: SDK 스타일 인터페이스 제공
- `create_cli_client()`: 클라이언트 팩토리 함수

---

## Two-Agent Pattern

이 시스템은 **Two-Agent Pattern**을 사용합니다. 각 에이전트는 독립적인 컨텍스트 윈도우에서 실행되며, 파일 시스템을 통해 상태를 공유합니다.

### Agent 1: Initializer Agent (첫 번째 세션)

프로젝트 초기화를 담당합니다.

```
┌─────────────────────────────────────────────────────────┐
│                  INITIALIZER AGENT                       │
│                                                         │
│  Input:  app_spec.txt (프로젝트 명세)                    │
│                                                         │
│  Tasks:                                                 │
│  1. app_spec.txt 읽기                                   │
│  2. feature_list.json 생성 (200개 테스트 케이스)         │
│  3. init.sh 생성 (환경 설정 스크립트)                    │
│  4. Git 초기화 및 첫 커밋                                │
│  5. 프로젝트 구조 생성                                   │
│                                                         │
│  Output: feature_list.json, init.sh, README.md          │
└─────────────────────────────────────────────────────────┘
```

### Agent 2-N: Coding Agent (후속 세션들)

실제 구현을 담당합니다. 각 세션은 **새로운 컨텍스트**로 시작합니다.

```
┌─────────────────────────────────────────────────────────┐
│                    CODING AGENT                          │
│                                                         │
│  Input:  feature_list.json, claude-progress.txt         │
│                                                         │
│  Steps:                                                 │
│  1. 현재 상태 파악 (ls, git log, feature_list.json)      │
│  2. 서버 시작 (init.sh)                                 │
│  3. 기존 기능 검증 테스트                                │
│  4. 다음 feature 선택 (passes: false)                   │
│  5. 구현 및 테스트                                       │
│  6. feature_list.json 업데이트 (passes: true)           │
│  7. Git 커밋                                            │
│  8. claude-progress.txt 업데이트                        │
│                                                         │
│  Output: 구현된 코드, 업데이트된 feature_list.json       │
└─────────────────────────────────────────────────────────┘
```

---

## 에이전트 간 통신

에이전트들은 **파일 시스템**을 통해 비동기적으로 통신합니다.

### 공유 상태 파일

| 파일 | 용도 | 작성자 | 읽는 자 |
|------|------|--------|---------|
| `feature_list.json` | 테스트 케이스 및 진행 상태 | Initializer → Coding | 모든 Coding Agent |
| `claude-progress.txt` | 세션 간 진행 노트 | 모든 Agent | 다음 Agent |
| `app_spec.txt` | 프로젝트 명세 (읽기 전용) | 사용자 | 모든 Agent |
| Git history | 코드 변경 이력 | 모든 Agent | 다음 Agent |

### feature_list.json 구조

```json
[
  {
    "category": "functional",
    "description": "사용자 로그인 기능",
    "steps": [
      "Step 1: 로그인 페이지 이동",
      "Step 2: 이메일/비밀번호 입력",
      "Step 3: 로그인 버튼 클릭",
      "Step 4: 대시보드 리다이렉트 확인"
    ],
    "passes": false  // ← Coding Agent가 true로 변경
  }
]
```

### 통신 규칙

1. **feature_list.json 수정 규칙**
   - `passes` 필드만 수정 가능 (`false` → `true`)
   - 테스트 삭제/수정 금지
   - 새 테스트 추가 금지

2. **claude-progress.txt 형식**
   ```
   === Session 5 (2024-01-05) ===
   Completed:
   - Feature #23: User authentication
   - Feature #24: Session management

   Issues found:
   - Login button styling needs fix

   Next session should:
   - Fix login button CSS
   - Implement Feature #25: Dashboard

   Progress: 24/200 tests passing (12%)
   ```

---

## 실행 흐름

```
┌──────────────┐
│   START      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  feature_list.json 존재 여부 확인     │
└──────────────────┬───────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼ (없음)              ▼ (있음)
┌───────────────┐      ┌───────────────┐
│  INITIALIZER  │      │    CODING     │
│    AGENT      │      │    AGENT      │
└───────┬───────┘      └───────┬───────┘
        │                      │
        ▼                      ▼
┌──────────────────────────────────────┐
│         세션 완료                     │
│   - Git 커밋                          │
│   - progress.txt 업데이트             │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│      max_iterations 확인             │
└──────────────────┬───────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼ (계속)              ▼ (종료)
┌───────────────┐      ┌───────────────┐
│  다음 세션    │      │     END       │
│  (3초 대기)   │      │               │
└───────────────┘      └───────────────┘
```

---

## Claude CLI 통신

### 명령어 구조

```bash
claude -p "프롬프트" \
  --output-format stream-json \
  --verbose \
  --allowed-tools "Read,Write,Edit,Bash,Glob,Grep" \
  --permission-mode bypassPermissions \
  --model sonnet
```

### JSON 스트림 형식

```json
{"type": "system", "subtype": "init", "session_id": "abc123..."}
{"type": "assistant", "message": {"content": [{"type": "text", "text": "분석 시작..."}]}}
{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {...}}]}}
{"type": "user", "message": {"content": [{"type": "tool_result", "content": "..."}]}}
{"type": "result", "result": "완료되었습니다."}
```

### 메시지 타입

| Type | Subtype | 설명 |
|------|---------|------|
| `system` | `init` | 세션 시작, session_id 포함 |
| `assistant` | - | Claude의 응답 (텍스트 또는 도구 사용) |
| `user` | - | 도구 실행 결과 |
| `result` | - | 최종 응답 |
| `error` | - | 오류 발생 |

---

## 세션 관리

### 세션 라이프사이클

```
1. 세션 시작
   └── Claude CLI subprocess 생성

2. 프롬프트 전송
   └── Initializer 또는 Coding 프롬프트

3. 응답 스트리밍
   └── JSON 라인별 파싱
   └── 도구 사용 로깅
   └── 텍스트 출력

4. 세션 종료
   └── subprocess 완료 대기
   └── 에러 체크

5. 다음 세션 준비
   └── 3초 대기
   └── 새 클라이언트 생성 (fresh context)
```

### 컨텍스트 윈도우 관리

각 세션은 **독립적인 컨텍스트 윈도우**를 가집니다:
- 이전 세션의 대화 기록 없음
- 파일 시스템을 통해서만 상태 공유
- 매 세션 시작 시 `Get Your Bearings` 단계 필수

---

## 확장 가능성

### 커스텀 프롬프트

`prompts/` 폴더의 마크다운 파일을 수정하여 에이전트 동작 커스터마이징:
- `initializer_prompt.md`: 초기화 에이전트 지침
- `coding_prompt.md`: 코딩 에이전트 지침
- `app_spec.txt`: 빌드할 애플리케이션 명세

### 새 도구 추가

`client.py`의 `BUILTIN_TOOLS` 리스트 수정:
```python
BUILTIN_TOOLS = [
    "Read", "Write", "Edit", "Bash",
    "Glob", "Grep", "WebSearch", "WebFetch",
    # 추가 도구...
]
```

### MCP 서버 통합

Puppeteer MCP 도구 활성화 예시:
```python
PUPPETEER_TOOLS = [
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    # ...
]
```
