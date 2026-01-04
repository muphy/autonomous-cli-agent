# Autonomous CLI Agent

Claude CLI를 사용한 자율 코딩 에이전트. **API 키 없이** Claude Pro/Max 구독만으로 실행 가능합니다.

## 특징

- Claude CLI subprocess 기반 (SDK 불필요)
- ANTHROPIC_API_KEY 없이 실행
- Claude Pro/Max 구독으로 인증
- 장기 실행 자율 코딩 세션 지원

## 설치

### 1. Claude CLI 설치

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Claude 로그인

```bash
claude /connect
```

브라우저에서 Claude Pro/Max 계정으로 로그인합니다.

### 3. Python 의존성 설치

```bash
pip install -r requirements.txt
```

## 사용법

```bash
# 기본 실행
python main.py --project-dir ./my_project

# 모델 선택 (sonnet, opus, haiku)
python main.py --project-dir ./my_project --model opus

# 반복 횟수 제한 (테스트용)
python main.py --project-dir ./my_project --max-iterations 5
```

## 파일 구조

```
autonomous-cli-agent/
├── main.py          # 진입점
├── agent.py         # 에이전트 로직
├── client.py        # Claude CLI 클라이언트
├── progress.py      # 진행 상황 추적
├── prompts.py       # 프롬프트 로딩
├── prompts/         # 프롬프트 템플릿
│   ├── app_spec.txt
│   ├── initializer_prompt.md
│   └── coding_prompt.md
└── requirements.txt
```

## 작동 방식

1. `main.py`가 Claude CLI를 subprocess로 실행
2. `--output-format stream-json`으로 실시간 스트리밍
3. 세션 간 컨텍스트 유지 (`--resume` 옵션)
4. `feature_list.json` 기반 진행 상황 추적

## 라이선스

MIT
