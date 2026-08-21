# Workflow SDLC với LLM Wiki (RAD)

## Tổng quan

Workflow này mô tả một quy trình phát triển phần mềm (SDLC) có sự tham gia của các AI agents và LLM Wiki để tổ chức, quản lý tài liệu xuyên suốt quá trình. Truyền cảm hứng từ [Rapid application development (RAD)](https://www.ibm.com/think/topics/rapid-application-development)

## Các thành phần chính

### 1. LLM Wiki (./llm-wiki)
- **Idea**: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- **Vai trò**: Trung tâm tổ chức & quản lý tài liệu
- **Chức năng**: 
    - Lưu trữ requirement/user story
    - Lưu trữ plan/prototype
    - Được cập nhật xuyên suốt workflow

- **Cấu trúc thư mục đề xuất**:

    ```
    wiki/
    ├── registry.yaml              # Central index; includes max_review_iterations
    ├── DESIGN.md                 # High-level design principles
    ├── SYSTEM.md                 # System topology & tech stack
    ├── 001-task-management/
    │   ├── requirement.md        # User stories, FR/NFR, success criteria
    │   ├── design.md              # Technical design (API, data models, approved UI summary)
    │   ├── mockup/
    │   │   ├── task-list.md
    │   │   └── create-task.md
    │   ├── plan.md               # Implementation tasks & steps
    │   ├── evidence.md           # Test logs & execution proof
    │   ├── quality-review.md     # (optional) Quality review report
    │   └── security-review.md    # (optional) Security review report
    │
    └── 002-feature-02/
        ├── requirement.md
        ├── design.md
        ├── mockup/
        ├── plan.md
        ├── evidence.md
        ├── quality-review.md
        └── security-review.md
    ```

- **Mô tả chi tiết**: Đây là 1 skill hướng dẫn AI Agents cách lưu trữ, truy xuất, và cập nhật thông tin vào LLM Wiki. Các agents sẽ sử dụng skill này để đảm bảo rằng tất cả các tài liệu quan trọng được tổ chức và dễ dàng truy cập.

### 2. Các Agents chính (hiện thực hóa dưới dạng skill/workflow)

#### Requirement Analyzer
- **Nhiệm vụ**: Thu thập & làm rõ yêu cầu từ user
- **Tương tác**:
    - Nhận yêu cầu mơ hồ (ask ambiguous requirements) từ User
    - Làm việc với các sub-agents để gather & clarify
- **Output**: Requirement/User Story document

- **requirement template**:

    ```markdown
    ---
    id: req-001
    title: Title of the requirement 001
    status: approved
    derived_to:
    - story-001
    - story-002
    ---

    # <Title>

    ## Scope
    <scope of the requirement e.g. frontend/backend, etc.>

    ## Description

    Goals: <goal description>

    Target Users: <list of target users>

    <detailed description of the requirement>

    ## User Stories

    ### US-001
    <description of user story 1>

    ### US-002
    <description of user story 2>

    ## Functional Requirements

    ### FR-001
    <description of functional requirement 1>

    ### FR-002
    <description of functional requirement 2>

    ## Non-Functional Requirements

    ### NFR-001
    <description of non-functional requirement 1>

    ## Testing Scenarios
    <list of testing scenarios to validate the requirement>

    ## Success Criteria
    <a list of criteria to determine if the requirement is successfully implemented>
    
    **Note for agents**: "Success Criteria" defines what "success" means for the requirement from a **business/mission perspective** — e.g., "users can complete task X within Y seconds", "system handles Z concurrent users", "compliance with regulation Q is achieved". This is NOT implementation-level acceptance criteria — do NOT confuse with "Acceptance Criteria" in design.md.

    ## User Feedbacks (Optional)
    <list of feedbacks from users to clarify the requirement>
    ```

- **Mô tả chi tiết**: 
    - Requirement Analyzer (as an agent) sẽ sử dụng các sub-agents để thu thập thông tin từ codebase, đối chiếu với yêu cầu từ user, làm rõ các yêu cầu mơ hồ, và tạo ra một tài liệu requirement/user story chi tiết. Agent đọc skill llm-wiki để lưu trữ tài liệu vào wiki/ đúng cách.
    - requirement-analyzer (as a skill) sẽ hướng dẫn các sub-agents cách gather & clarify thông tin, đảm bảo rằng tất cả các yêu cầu được hiểu rõ và đầy đủ trước khi chuyển sang bước tiếp theo. Skill này cũng tham chiếu/nhắc đến skill llm-wiki để agent (sử dụng skill) lưu trữ tài liệu vào wiki/ đúng cách.

#### User Designer
- **Nhiệm vụ**: Tạo design/mockup/plan từ requirement
- **Input**: Requirement/user story
- **Output**:
    - Technical Design (`design.md`) — API contracts, data models, acceptance criteria
    - Mockup / Plan
- **Thứ tự thực hiện**: design.md → mockup/ (user review loop) → plan.md
- **Vòng lặp với User**:
    - User review mockups → gửi request changes
    - User Designer xử lý yêu cầu thay đổi (loop)
    - Sau khi user approve mockups → cập nhật design.md status = approved

- **plan template**:

    ```markdown
    ---
    id: plan-001
    title: Title of the plan 001
    derived_from:
    - <link to requirement/user story>
    ---

    # <Title>

    ## Implementation Plan

    <detailed implementation plan for the requirement>

    ## Implementation Process

    <diagram or flowchart of the implementation process>

    ## Tasks

    ### Task 1
    
    id: I-001
    type: implementation
    description: <description of task 1>
    status: pending
    steps:
    1. Do something
    2. Do something else
    3. Do another thing

    ### Task 2

    id: T-002
    type: testing
    description: <description of task 2>
    status: pending
    steps:
    1. Do something
    2. Do thing 2

    ## UI Mockup (if applicable)
    <link to UI mockup or attach images>
    ```

- **Design template**:

    ```markdown
    ---
    id: design-001
    title: Title of the design 001
    status: draft | approved
    derived_from:
    - <link to requirement/user story>
    approved_ui_summary: <link to approved mockup or summary of approved UI>
    ---

    # <Title>

    ## Overview
    <brief description of the system/component being designed>

    ## System Architecture
    <high-level architecture diagram or description>
    <components and their responsibilities>

    ## API Contracts

    ### Endpoint 1: <Method> /<path>
    **Description**: <what this endpoint does>

    **Request**:
    ```json
    {
      "field1": "<type> — <description>",
      "field2": "<type> — <description>"
    }
    ```

    **Response** (Success - 200):
    ```json
    {
      "result": "<type> — <description>"
    }
    ```

    **Response** (Error - 4xx/5xx):
    ```json
    {
      "error": {
        "code": "<error_code>",
        "message": "<human-readable message>"
      }
    }
    ```

    **Business Rules**:
    - <rule 1>
    - <rule 2>

    ### Endpoint 2: ...

    ## Data Models

    ### Model: <EntityName>
    <description of the entity>

    | Field | Type | Constraints | Description |
    |-------|------|-------------|-------------|
    | id | UUID | PK, auto-generated | Unique identifier |
    | field1 | String | required, max 255 chars | Description |
    | field2 | Integer | optional | Description |
    | created_at | DateTime | auto-generated | Creation timestamp |
    | updated_at | DateTime | auto-updated | Last update timestamp |

    ### Model Relationships
    <diagram or description of relationships between models>

    ## Approved UI Summary
    <summary of approved UI from mockup review>
    <links to approved mockup files>

    ## Acceptance Criteria
    - <criteria 1>
    - <criteria 2>
    - <criteria 3>

    **Note for agents**: "Acceptance Criteria" defines technical conditions that the **implementation must satisfy** to be considered correct — e.g., "API returns 200 with valid JSON", "database schema matches data model", "error handling returns proper error codes". This is NOT business-level success criteria — do NOT confuse with "Success Criteria" in requirement.md. Acceptance Criteria should be **testable/verifiable** conditions that Constructor can prove with evidence.

    ## Technical Constraints
    - <constraint 1>
    - <constraint 2>

    ## Dependencies
    - <external service/component 1>
    - <external service/component 2>

    ## Related Designs
    - <link to related design documents>
    ```

- **Mockup template**: mockup content, e.g. Semantic Markdown + ASCII wireframe

    ```markdown
    ---
    id: mockup-001
    title: Title of the mockup 001
    derived_from:
    - <link to requirement/user story>
    ---

    # Mockup for <Title>

    ## Screen Name

    ```text  
    ┌──────────────────────────────────────────────────────┐ 
    │ Upload Document                                [ X ] │ 
    ├──────────────────────────────────────────────────────┤ 
    │                                                      │ 
    │ ┌──────────────────────────┐                         │ 
    │ │                          │                         │ 
    │ │ 📄                       │                         │ 
    │ │                          │                         │ 
    │ │ Drag & drop your PDF     │                         │ 
    │ │ or click to browse       │                         │ 
    │ │                          │                         │ 
    │ └──────────────────────────┘                         │ 
    │                                                      │ 
    │ Supported: PDF                                       │ 
    │ Maximum size: 50 MB                                  │ 
    │                                                      │ 
    │                                [ Cancel ] [ Upload ] │ 
    └──────────────────────────────────────────────────────┘
    ```

    ## Components
    
    - Header
      - title
      - close button
    - UploadDropzone
      - file type: PDF
      - max size: 50 MB
    - Footer
      - cancel button
      - upload button

    ## Interactions
    - User clicks "Upload" button -> triggers file upload process
    - Dropping a file selects it.
    - Upload is disabled when no file is selected.

    ## Related Requirements
    - req-001: <link to requirement 1>
    - req-002: <link to requirement 2>
    ```

- **Mô tả chi tiết**: 
    - User Designer (as an agent) sẽ tạo `design.md` (technical design) TRƯỚC, sau đó tạo mockup/plan dựa trên requirement/user story. `design.md` là tài liệu kỹ thuật cuối cùng bao gồm API contracts, data models, và approved UI summary — nó là single source of truth cho implementation. Khi UI có thay đổi hoặc requirement tạo mới UI, agent sẽ tạo thêm các bản mockup UI design để user review layout/components/interactions. Agent đọc skill llm-wiki để lưu trữ tài liệu vào wiki/ đúng cách.
    - user-designer (as a skill) sẽ hướng dẫn agent: (1) tạo `design.md` với đầy đủ API contracts và data models, (2) tạo mockup và loop với user để approve UI, (3) cập nhật design.md UI summary sau khi user approve, (4) tạo `plan.md` với task list rõ ràng. Skill này cũng tham chiếu/nhắc đến skill llm-wiki để agent lưu trữ tài liệu vào wiki/ đúng cách.

#### Constructor
- **Nhiệm vụ**: Implement tasks và testing theo Implementation Process trên plan
- **Input**: `design.md` + `plan.md` từ User Designer
- **Output**: Source code, evidence of testing -> `evidence.md`.
- **Mô tả chi tiết**:
    - Constructor (as an agent) đọc `design.md` để nắm API contracts và data models trước khi implement. Thực hiện các tasks được xác định trong Implementation Process của plan. Lập Todo list dựa trên danh sách tasks trong `plan.md`. Constructor cũng sẽ load các skill tương ứng với Programming Language/Framework/Library để sử dụng (nếu available). Sau khi hoàn thành các testing tasks, agent sẽ tạo ra evidence of testing và lưu trữ vào `evidence.md`. Agent đọc skill llm-wiki để lưu trữ tài liệu vào wiki/ đúng cách.
    - constructor (as a skill) sẽ hướng dẫn agent cách implement tasks và testing, đảm bảo rằng tất cả các yêu cầu được đáp ứng. Lập Todo list dựa trên danh sách tasks trong `plan.md`. Skill chỉ dẫn agent load các skill tương ứng với Programming Language/Framework/Library để sử dụng (nếu available). Sau khi hoàn thành, skill hướng dẫn tạo ra evidence of testing và lưu trữ vào `evidence.md`. Skill này cũng tham chiếu/nhắc đến skill llm-wiki để agent (sử dụng skill) lưu trữ tài liệu vào wiki/ đúng cách.


#### Quality Reviewer (Optional)
- **Nhiệm vụ**: Review code & yêu cầu thay đổi nếu cần
- **Vòng lặp**: Loop với Constructor cho đến khi chất lượng đạt yêu cầu (max `max_review_iterations` từ `wiki/registry.yaml`)
- **Review checklist**:
    1. Design
      - Các thành phần code tương tác với nhau có hợp lý không?
      - Thay đổi này thuộc về codebase hay nên tách thành library?
      - Có tích hợp tốt với rest of system không?
      - Thời điểm thêm functionality này có hợp lý không?
    2. Functionality
      - Code có làm được điều developer định làm không?
      - Có tốt cho end-users và developers (những người sẽ dùng code này sau này)?
      - Check edge cases, concurrency problems, race conditions, deadlocks
    3. Complexity
      - Code có phức tạp hơn mức cần thiết không?
      - Tránh over-engineering: đừng implement thứ developer đoán sẽ cần trong tương lai
      - Giải quyết vấn đề hiện tại, không phải vấn đề speculated future
    4. Tests
      - Có đủ unit/integration/end-to-end tests phù hợp với thay đổi?
      - Tests có đúng, sensible, useful không?
      - Tests sẽ fail khi code break? Hay sẽ gây false positives?
      - Tests cũng là code, đừng accept complexity không cần thiết
    5. Naming
      - Tên phải đủ dài để communicate rõ ràng nhưng không quá dài khó đọc
    6. Comments
      - Viết bằng English dễ hiểu
      - Comment nên giải thích WHY (tại sao), không phải WHAT (làm gì)
      - Code không rõ ràng -> simplify code, không phải thêm comment
      - Check TODOs cũ có thể remove được không
    7. Style
      - Tuân thủ style guides của ngôn ngữ
      - Tuân thủ style guides của project
    8. Consistency
      - Style guide là authority cuối cùng
      - Nếu local code không consistent với style guide -> bias towards following guide
      - Author nên tạo TODO/issue để clean up sau
    9. Documentation
      - Nếu thay đổi ảnh hưởng đến build, test, release -> cập nhật READMEs, docs
      - Nếu xóa/deprecate code -> xóa luôn documentation
    10. Every Line
      - Đọc mọi dòng code được assign để review (trừ data files, generated code)
      - Nếu không hiểu code → thông báo developer để clarify
    11. Context
      - Nhìn toàn bộ file, không chỉ mấy dòng thay đổi
      - Xem xét CL trong context cả system — có improve hay degrade code health?

- **Mô tả chi tiết**: 
    - Quality Reviewer (as an agent) là một optional agent - tức là một workflow bình thường có thể không cần tới agent này. Agent sẽ thực hiện review code và yêu cầu Constructor thay đổi nếu cần. 
    - quality-reviewer (as a skill) sẽ hướng dẫn agent cách review code, đảm bảo rằng tất cả các yêu cầu được đáp ứng.

#### Security Reviewer (Optional)
- **Nhiệm vụ**: Review bảo mật & yêu cầu thay đổi nếu cần
- **Vòng lặp**: Loop với Constructor cho đến khi đạt chuẩn bảo mật (max `max_review_iterations` từ `wiki/registry.yaml`)
- **Types of Vulnerabilities Detected**:
    1. Injection Attacks: SQL injection, command injection, LDAP injection, XPath injection, NoSQL injection, XXE
    2. Authentication & Authorization: Broken authentication, privilege escalation, insecure direct object references, bypass logic, session flaws
    3. Data Exposure: Hardcoded secrets, sensitive data logging, information disclosure, PII handling violations
    4. Cryptographic Issues: Weak algorithms, improper key management, insecure random number generation
    5. Input Validation: Missing validation, improper sanitization, buffer overflows
    6. Business Logic Flaws: Race conditions, time-of-check-time-of-use (TOCTOU) issues
    7. Configuration Security: Insecure defaults, missing security headers, permissive CORS
    8. Supply Chain: Vulnerable dependencies, typosquatting risks
    9. Code Execution: RCE via deserialization, pickle injection, eval injection
    10. Cross-Site Scripting (XSS): Reflected, stored, and DOM-based XSS

- **False Positive Filtering**: 

   The tool automatically excludes a variety of low-impact and false positive prone findings to focus on high-impact vulnerabilities:
     - Denial of Service vulnerabilities
     - Rate limiting concerns
     - Memory/CPU exhaustion issues
     - Generic input validation without proven impact
     - Open redirect vulnerabilities

   The false positive filtering can also be tuned as needed for a given project's security goals.

- **Mô tả chi tiết**: 
    - Security Reviewer (as an agent) là một optional agent - tức là một workflow bình thường có thể không cần tới agent này. Agent sẽ thực hiện review bảo mật và yêu cầu Constructor thay đổi nếu cần. Tìm kiếm Vulnerabilities sau đó thực hiện False Positive Filtering để loại bỏ các findings không quan trọng.
    - security-reviewer (as a skill) sẽ hướng dẫn agent cách review bảo mật, đảm bảo rằng tất cả các yêu cầu được đáp ứng. Tìm kiếm Vulnerabilities sau đó thực hiện False Positive Filtering để loại bỏ các findings không quan trọng.

### 3. User (Stakeholder)
- Tham gia ở nhiều giai đoạn:
    - Cung cấp yêu cầu ban đầu cho Requirement Analyzer
    - Review và request changes với User Designer (loop)
    - Xác nhận (confirm) kết quả cuối cùng sau khi Quality Reviewer và Security Reviewer hoàn thành

## Luồng workflow chi tiết

```
User -> [ask ambiguous requirements]
   ↓
Requirement Analyzer -> [gather & clarify with sub-agents]
   ↓
Requirement/User Story -> [lưu vào wiki/ bằng llm-wiki skill]
   ↓
User Designer -> [tạo design.md (API contracts, data models)]
   ↓
User Designer -> [tạo mockup/]
   ↓ ←-> User [loop: review mockup ↔ request changes]
   ↓
User Designer -> [cập nhật design.md status=approved, tạo plan.md]
   ↓
Plan/Prototype -> [lưu vào wiki/ bằng llm-wiki skill]
   ↓
Constructor -> [implement tasks + testing]
   ↓
Source Code + evidence.md -> [lưu vào wiki/ bằng llm-wiki skill]
   ↓
Quality Reviewer -> [review & request changes] -> Constructor [loop max N lần từ registry.yaml]
   ↓
Security Reviewer -> [review & request changes] -> Constructor [loop max N lần từ registry.yaml]
   ↓
User -> [confirm] ✓
```

### Registry Configuration (`wiki/registry.yaml`)

| Key | Mô tả | Default |
|-----|--------|---------|
| `max_review_iterations` | Số lần max Constructor-Reporter loop | `3` |

Các reviewer đọc `max_review_iterations` từ `wiki/registry.yaml` để giới hạn số lần feedback loop.
