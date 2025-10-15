# Copilot Ruleset for Reserve Flow AI 2026 Development

This ruleset is derived from the CodeMachine orchestration platform's procedures and methodologies. It provides guidelines for AI assistants (like GitHub Copilot) to follow when contributing to the development of the Reserve Flow AI 2026 project.

## Core Principles

### 1. Specification-Driven Development

- **Always start with specifications**: Before implementing any feature, create or reference detailed specifications that outline goals, constraints, and requirements.
- **Use structured documentation**: Maintain specifications in markdown format with clear sections for functional requirements, non-functional requirements, and acceptance criteria.
- **Validate against specs**: Every code change must align with the documented specifications.

### 2. Modular Agent-Based Approach

- **Specialize roles**: Treat different development tasks as specialized "agents" with distinct responsibilities:
  - **Architect**: Design system architecture and data flows
  - **Code Generator**: Implement clean, production-ready code
  - **Tester**: Write comprehensive tests
  - **Reviewer**: Validate code quality and adherence to standards
  - **Documenter**: Maintain documentation and comments

### 3. Workflow Orchestration

- **Break down complex tasks**: Decompose large features into sequential, manageable steps with clear dependencies.
- **Enable parallel execution**: Identify independent tasks that can be developed concurrently to accelerate progress.
- **Track progress**: Maintain visibility into task status, marking steps as completed only after validation.

### 4. Quality Assurance

- **Implement rigorous validation**: Each step must include automated tests, linting, and type checking.
- **Handle failures gracefully**: Design fallback mechanisms for error scenarios and edge cases.
- **Ensure reliability**: Aim for high uptime, security compliance, and performance standards.

### 5. Persistent Context and Memory

- **Maintain project context**: Reference existing codebase patterns, configurations, and conventions.
- **Use version control effectively**: Commit changes frequently with descriptive messages.
- **Document decisions**: Record rationale for architectural choices and implementation details.

## Development Guidelines

### Code Implementation

- Follow the project's existing code structure and naming conventions.
- Implement features incrementally, ensuring each addition is fully functional.
- Prioritize clean, readable code with comprehensive comments.
- Use type safety (TypeScript) and follow established patterns.

### Testing Strategy

- Write unit tests for all new functions and components.
- Include integration tests for API endpoints and user interactions.
- Cover edge cases and error scenarios.
- Run tests automatically as part of the development workflow.

### Documentation

- Update README and technical docs for any new features.
- Maintain API documentation for backend endpoints.
- Document configuration changes and deployment procedures.

### Security and Compliance

- Implement proper authentication and authorization.
- Ensure data encryption and secure communication.
- Follow GDPR and other relevant compliance standards.

## Workflow Execution

### Sequential Tasks

For tasks with dependencies:

1. Plan the sequence of steps
2. Execute each step in order
3. Validate output before proceeding
4. Document completion

### Parallel Tasks

For independent tasks:

1. Identify parallelizable components
2. Execute simultaneously where possible
3. Synchronize at integration points
4. Validate combined results

### Error Handling

- Detect failures early
- Implement fallback strategies
- Log errors with context
- Resume from last successful state

## Validation Gates

- **Build**: Ensure code compiles without errors
- **Lint/Typecheck**: Pass all static analysis
- **Tests**: All tests pass with good coverage
- **Integration**: Components work together correctly
- **Deployment**: Ready for production deployment

This ruleset ensures that development follows CodeMachine's proven orchestration patterns, leading to high-quality, maintainable code for the Reserve Flow AI 2026 project.
