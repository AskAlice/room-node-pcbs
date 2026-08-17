# CI workflows pending activation

The three workflow files here could not be pushed directly to `.github/workflows/`
because the GitHub OAuth token used by the automation lacks the `workflow` scope.

**To activate:** move (or rename) this folder's files into `.github/workflows/`
in the GitHub web UI (Add file → upload, or edit paths), or reconnect the GitHub
integration with the `workflow` scope and let the bot re-push.

- `docs.yml` — builds the MkDocs Material docs in `docs/` and deploys to GitHub Pages
  (also enable Settings → Pages → Source: GitHub Actions).
- `render.yml` — downloads KiCad 10.0.5 AppImage, regenerates all boards from
  `build.py`, binds STEP 3D models, produces raytraced renders + routing/schematic
  exports + JLCPCB fab zips, and commits them back to the repo.
- `fab.yml` — rezips `fab/<board>/` into `*_jlcpcb.zip` artifacts on fab/ changes.
