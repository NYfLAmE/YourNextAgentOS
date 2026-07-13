# Terai Adapter

This adapter points Personal Agent OS at the self-contained Terai backend repository:

```text
/home/ZykLyj/yjdev/terai
```

Use [`terai-build`](../skills/terai-build/SKILL.md) as the project router. It owns route selection and Terai-specific overrides; detailed project facts remain in the repository.

## Required entry

Before Terai conclusions or work:

1. Load `terai-build`.
2. Read `/home/ZykLyj/yjdev/terai/AGENTS.md`.
3. Follow its task-relevant pointers into `docs/`, `arch/`, source, tests, and build-task records.

Use `terai-onboarding` only when the user explicitly requests analysis of the legacy `tafs` base, Host Kernel migration details, `terai_ye`, or old sidecar decisions. Those sources are references, not the greenfield target authority.

Do not duplicate fact priority, delivery routes, or write rules in this adapter. They are maintained by `terai-build` and the current Terai repository authorities, especially `AGENTS.md` and `docs/workflow.md`.
