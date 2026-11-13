[스킬 ZIP 다운로드](https://github.com/testofschool/problem-finding-skill/releases/download/v1.0.0/hackathon-win-protocol-public.zip)

# Problem Finding

대회의 주최 의도와 심사 기준을 읽고, 어떤 문제를 왜 골랐는지 근거로 설명하도록 돕는 스킬입니다.

ZIP을 내려받아 압축을 푼 뒤, `skills/hackathon-win-protocol` **폴더 전체**를 사용할 프로젝트에 복사하세요.

- **Codex:** `.agents/skills/hackathon-win-protocol/`에 넣습니다.
- **Claude Code:** `.claude/skills/hackathon-win-protocol/`에 넣습니다.

스크립트와 참고 문서도 필요하므로 `SKILL.md`만 따로 복사하지 마세요. 파일을 읽고 **Python 3**를 실행할 수 있는 환경에서 사용합니다.

그 프로젝트에서 AI를 열고 이렇게 시작해 보세요.

```text
hackathon-win-protocol을 적용해줘.
참가할 대회는 [대회 공식 URL], 목표는 [내 목표]야.
먼저 주최 의도와 심사 기준부터 확인해줘.
```

Codex CLI·IDE에서는 `$hackathon-win-protocol`, Claude Code에서는 `/hackathon-win-protocol`로 직접 호출할 수도 있습니다.

이 스킬은 대회 회고에서 정리한 문제 선택과 검증 절차입니다. 원래 참가자의 대회 자료·이메일·대화 로그는 포함하지 않으며, 선정이나 수상을 보장하지 않습니다. 자기 대회의 조건과 판단에 맞게 고쳐 쓰세요.

설치·호출 방법은 [OpenAI의 스킬 안내](https://learn.chatgpt.com/docs/build-skills)와 [Claude Code의 스킬 안내](https://code.claude.com/docs/en/skills)를 따릅니다.
