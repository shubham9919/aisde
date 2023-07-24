# VisionBox DevOps #

This is intended to be a living document of DevOps basics that should apply across all project domains.

## Git

### Broad Policies
* Pull Requests are always reviewed by a second party before merging
* Multi-factor Auth (MFA) enabled
* No direct edits, _ever_ to a `master*` branch
* Avoid rebasing wherever possible
* No private account keys _ever_
* **Always** triple check `.gitignore` for sensitive files

### Repository Setup
* Set to Private
* (New) Initialized w/ Readme
* `master*` branch locked from direct commits.
* Repository Settings -> Branch Permissions -> add `master*` rule requiring 1 reviewer
> Note: **Include Administrators** in review check requirement.
* Create `master-dev` branch from `master`
* **Set `master-dev` as default branch** (defaults to `main`)

### Development Lifecycle
* New dev / feature branches are created from `master-dev`
* During development, frequently `pull from origin/master-dev` to keep the working branch up to date with any changes being merged in parallel
* Local work is tested, linted, committed, and pushed to remote
> Note: Please ensure a full Prod build succeeds before committing code. Self-onus on this prevents long waits for pre-push builds locally.
* Pull Request submitted against `master-dev` and assigned reviewer
* **Any oustanding merge conflicts** should be resolved when the PR is submitted, _not_ by the reviewer. Frequently pulling from `master-dev` and resolving locally will ease this aggravation.
* Merges are accumulated in `master-dev` and "smoke tested" by the _active_ dev team and any QA team members that may happen to be paying attention. It is **expected** that the Dev environment could be dirty at any time so no concerted QA efforts should ever be mounted there.
* Once sanity/smoke tests have passed, `master-dev` is **promoted** to `master-qa` and deployed
* When QA is deployed, *patch* version is updated: `0.1.1` -> `0.1.2`. Minor/major patch versions can be upreved at appropriate times.
> Note: For smaller projects this promotion could go straight to `master` if no in-earnest QA/Test environment is available. Consider the following as optional depending on the size and needs of the current project
* After a thorough QA pass, `master-qa` is promoted to `master-stage` and deployed. At this point the number of deployments should be _considerably_ less than QA and the release is considered to be a Release Candidate (RC) with zero showstopping bugs and _very_ minimal edge case bugs
* Once all QA tests have passed and client has signed off on offical release, `master-stage` is promoted to `master` and a new release version is cut from `master` with any relevant release notes

---