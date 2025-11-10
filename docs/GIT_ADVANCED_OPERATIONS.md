# Advanced Git Operations & Troubleshooting

## 📋 Table of Contents

- [Complex Merge Scenarios](#complex-merge-scenarios)
- [Advanced Rebase Operations](#advanced-rebase-operations)
- [Disaster Recovery](#disaster-recovery)
- [Submodule & Subtree Management](#submodule--subtree-management)
- [Large File Handling](#large-file-handling)
- [Git Internals & Debugging](#git-internals--debugging)
- [Performance Optimization](#performance-optimization)
- [Security & Secrets Management](#security--secrets-management)
- [Advanced Workflows](#advanced-workflows)
- [Root Cause Analysis](#root-cause-analysis)

---

## Complex Merge Scenarios

### Three-Way Merge with Conflicts

**Scenario**: Merging a long-lived feature branch with multiple conflicts

```bash
# Step 1: Update your branch first
git checkout feature/long-lived-feature
git fetch origin
git rebase origin/main

# Step 2: If conflicts occur, use three-way merge strategy
git merge --strategy=recursive --strategy-option=patience origin/main

# Step 3: For complex conflicts, use merge tool
git mergetool --tool=vimdiff

# Step 4: If you need to restart the merge
git merge --abort
git merge --strategy=ours origin/main  # Keep our changes
# OR
git merge --strategy=theirs origin/main  # Keep their changes
```

**Edge Case**: Binary file conflicts

```bash
# Binary files can't be merged - choose one version
git checkout --ours path/to/binary/file.png    # Keep our version
git checkout --theirs path/to/binary/file.png  # Keep their version
git add path/to/binary/file.png
```

### Octopus Merge (Multiple Branches)

**Scenario**: Merging multiple feature branches simultaneously

```bash
# Merge 3 branches at once
git merge feature/auth feature/payments feature/notifications

# If conflicts occur, Git will stop
# You can't use octopus merge with conflicts - fall back to sequential merges
git merge --abort
git merge feature/auth
git merge feature/payments
git merge feature/notifications
```

### Subtree Merge Strategy

**Scenario**: Merging an external project into a subdirectory

```bash
# Add the external repo as a remote
git remote add external-lib https://github.com/external/lib.git
git fetch external-lib

# Merge using subtree strategy
git merge -s subtree --allow-unrelated-histories external-lib/main

# Or with prefix
git merge -s subtree=lib/ --allow-unrelated-histories external-lib/main
```

### Cherry-Pick with Conflicts

**Scenario**: Applying specific commits from another branch

```bash
# Cherry-pick a single commit
git cherry-pick abc123

# Cherry-pick a range of commits
git cherry-pick abc123^..def456

# Cherry-pick without committing (review first)
git cherry-pick -n abc123

# If conflicts occur
git status
# Fix conflicts
git add <resolved-files>
git cherry-pick --continue

# If you want to skip this commit
git cherry-pick --skip

# If you want to abort
git cherry-pick --abort
```

**Edge Case**: Cherry-picking merge commits

```bash
# Merge commits have 2 parents - specify which to use
git cherry-pick -m 1 <merge-commit-sha>  # Use first parent
git cherry-pick -m 2 <merge-commit-sha>  # Use second parent
```

---

## Advanced Rebase Operations

### Interactive Rebase (Squash, Fixup, Edit, Reword)

```bash
# Rebase last 5 commits interactively
git rebase -i HEAD~5

# In the editor:
# pick abc123 Initial commit
# squash def456 Fix typo          # Combine with previous
# fixup 789abc Another fix         # Combine, discard message
# reword bcd234 Update feature     # Change commit message
# edit efg567 Major change         # Pause to amend
# drop hij890 Experimental feature # Remove this commit

# If you chose 'edit', make changes then:
git add <files>
git commit --amend
git rebase --continue

# If things go wrong
git rebase --abort
```

**Edge Case**: Rebase with merge commits

```bash
# Preserve merge commits
git rebase -p origin/main  # DEPRECATED in newer Git versions

# New way (Git 2.18+):
git rebase --rebase-merges origin/main

# Or flatten merge commits (convert to linear history)
git rebase origin/main  # Default behavior
```

### Rebase onto Different Base

**Scenario**: Moving a branch from one base to another

```bash
# Current state:
#   A---B---C  main
#        \
#         D---E  feature
#              \
#               F---G  sub-feature

# Move sub-feature to be based on main instead of feature
git rebase --onto main feature sub-feature

# Result:
#   A---B---C  main
#        \   \
#         \   F'---G'  sub-feature
#          \
#           D---E  feature
```

### Autosquash Workflow

```bash
# Make a commit
git commit -m "Add feature"

# Later, make a fix for that commit
git add <files>
git commit --fixup abc123  # abc123 is the original commit

# Even later, auto-squash all fixup commits
git rebase -i --autosquash HEAD~10
```

### Rebase with Conflict Resolution Strategy

```bash
# Rebase with automatic conflict resolution preference
git rebase -Xours origin/main   # Prefer our changes
git rebase -Xtheirs origin/main # Prefer their changes

# Rebase with patience algorithm (better for large refactors)
git rebase -Xpatience origin/main

# Ignore whitespace changes during rebase
git rebase -Xignore-space-change origin/main
```

**Edge Case**: Rebase interrupted by hooks

```bash
# If pre-commit hooks are failing
git rebase --no-verify

# Skip Git LFS during rebase
GIT_LFS_SKIP_SMUDGE=1 git rebase origin/main
```

---

## Disaster Recovery

### Recovering Deleted Commits (Reflog)

**Scenario**: You accidentally reset/rebased and lost commits

```bash
# View all ref changes (including "lost" commits)
git reflog

# Example output:
# abc123 HEAD@{0}: reset: moving to HEAD~1
# def456 HEAD@{1}: commit: Important work (LOST)
# ghi789 HEAD@{2}: commit: Previous work

# Recover the lost commit
git cherry-pick def456
# OR
git reset --hard def456
# OR create a new branch
git branch recovery def456
```

**Edge Case**: Reflog expired

```bash
# Reflog entries expire after 90 days by default
# Find dangling commits before they're garbage collected
git fsck --lost-found

# This shows dangling commits
# Examine them:
git show <dangling-commit-sha>

# Recover:
git branch recovery <dangling-commit-sha>
```

### Recovering Deleted Branch

```bash
# Find the branch in reflog
git reflog show --all | grep "branch-name"

# Or find it by commit message
git log --all --oneline | grep "commit message"

# Recreate the branch
git branch recovered-branch <commit-sha>
```

### Undoing a Public Push

**Scenario**: You pushed bad code to production

```bash
# Option 1: Revert (safe for public branches)
git revert <bad-commit-sha>
git push origin main

# Option 2: Create a new commit that undoes changes
git revert -n HEAD~3..HEAD  # Revert last 3 commits
git commit -m "Revert changes from deploy"
git push origin main

# Option 3: Force push (DANGEROUS - only if no one else pulled)
git reset --hard HEAD~1
git push --force-with-lease origin main  # Safer than --force
```

**Edge Case**: Someone already pulled your bad commit

```bash
# You CANNOT rewrite history
# Must use revert
git revert <bad-commit-sha>
git push origin main

# Team members then:
git pull origin main  # They get the revert
```

### Recovering from Corrupted Repository

```bash
# Check for corruption
git fsck --full

# If objects are corrupted, try to recover from remote
git fetch origin
git reset --hard origin/main

# If local repo is completely broken
cd ..
mv broken-repo broken-repo.bak
git clone <remote-url> broken-repo
cd broken-repo
# Restore any uncommitted work from broken-repo.bak
```

### Split a Commit into Multiple Commits

```bash
# Start interactive rebase
git rebase -i HEAD~3

# Mark the commit as 'edit'
# When rebase pauses:
git reset HEAD^  # Unstage all changes from the commit

# Now stage and commit in smaller chunks
git add file1.py
git commit -m "Part 1: Add validation"

git add file2.py
git commit -m "Part 2: Add tests"

git rebase --continue
```

---

## Submodule & Subtree Management

### Submodules: Advanced Operations

**Adding and Updating Submodules**

```bash
# Add a submodule
git submodule add https://github.com/external/lib.git lib/external

# Clone a repo with submodules
git clone --recurse-submodules https://github.com/your/repo.git

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Update all submodules to latest
git submodule update --remote --recursive

# Update specific submodule
git submodule update --remote lib/external
```

**Edge Case**: Submodule detached HEAD

```bash
# Submodules are in detached HEAD by default
cd lib/external
git checkout main  # Switch to a branch
cd ../..

# Or update .gitmodules to track a branch
git config -f .gitmodules submodule.lib/external.branch main
git submodule update --remote
```

**Removing a Submodule**

```bash
# Step 1: Deinitialize
git submodule deinit -f lib/external

# Step 2: Remove from index
git rm -f lib/external

# Step 3: Remove from .git/modules
rm -rf .git/modules/lib/external

# Step 4: Commit
git commit -m "Remove external library submodule"
```

**Converting Submodule to Subtree**

```bash
# Remove submodule (see above)
# Then add as subtree
git subtree add --prefix=lib/external https://github.com/external/lib.git main --squash
```

### Subtrees: Advanced Operations

**Adding a Subtree**

```bash
# Add remote
git remote add external-lib https://github.com/external/lib.git

# Add subtree (first time)
git subtree add --prefix=lib/external external-lib main --squash

# Update subtree (later)
git subtree pull --prefix=lib/external external-lib main --squash

# Push changes back to upstream
git subtree push --prefix=lib/external external-lib main
```

**Splitting Out a Subtree**

```bash
# Extract subtree history into a new branch
git subtree split --prefix=lib/external -b external-lib-only

# Push to new repo
git push git@github.com:your/extracted-lib.git external-lib-only:main
```

**Edge Case**: Subtree merge conflicts

```bash
# If subtree pull fails with conflicts
git subtree pull --prefix=lib/external external-lib main --squash

# Resolve conflicts manually
git status
# Fix conflicts
git add <resolved-files>
git commit
```

---

## Large File Handling

### Git LFS (Large File Storage)

**Setup and Usage**

```bash
# Install Git LFS
git lfs install

# Track large files by extension
git lfs track "*.psd"
git lfs track "*.mp4"
git lfs track "*.zip"

# Track specific file
git lfs track "large-dataset.csv"

# Check what's being tracked
git lfs ls-files

# Migrate existing files to LFS
git lfs migrate import --include="*.psd,*.mp4"

# Clone with LFS
git lfs clone https://github.com/your/repo.git
```

**Edge Cases and Troubleshooting**

```bash
# LFS smudge error (file not downloaded)
git lfs pull

# Re-download all LFS files
git lfs fetch --all
git lfs checkout

# Skip LFS during clone (faster, gets pointers only)
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/your/repo.git

# Later, download LFS files
git lfs pull

# Check LFS bandwidth usage
git lfs env

# Prune old LFS files
git lfs prune
```

### Reducing Repository Size

**BFG Repo-Cleaner (Remove Large Files from History)**

```bash
# Install BFG
# brew install bfg  # macOS
# Download from https://rtyley.github.io/bfg-repo-cleaner/

# Clone a fresh bare repo
git clone --mirror https://github.com/your/repo.git repo.git

# Remove files larger than 100MB
java -jar bfg.jar --strip-blobs-bigger-than 100M repo.git

# Remove specific file from history
java -jar bfg.jar --delete-files large-file.zip repo.git

# Remove folder from history
java -jar bfg.jar --delete-folders .venv repo.git

# Clean up
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push --force

# Team members must re-clone
```

**Git Filter-Repo (Modern Alternative)**

```bash
# Install
pip install git-filter-repo

# Remove file from history
git filter-repo --path large-file.zip --invert-paths

# Remove directory from history
git filter-repo --path .venv/ --invert-paths

# Remove files by size
git filter-repo --strip-blobs-bigger-than 100M

# Rewrite commit messages
git filter-repo --replace-message ../replacements.txt
```

**Shallow Clone (Reduce Download Size)**

```bash
# Clone with limited history
git clone --depth 1 https://github.com/your/repo.git  # Only latest commit
git clone --depth 50 https://github.com/your/repo.git # Last 50 commits

# Clone specific branch only
git clone --single-branch --branch main https://github.com/your/repo.git

# Deepen a shallow clone
git fetch --deepen 100  # Fetch 100 more commits
git fetch --unshallow   # Fetch all history
```

---

## Git Internals & Debugging

### Understanding Git Objects

```bash
# View object type
git cat-file -t <sha1>  # blob, tree, commit, tag

# View object contents
git cat-file -p <sha1>

# View object size
git cat-file -s <sha1>

# Find object
git rev-parse HEAD
git rev-parse main^{tree}  # Get tree object of main

# List all objects
git rev-list --objects --all

# Count objects
git count-objects -v
```

### Debugging Merge Conflicts

```bash
# See common ancestor (merge base)
git merge-base feature-branch main

# View three versions of a conflicted file
git show :1:file.txt  # Common ancestor
git show :2:file.txt  # Our version (HEAD)
git show :3:file.txt  # Their version (merging branch)

# Use three-way diff
git diff HEAD...feature-branch  # Changes in feature-branch since fork

# Blame with merge commits
git blame -M file.txt  # Detect moved lines
git blame -C file.txt  # Detect copied lines from other files
git blame -w file.txt  # Ignore whitespace
```

### Bisect (Binary Search for Bugs)

```bash
# Start bisect
git bisect start

# Mark current commit as bad
git bisect bad

# Mark known good commit
git bisect good v1.0

# Git checks out middle commit - test it
# If it's bad:
git bisect bad
# If it's good:
git bisect good

# Git automatically narrows down
# When found:
git bisect reset  # Return to original state

# Automated bisect
git bisect start HEAD v1.0
git bisect run pytest tests/test_feature.py
```

### Grep Across History

```bash
# Search for string in all commits
git log -S "searchString"

# Search with regex
git log -G "regex.*pattern"

# Search in specific file
git log -S "searchString" -- path/to/file.txt

# Search commit messages
git log --grep="bug fix"

# Search across all branches
git log --all --grep="feature"
```

### Find Who Deleted a File

```bash
# Find when file was deleted
git log --full-history --diff-filter=D -- path/to/file.txt

# See the file content before deletion
git show <commit>^:path/to/file.txt

# Restore deleted file
git checkout <commit>^ -- path/to/file.txt
```

---

## Performance Optimization

### Speeding Up Git Operations

```bash
# Enable parallel checkout (Git 2.36+)
git config --global checkout.workers 0  # Auto-detect CPU cores

# Enable filesystem monitor (Git 2.39+ on macOS/Windows)
git config core.fsmonitor true
git config core.untrackedcache true

# Aggressive compression
git config --global pack.compression 9
git config --global pack.windowMemory 100m

# Increase pack window
git config --global pack.window 1

# Use Git maintenance (Git 2.30+)
git maintenance start  # Runs background tasks
```

### Optimizing Large Repositories

```bash
# Repack repository
git repack -afd --depth=250 --window=250

# Aggressive garbage collection
git gc --aggressive --prune=now

# Prune unreachable objects
git prune --expire=now

# Clean up remote tracking branches
git remote prune origin

# Enable sparse checkout (only checkout needed directories)
git sparse-checkout init --cone
git sparse-checkout set addons/custom docs

# Enable partial clone (Git 2.22+)
git clone --filter=blob:none https://github.com/your/repo.git
git clone --filter=tree:0 https://github.com/your/repo.git  # Even more aggressive
```

### Parallel Fetching

```bash
# Fetch multiple remotes in parallel
git config --global fetch.parallel 4

# Submodule parallel fetch
git config --global submodule.fetchJobs 4
```

---

## Security & Secrets Management

### Removing Secrets from History

**Using BFG Repo-Cleaner**

```bash
# Create a file with secrets to remove
cat > passwords.txt << EOF
secret_password_123
api_key_abc456def
EOF

# Remove secrets from history
java -jar bfg.jar --replace-text passwords.txt repo.git

# Cleanup
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

**Using Git Filter-Repo**

```bash
# Remove specific secrets
git filter-repo --replace-text <(echo 'secret_password_123==>REMOVED')

# Remove .env files from history
git filter-repo --path .env --invert-paths
git filter-repo --path config/secrets.yml --invert-paths
```

### Git Signing (GPG)

```bash
# Generate GPG key
gpg --full-generate-key

# List keys
gpg --list-secret-keys --keyid-format LONG

# Configure Git to use key
git config --global user.signingkey <key-id>

# Sign commits
git commit -S -m "Signed commit"

# Auto-sign all commits
git config --global commit.gpgsign true

# Sign tags
git tag -s v1.0 -m "Signed tag"

# Verify signature
git verify-commit HEAD
git verify-tag v1.0
```

### Credential Management

```bash
# Store credentials (insecure)
git config --global credential.helper store

# Cache credentials for 1 hour
git config --global credential.helper 'cache --timeout=3600'

# Use OS keychain (macOS)
git config --global credential.helper osxkeychain

# Use OS credential manager (Windows)
git config --global credential.helper wincred

# Use specific helper for specific host
git config --global credential.https://github.com.helper manager
```

---

## Advanced Workflows

### Worktrees (Multiple Working Directories)

```bash
# Create a worktree for hotfix
git worktree add ../hotfix-branch hotfix

# List worktrees
git worktree list

# Work in worktree
cd ../hotfix-branch
# Make changes, commit
git commit -m "Hotfix"

# Return to main repo
cd ../main-repo
git fetch ../hotfix-branch hotfix
git merge hotfix

# Remove worktree
git worktree remove ../hotfix-branch

# Prune deleted worktrees
git worktree prune
```

### Monorepo Strategies

**Sparse Checkout**

```bash
# Initialize sparse checkout
git sparse-checkout init --cone

# Checkout specific directories
git sparse-checkout set apps/frontend libs/shared

# Add more directories
git sparse-checkout add apps/backend

# Disable sparse checkout
git sparse-checkout disable
```

**Git Filter-Branch (Split Monorepo)**

```bash
# Extract subdirectory into new repo
git filter-repo --subdirectory-filter apps/frontend --force

# Push to new repo
git remote add new-origin https://github.com/your/frontend.git
git push -u new-origin main
```

### Patch Workflows

```bash
# Create patch files
git format-patch -1 HEAD      # Last commit
git format-patch HEAD~3       # Last 3 commits
git format-patch main..feature # All commits in feature not in main

# Apply patch
git am < 0001-commit.patch

# Apply patch without committing
git apply --check 0001-commit.patch  # Check if it applies cleanly
git apply 0001-commit.patch

# Create diff
git diff > changes.patch

# Apply diff
patch -p1 < changes.patch
```

---

## Root Cause Analysis

### Debugging: "detached HEAD" State

**Symptoms:**
```
You are in 'detached HEAD' state...
```

**Root Cause:**
- Checked out a commit directly (not a branch)
- Checked out a tag
- Rebased/bisected and didn't finish

**Recovery:**

```bash
# Create a branch from current position
git branch temp-branch

# Or switch to existing branch (lose changes)
git checkout main

# If you made commits in detached HEAD:
git reflog  # Find the commit
git branch recovery <commit-sha>
git checkout recovery
```

### Debugging: "Your branch and origin/main have diverged"

**Symptoms:**
```
Your branch and 'origin/main' have diverged,
and have 3 and 5 different commits each.
```

**Root Cause:**
- You rewrote history (rebase/amend) on a shared branch
- Someone else force-pushed

**Recovery:**

```bash
# Option 1: Merge (preserves both histories)
git pull origin main

# Option 2: Rebase (linear history)
git pull --rebase origin main

# Option 3: Reset (lose local changes)
git reset --hard origin/main

# Option 4: Force push (DANGEROUS)
git push --force-with-lease origin main
```

### Debugging: "fatal: refusing to merge unrelated histories"

**Symptoms:**
```
fatal: refusing to merge unrelated histories
```

**Root Cause:**
- Trying to merge two repos with no common commits
- Merging a freshly initialized repo

**Solution:**

```bash
# Allow unrelated histories
git merge --allow-unrelated-histories origin/main

# Or during pull
git pull origin main --allow-unrelated-histories
```

### Debugging: "error: failed to push some refs"

**Symptoms:**
```
error: failed to push some refs to 'origin'
hint: Updates were rejected because the tip of your current branch is behind
```

**Root Cause:**
- Someone pushed before you
- You amended/rebased a public commit

**Solution:**

```bash
# Pull first
git pull origin main

# If that creates merge commit you don't want:
git pull --rebase origin main

# If you're SURE your version is correct:
git push --force-with-lease origin main  # Safer than --force
```

### Debugging: Large Pack Files

**Symptoms:**
- `git push` or `git clone` times out
- Repository size is huge

**Root Cause:**
- Large files committed to history
- No garbage collection

**Analysis:**

```bash
# Find large files
git rev-list --objects --all |
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' |
  sed -n 's/^blob //p' |
  sort --numeric-sort --key=2 |
  tail -n 10

# Find large packs
git count-objects -v
```

**Solution:**
```bash
# Use BFG or git-filter-repo (see Large File Handling section)
# Or migrate to Git LFS
```

### Debugging: "index.lock exists"

**Symptoms:**
```
fatal: Unable to create '.git/index.lock': File exists.
```

**Root Cause:**
- Previous git operation crashed
- Another git process is running

**Solution:**

```bash
# Check if another git process is running
ps aux | grep git

# If not, remove lock file
rm -f .git/index.lock

# If in submodule:
rm -f .git/modules/<submodule>/index.lock
```

### Debugging: Corrupted Object

**Symptoms:**
```
error: object file .git/objects/ab/cdef... is empty
fatal: loose object abcdef... is corrupt
```

**Root Cause:**
- Disk corruption
- Power failure during git operation
- Filesystem issues

**Recovery:**

```bash
# Try fsck
git fsck --full

# If specific object is corrupt, fetch from remote
git fetch origin

# Copy object from remote
git cat-file -p origin/main:.git/objects/ab/cdef > .git/objects/ab/cdef

# If all else fails, re-clone
cd ..
mv corrupt-repo corrupt-repo.bak
git clone <remote-url> corrupt-repo
# Manually restore uncommitted work from corrupt-repo.bak
```

---

## Quick Reference: Emergency Commands

```bash
# Undo last commit (keep changes)
git reset --soft HEAD^

# Undo last commit (discard changes)
git reset --hard HEAD^

# Undo last push (DANGEROUS)
git push --force-with-lease origin main

# Recover deleted branch
git reflog | grep branch-name
git branch recovered <commit-sha>

# Recover deleted commits
git reflog
git cherry-pick <commit-sha>

# Unstage file
git restore --staged <file>

# Discard local changes
git restore <file>

# Abort merge
git merge --abort

# Abort rebase
git rebase --abort

# Abort cherry-pick
git cherry-pick --abort

# Create branch without switching
git branch new-branch

# Rename current branch
git branch -m new-name

# Delete local branch
git branch -d branch-name

# Force delete local branch
git branch -D branch-name

# Delete remote branch
git push origin --delete branch-name

# Stash with message
git stash push -m "Work in progress"

# Apply stash without removing
git stash apply

# List all stashes
git stash list

# Apply specific stash
git stash apply stash@{2}

# Drop specific stash
git stash drop stash@{2}

# Clear all stashes
git stash clear

# Show what's in a stash
git stash show -p stash@{0}
```

---

## Configuration Best Practices

```bash
# Global gitignore
git config --global core.excludesfile ~/.gitignore_global

# Default branch name
git config --global init.defaultBranch main

# Auto-correct typos
git config --global help.autocorrect 10  # 1 second delay

# Colorful output
git config --global color.ui auto

# Better diff algorithm
git config --global diff.algorithm patience

# Reuse recorded resolution (rerere)
git config --global rerere.enabled true

# Prune on fetch
git config --global fetch.prune true

# Auto-stash on rebase
git config --global rebase.autoStash true

# Push current branch only
git config --global push.default current

# Auto-setup remote tracking
git config --global push.autoSetupRemote true

# Show branch in prompt
git config --global bash.showDirtyState true
```

---

**Last Updated**: 2025-11-10
**Author**: InsightPulseAI DevOps Team
**License**: AGPL-3.0
