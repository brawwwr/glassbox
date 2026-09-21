# scratch/ — hand-off scripts and the current step list

Claude writes scripts and step lists here on the Mac; the PC pulls and runs them. Replaces emailing
command blocks back and forth.

Rules (this repo is public):
- Nothing in here may contain a secret, key, password or personal e-mail. Scripts that need secrets
  generate them at run time or prompt for them.
- `NEXT.md` is the live "what to run now" list. It is overwritten as we go.
- Scripts are numbered by phase. Run them from the repo root: `bash scratch/03_langfuse_env.sh`.
- Anything here is disposable; the durable record is NOTES.md.
