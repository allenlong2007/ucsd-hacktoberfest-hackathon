# Onboarding prompt: paste this into your AI coding agent

Replace `<AREA>` with your area (`frontend`, `backend`, `ai`, or `infra`), then paste the
whole block into Claude Code, Codex, Gemini CLI, Cursor, or whatever agent you use.

---

I'm joining a 4-person hackathon team. Set me up on our shared GitHub repo
`allenlong2007/ucsd-hacktoberfest-hackathon`. My area is **<AREA>**, so my branch is
`dev/<AREA>` and my folder is `<AREA>/`.

Do these steps in order, and show me the output of each:

1. **GitHub CLI.** Check that `git` and `gh` are installed. If `gh` is missing, tell me how
   to install it for my OS (https://cli.github.com). Run `gh auth status`. If I'm not logged
   in, have me run `gh auth login` (GitHub.com, HTTPS, "Login with a web browser") and wait
   until I'm done. Then run `gh auth setup-git` so git pushes use that login.
2. **Git identity.** If `git config --global user.name` or `user.email` is empty, ask me
   for them and set them.
3. **Collaborator access.** Run `gh api user/repository_invitations` and accept any invite
   for this repo with `gh api -X PATCH user/repository_invitations/<id>`. If there's no
   invite, tell me to ask Allen to add my GitHub username as a collaborator.
4. **Clone.** Run `gh repo clone allenlong2007/ucsd-hacktoberfest-hackathon`, `cd` into it,
   then `git checkout dev/<AREA>`.
5. **Verify.** Run `./scripts/check-setup.sh dev/<AREA>`. Every line must say `[ok]`.
   Fix anything marked FAIL, then rerun it.
6. **Read the rules.** Read `AGENTS.md` and `OWNERSHIP.md` and follow them from now on.
   In short: commit only on `dev/<AREA>`, create or edit files only inside `<AREA>/`, never
   push to `main`, and merge only through a PR (`gh pr create --base main`).
7. **File permissions.** The repo ships a `.claude/settings.json` that lets Claude Code read
   the whole project and edit files without prompting. If you're Claude Code, confirm it's
   loaded. If you're another agent, turn on read and write access to this project folder in
   your own tool's settings (for example Codex: `--sandbox workspace-write`; Cursor or
   Gemini: trust this workspace).
8. **Prove it works.** Add a line to `<AREA>/README.md` saying who owns this area (my GitHub
   username), commit it as `<AREA>: claim area`, and run `git push -u origin dev/<AREA>`.
   Then tell me "Setup complete" with my GitHub username so I can report it to the team.
