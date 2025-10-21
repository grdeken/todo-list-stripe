# Git Version Control Guide

## Repository Setup

Your project is now under Git version control!

### Branch: `main`
- Initial commit: `10aa7d8`
- 77 files tracked
- 10,238+ lines of code

## Protected Files (Not Committed)

The following sensitive files are **automatically excluded** from version control:

### Environment Files
- `.env` - Contains Stripe API keys and secrets
- `.env.local`
- `.env.production`

### Database Files
- `todos.db` - Active database (regenerated from migrations)
- `*.sqlite3`

### Test Scripts
- `test_*.py` - Temporary test scripts
- `check_*.py` - Helper scripts
- `setup_stripe_product.py` - One-time setup script

### Other
- `node_modules/` - NPM dependencies
- `__pycache__/` - Python cache
- `.vscode/`, `.idea/` - IDE settings
- `backend/`, `backend_env/` - Old/deprecated directories

## What IS Committed

### Safe to commit:
- `.env.example` - Template without secrets
- `todos.db.backup` - Database backups (for reference)
- All source code
- Configuration files (without secrets)
- Documentation
- Alembic migrations

## Common Git Commands

### Check status
```bash
git status
```

### View changes
```bash
git diff
```

### Stage changes
```bash
git add .                    # Stage all changes
git add specific_file.py     # Stage specific file
```

### Commit changes
```bash
git commit -m "Your commit message"
```

### View history
```bash
git log                      # Full history
git log --oneline            # Compact view
git log --graph --oneline    # Visual branch history
```

### Create a new branch
```bash
git checkout -b feature-name
```

### Switch branches
```bash
git checkout main
git checkout feature-name
```

### Undo changes (before commit)
```bash
git restore filename         # Discard changes to a file
git restore .               # Discard all changes
```

## Best Practices

1. **Commit Often**: Make small, focused commits
2. **Write Clear Messages**: Describe what and why, not how
3. **Never Commit Secrets**: The .gitignore protects you, but double-check
4. **Test Before Committing**: Ensure code works
5. **Use Branches**: Create feature branches for new work

## Emergency: Accidentally Committed Secrets

If you accidentally commit `.env` or other secrets:

```bash
# Remove from staging (before commit)
git restore --staged .env

# Remove from last commit (after commit)
git reset --soft HEAD~1  # Undo last commit, keep changes
git restore --staged .env
git commit -m "Your message"

# If already pushed to remote
# IMPORTANT: Rotate all exposed API keys immediately!
# Then force push (use with caution)
git push --force
```

## Remote Repository Setup (Future)

When you're ready to push to GitHub/GitLab:

```bash
# Add remote
git remote add origin <repository-url>

# Push to remote
git push -u origin main
```

## Alembic Migration Workflow

When making database changes:

```bash
# 1. Modify models in src/api_service/models/
# 2. Generate migration
python3 -m alembic revision --autogenerate -m "description"

# 3. Review migration file in alembic/versions/
# 4. Apply migration
python3 -m alembic upgrade head

# 5. Commit migration
git add alembic/versions/*.py
git commit -m "Add migration: description"
```

## Current Repository Structure

```
/Users/grant/Desktop/test/
├── .git/                   # Git repository data
├── .gitignore             # Root ignore rules
├── fastapi-backend/       # Backend API
│   ├── .gitignore        # Backend-specific rules
│   ├── .env              # ❌ NOT COMMITTED (secrets)
│   ├── .env.example      # ✅ Committed (template)
│   ├── alembic/          # Database migrations
│   ├── src/              # Source code
│   └── requirements.txt  # Python dependencies
├── todo-app/             # Frontend React app
│   ├── .gitignore        # Frontend-specific rules
│   ├── .env              # ❌ NOT COMMITTED (secrets)
│   ├── src/              # React components
│   └── package.json      # NPM dependencies
└── *.md                  # Documentation files
```

## Security Reminder

**CRITICAL**: Never commit files containing:
- API keys (Stripe, etc.)
- Database passwords
- JWT secrets
- Any credentials or tokens

The `.gitignore` files protect you, but always verify before pushing!
