# Managed User Skills

This directory is the Git-managed source of truth for user-level Codex skills.

The compatibility entrypoint remains:

```text
/home/ZykLyj/.agents/skills
```

That path should be a relative symlink to this directory:

```text
../yjdev/personal-agent-os/skills
```

## Scope

Managed here:

- user skills from `/home/ZykLyj/.agents/skills/*`

Not managed here:

- Codex system skills under `/home/ZykLyj/.codex/skills/.system`
- plugin cache skills
- `/home/ZykLyj/.agents/.skill-lock.json`

## Workflow

Add or edit skills through either path:

```text
/home/ZykLyj/.agents/skills/<skill-name>
/home/ZykLyj/yjdev/personal-agent-os/skills/<skill-name>
```

Both paths resolve to the same files after migration. Commit skill changes in
the `personal-agent-os` repository.

## Verify

Run:

```bash
/home/ZykLyj/yjdev/personal-agent-os/scripts/manage-skills.sh verify
```

This checks that the compatibility path is a symlink to this managed directory
and that every managed skill has a `SKILL.md`.

## Rollback

The migration keeps a timestamped backup at:

```text
/home/ZykLyj/.agents/skills-backup-<timestamp>
```

To roll back manually, remove the symlink and restore the backup:

```bash
rm /home/ZykLyj/.agents/skills
mv /home/ZykLyj/.agents/skills-backup-<timestamp> /home/ZykLyj/.agents/skills
```
