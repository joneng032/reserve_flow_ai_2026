# Contributing to Reserve Flow AI 2026

Thank you for your interest in contributing to the Reserve Flow AI 2026 project! This project follows a structured development approach inspired by the CodeMachine orchestration platform, ensuring high-quality, specification-driven development.

## Development Philosophy

Our development process is guided by the principles outlined in `COPILOT_RULES.md` and leverages the CodeMachine virtual assistant software located in the `.codemachine/` folder. We emphasize:

- **Specification-first development**: All features start with detailed specifications
- **Multi-agent collaboration**: Breaking down tasks into specialized roles
- **Orchestrated workflows**: Systematic execution of development steps
- **Quality assurance**: Rigorous testing and validation at each step

## Getting Started

### Prerequisites

- Node.js and npm (for frontend development)
- Python 3.8+ (for backend development)
- Git for version control
- Familiarity with the CodeMachine CLI (see `.codemachine/README.md`)

### Setup

1. Fork the repository and clone your fork
2. Install dependencies:

   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

3. Set up development environment using the provided scripts:

   ```bash
   # Windows
   .\setup-dev.ps1
   .\start-dev.ps1

   # Or Linux/Mac
   ./setup-dev.sh
   ./start-dev.sh
   ```

## Development Workflow

### 1. Create Specifications

Before implementing any feature, create detailed specifications:

1. Navigate to `.codemachine/inputs/specifications.md`
2. Add your feature requirements following the format:

   ```markdown
   # Feature: [Feature Name]

   ## Goals
   - [Goal 1]
   - [Goal 2]

   ## Constraints
   - [Constraint 1]

   ## Functional Requirements
   - [FR-001]: [Description]

   ## Non-Functional Requirements
   - [NFR-001]: [Description]
   ```

### 2. Use CodeMachine Orchestration

Leverage the CodeMachine platform to generate implementation:

1. Ensure CodeMachine is installed: `npm install -g codemachine`
2. Authenticate with your preferred AI engine (Claude, Codex, etc.)
3. Run the orchestration:

   ```bash
   cd .codemachine
   codemachine
   ```

4. Follow the `/start` command to begin workflow execution

### 3. Implement Features

Following CodeMachine's guidance:

- **Architect**: Design system components and data flows
- **Code Generator**: Implement clean, production-ready code
- **Tester**: Write comprehensive tests
- **Reviewer**: Validate code quality

### 4. Quality Gates

Ensure all changes pass our quality requirements:

- **Build**: Code compiles without errors
- **Lint/Typecheck**: Passes static analysis
- **Tests**: All tests pass with good coverage
- **Integration**: Components work together correctly

## Code Standards

### Backend (Python/FastAPI)

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings
- Maintain test coverage above 80%

### Frontend (React/TypeScript)

- Use TypeScript for all new code
- Follow the existing component patterns
- Implement proper error boundaries
- Ensure accessibility compliance

### General

- Write clear, descriptive commit messages
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
# Run full test suite
pytest tests/
npm run test --prefix frontend
```

## Pull Request Process

1. **Create a Branch**: Use descriptive branch names (e.g., `feature/user-authentication`)
2. **Make Changes**: Follow the workflow above
3. **Run Tests**: Ensure all tests pass
4. **Update Documentation**: Modify relevant docs if needed
5. **Create PR**: Use the PR template and reference specifications
6. **Code Review**: Address reviewer feedback
7. **Merge**: Squash merge with descriptive commit message

## Issue Reporting

When reporting issues, please:

- Use the issue template
- Reference relevant specifications
- Include steps to reproduce
- Provide environment details
- Attach relevant logs or screenshots

## Communication

- Use GitHub issues for bug reports and feature requests
- Join discussions in pull request comments
- Follow the CodeMachine procedures for complex changes

## Recognition

Contributors will be recognized in the project README and release notes. Significant contributions may be acknowledged in the `.codemachine/` case studies.

Thank you for contributing to Reserve Flow AI 2026! Your efforts help build a robust, AI-driven platform for reserve flow management.
