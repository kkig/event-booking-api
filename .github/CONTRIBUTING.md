# Contributing Guidelines

Thank you for contributing! Please follow the guidelines below to ensure smooth collaboration.

## 🏷️ Branch Naming

Use the format:
`<type>/<short-description>`

**Examples:**

- `feature/add-login-endpoint`
- `bugfix/fix-timezone-bug`
- `chore/upgrade-dependencies`
- `docs/update-readme`

Branch names should be lowercase and use dashes `-` as separators.

## ✍️ Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard:
`<type>(optional-scope): short description`

**Valid types:**

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Code style (formatting, missing semi colons, etc)
- `refactor`: Code refactoring without feature or bug changes
- `test`: Adding or correcting tests
- `chore`: Maintenance tasks (build, deps)

**Examples:**

- `feat(accounts): add user registration`
- `fix(events): correct date filter logic`
- `refactor: clean up serializer logic`

## ✅ PR Requirements

- Reference relevant issues with `Closes #123` or `Fixes #456`.
- Add or update tests when needed.
- Ensure all checks pass locally (`make test`, `make format`, etc.).
