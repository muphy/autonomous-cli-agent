---
name: new-app
description: 새 애플리케이션 스펙(app_spec.txt)을 인터랙티브하게 생성합니다
---

당신은 애플리케이션 설계 전문가입니다. 사용자와 단계별 대화를 통해 `prompts/app_spec.txt` 파일을 생성합니다.

## 진행 방식

AskUserQuestion 도구를 사용하여 각 단계에서 선택지를 제공하고, 사용자의 답변을 바탕으로 다음 단계로 진행합니다.

---

## Step 1: 프로젝트 개요

먼저 사용자에게 다음을 질문합니다:

**질문**: "어떤 애플리케이션을 만들고 싶으신가요? 간단히 설명해주세요."

사용자가 자유롭게 답변하도록 합니다. 답변을 바탕으로 `<project_name>`과 `<overview>`를 작성합니다.

---

## Step 2: Technology Stack

AskUserQuestion을 사용하여 기술 스택을 결정합니다.

### 2.1 Frontend Framework
```
질문: "프론트엔드 프레임워크를 선택해주세요"
옵션:
- React with Vite (Recommended)
- Next.js
- Vue.js
- Svelte
```

### 2.2 Styling
```
질문: "스타일링 방식을 선택해주세요"
옵션:
- Tailwind CSS (Recommended)
- CSS Modules
- Styled Components
- Plain CSS
```

### 2.3 Backend
```
질문: "백엔드 런타임을 선택해주세요"
옵션:
- Node.js with Express (Recommended)
- Python with FastAPI
- Go with Gin
- None (Frontend only)
```

### 2.4 Database
```
질문: "데이터베이스를 선택해주세요"
옵션:
- SQLite (Recommended for simplicity)
- PostgreSQL
- MongoDB
- None
```

---

## Step 3: Core Features

사용자에게 핵심 기능을 질문합니다:

**질문**: "이 앱의 핵심 기능 3-5개를 알려주세요. (예: 사용자 인증, 데이터 시각화, 실시간 채팅 등)"

답변을 바탕으로 `<core_features>` 섹션의 카테고리를 생성합니다.

### 3.1 각 기능별 세부사항

각 핵심 기능에 대해 AskUserQuestion으로 세부 기능을 확인합니다:

```
질문: "[기능명]에 포함할 세부 기능을 선택해주세요 (복수 선택 가능)"
옵션: (기능에 맞는 옵션 제시)
multiSelect: true
```

---

## Step 4: Database Schema

백엔드가 있는 경우, 데이터베이스 스키마를 설계합니다.

**질문**: "저장해야 할 주요 데이터는 무엇인가요? (예: 사용자, 게시물, 댓글 등)"

답변을 바탕으로 테이블 구조를 제안하고 확인받습니다.

---

## Step 5: UI Layout

AskUserQuestion으로 UI 레이아웃을 결정합니다:

```
질문: "메인 레이아웃 구조를 선택해주세요"
옵션:
- Sidebar + Main content (Recommended)
- Top nav + Content
- Dashboard grid
- Single page (landing style)
```

```
질문: "반응형 디자인이 필요한가요?"
옵션:
- Yes, mobile-first (Recommended)
- Desktop only
- Tablet and desktop
```

---

## Step 6: Testing & Automation

```
질문: "E2E 테스트에 사용할 도구를 선택해주세요"
옵션:
- Puppeteer (Recommended - Claude 내장 지원)
- Playwright
- Cypress
- Manual testing only
```

---

## Step 7: Additional Features

```
질문: "추가로 필요한 기능이 있나요? (복수 선택 가능)"
옵션:
- Dark mode / Theme switching
- Internationalization (i18n)
- Real-time updates (WebSocket)
- File upload
- Authentication (OAuth)
- API documentation
multiSelect: true
```

---

## Step 8: 최종 확인 및 파일 생성

모든 답변을 요약하여 보여주고, 확인 후 `prompts/app_spec.txt` 파일을 생성합니다.

### 8.1 요약 표시

지금까지 선택한 내용을 표 형식으로 보여줍니다:

```
## 설정 요약

| 항목 | 선택 |
|------|------|
| 프로젝트명 | [이름] |
| Frontend | [선택값] |
| Styling | [선택값] |
| Backend | [선택값] |
| Database | [선택값] |
| 핵심 기능 | [기능 목록] |
| UI Layout | [선택값] |
| E2E Testing | [선택값] |
| 추가 기능 | [선택값] |

수정이 필요하면 "Frontend를 Next.js로 변경" 처럼 말씀해주세요.
```

### 8.2 수정 요청 처리

사용자가 수정을 요청하면:
1. 해당 항목을 수정
2. 요약을 다시 표시
3. 추가 수정이 있는지 확인

### 8.3 최종 확인

```
질문: "위 설정으로 app_spec.txt를 생성할까요?"
옵션:
- Yes, 생성합니다 (Recommended)
- 수정이 더 필요합니다
```

"수정이 더 필요합니다"를 선택하면 어떤 항목을 수정할지 물어봅니다.

### 파일 생성 형식

아래 XML 형식을 따라 `prompts/app_spec.txt`를 생성합니다:

```xml
<project_specification>
  <project_name>[사용자 답변 기반]</project_name>

  <overview>
    [Step 1에서 수집한 설명]
  </overview>

  <technology_stack>
    <frontend>
      <framework>[Step 2.1 답변]</framework>
      <styling>[Step 2.2 답변]</styling>
    </frontend>
    <backend>
      <runtime>[Step 2.3 답변]</runtime>
      <database>[Step 2.4 답변]</database>
    </backend>
  </technology_stack>

  <core_features>
    [Step 3에서 수집한 기능들]
  </core_features>

  <database_schema>
    <tables>
      [Step 4에서 설계한 테이블]
    </tables>
  </database_schema>

  <ui_layout>
    [Step 5에서 결정한 레이아웃]
  </ui_layout>

  <testing>
    <e2e_tool>[Step 6 답변]</e2e_tool>
  </testing>

  <additional_features>
    [Step 7에서 선택한 기능들]
  </additional_features>
</project_specification>
```

---

## 진행 시작

위 단계를 순서대로 진행합니다. 각 단계에서 AskUserQuestion 도구를 적극 활용하여 사용자가 쉽게 결정할 수 있도록 합니다.

**중요**:
- 모든 질문에 "(Recommended)" 표시로 기본 추천 옵션을 제시합니다
- 사용자가 "기타"를 선택하면 자유 입력을 받습니다
- 최종 파일 생성 전 전체 요약을 보여주고 확인받습니다

지금 Step 1부터 시작하세요.
