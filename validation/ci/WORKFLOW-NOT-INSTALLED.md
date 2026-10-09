# CI workflow is preserved here as text, not installed

`component-ci.workflow.yml.txt` is a verbatim copy of the working GitHub Actions
workflow that builds and tests `MrSpicyUI` on a macOS runner
(`.github/workflows/component-ci.yml` on `abadrun/8ballspicy`, branch
`arena/6264dd0a-8ballspicy`).

It is stored as `.txt` in this directory — **not** under `.github/workflows/` —
because the GitHub App token available to this session was rejected when pushing
any commit that creates or updates a workflow file:

```
! [remote rejected] (refusing to allow a GitHub App to create or update workflow
  `.github/workflows/component-ci.yml` without `workflows` permission)
```

Consequences, stated plainly:

* This session branch (`arena/627c356f-8ballspicy` on `Adhambadrun/8ballspicy`)
  **cannot run the macOS component CI itself**, and therefore cannot produce its
  own new build/test evidence.
* All build and test evidence cited by this session was produced by runs on
  `abadrun/8ballspicy` and was **independently re-verified** here: artifact ZIPs
  were downloaded, their SHA-256 recomputed and compared to the recorded values,
  the Mach-O outputs re-parsed, and the raw `xcodebuild` logs re-read for the
  actual executed / failed / skipped counts.
* To re-enable CI on a branch, a maintainer with the `workflows` scope must copy
  this file to `.github/workflows/component-ci.yml` and update the two references
  to the session branch name (the `on.push.branches` filter and the
  `test "$SESSION_BRANCH" = ...` guard in the publish job).

The workflow only builds and tests the independent `MrSpicyUI` component and
performs read-only static inspection of the input IPA. It never modifies,
re-signs, or repackages the 8 Ball Pool application.
