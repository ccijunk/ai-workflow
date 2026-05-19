# Meta — Reflect and Update Memory

## Role
Read your role prompt and learned heuristics from `memory/meta.md`.

## Task
Analyze the run and update memory files for future runs:

**reflect.md structure:**

**Run summary:** One paragraph: what was built, how many gate cycles each gate triggered.

**What worked:** By role: practices or artifact sections that produced high-quality output.

**What degraded:** By role: sections that were thin, inconsistent, or produced noise.

**Gate statistics:** Table: gate | APPROVED on attempt # | total retries | max retries hit?

**Carry-forward:** Table: role | change to role prompt or template | reason

**Memory updates:** For each role with meaningful signal, append new heuristics or anti-patterns:

**Heuristics format:**
```markdown
- observation: "<pattern observed>"
  run_date: "<date>"
  context: "<run context>"
```

**Anti-patterns format:**
```markdown
- pattern: "<anti-pattern description>"
  reason: "<why it fails>"
  discovered_in: "<run identifier>"
```

**Outputs:**
- Write `reflect.md`
- Write updated memory files (append new content to existing):
  - memory/ba.md (if BA had signal)
  - memory/architect.md (if Architect had signal)
  - memory/test-arch.md (if Test-Arch had signal)
  - memory/developer.md (if Developer had signal)
  - memory/test-developer.md (if Test-Developer had signal)
  - memory/reviewer.md (if Reviewer had signal)