---
title: Pasting code into nano mangles indentation
date: 2026-09-01
tags: [linux, tooling, gotcha]
---

# Pasting code into nano mangles indentation

Pasting a Python block into nano doubles the indentation because auto-indent adds spaces on every new line.
The result is an IndentationError on the first indented line.

Fixes, in order of preference:
1. Write the file with a heredoc at the shell prompt: cat > file.py << 'EOF' ... EOF. Exact bytes, no editor.
2. In nano, press Alt+I to toggle auto-indent off before pasting.
3. Use a real editor over SSH.

The heredoc also fails if you paste it INTO nano instead of at the prompt; the first line becomes part of the file.
