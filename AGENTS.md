# Lady Sia 2 project continuity

- Continue the existing GBA reconstruction from the latest repository state. Preserve unrelated changes.
- After each verified milestone, commit and push its sources, reproducible asset changes, relevant previews and status notes to this repository. The user explicitly requests GitHub checkpoints to recover from session loss. Confirm the remote commit before reporting the checkpoint as saved.
- Run relevant checks and distinguish local results, GitHub CI results and hardware tests. Never claim a build or emulator test passed without evidence.
- Keep the overall weighted completion estimate in docs/progress.json honest. A validation-only milestone does not imply completed levels. Generate the progress display using tools/update_progress.py when the estimate changes.
- User-facing progress updates and final delivery should include the overall completion estimate and an actual build screenshot or animation when available. Clearly label reused previews.
- Maintain visual and gameplay fidelity to supplied references. Intro playback and recording overlays must remain removed; generated approximations must be identified in status notes.
- End each milestone with a recoverable source commit and state what remains unfinished. Do not imply unattended work continues after the session ends.
