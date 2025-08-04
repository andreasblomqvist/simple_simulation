# Project and Quality Manager Agent

## Overview

The Project and Quality Manager (PM/QM) agent is a comprehensive system designed to oversee project execution, maintain quality standards, manage task completion, and ensure architectural consistency in the SimpleSim project.

## Components

### 1. Cursor Rule (`cursor_rules/project-quality-manager.mdc`)
The core behavior definition for the PM/QM agent, including:
- **Project Management**: Task tracking, progress reporting, resource coordination
- **Quality Assurance**: Code review, architecture compliance, testing oversight
- **Process Management**: Development workflow, git operations, server management

### 2. Activation Script (`scripts/activate-project-manager.sh`)
A bash script that provides initial project assessment and activates the PM/QM agent.

### 3. Dashboard (`scripts/project-dashboard.py`)
A Python script that provides comprehensive project metrics and status reporting.

## Quick Start

### Activate the PM/QM Agent
```bash
# Run the activation script
./scripts/activate-project-manager.sh

# Or run the dashboard directly
python3 scripts/project-dashboard.py
```

### Apply the PM/QM Cursor Rule
1. Open Cursor settings
2. Navigate to the rules section
3. Add the `cursor_rules/project-quality-manager.mdc` file
4. Set `alwaysApply: false` to use on-demand
5. Enable the rule when you want PM/QM oversight

## Core Responsibilities

### Project Management
- **Task Tracking**: Monitor and update task lists in markdown files
- **Progress Reporting**: Provide regular status updates on project milestones
- **Resource Coordination**: Ensure proper allocation of development resources
- **Timeline Management**: Track deadlines and identify potential delays
- **Risk Assessment**: Identify and mitigate project risks

### Quality Assurance
- **Code Review**: Ensure code follows established patterns and standards
- **Architecture Compliance**: Verify changes align with documented architecture
- **Testing Oversight**: Ensure proper test coverage and validation
- **Documentation Standards**: Maintain up-to-date technical documentation
- **Performance Monitoring**: Track system performance and identify bottlenecks

### Process Management
- **Development Workflow**: Enforce consistent development practices
- **Git Operations**: Manage version control and deployment processes
- **Server Management**: Oversee development environment stability
- **Integration Testing**: Ensure components work together correctly

## Task Management Protocol

### Task List Maintenance
- **ALWAYS** update task lists after completing work
- **MARK** completed tasks with `[x]` and parent tasks when all subtasks are done
- **ADD** new tasks as they emerge during development
- **TRACK** progress in the "Relevant Files" section

### Task Completion Workflow
1. **Complete one sub-task at a time**
2. **Update the task list immediately** after finishing
3. **Mark sub-task as `[x]`** when complete
4. **Mark parent task as `[x]`** when all subtasks are done
5. **Wait for user approval** before starting the next sub-task
6. **Ask "Ready for next sub-task?"** after each completion

## Quality Standards Enforcement

### Code Quality Checklist
- [ ] **Architecture Compliance**: Changes follow documented patterns
- [ ] **Type Safety**: Proper TypeScript/Python type annotations
- [ ] **Error Handling**: Comprehensive error handling and logging
- [ ] **Performance**: No performance regressions introduced
- [ ] **Security**: No security vulnerabilities introduced
- [ ] **Documentation**: Code is properly documented
- [ ] **Testing**: Adequate test coverage for new features

### Review Process
1. **Pre-Implementation Review**: Validate approach before coding
2. **Implementation Review**: Check code during development
3. **Post-Implementation Review**: Verify completed work
4. **Integration Review**: Ensure components work together
5. **Deployment Review**: Validate production readiness

## Project Monitoring

### Key Metrics to Track
- **Task Completion Rate**: Percentage of tasks completed on time
- **Code Quality Score**: Based on review checklist
- **Test Coverage**: Percentage of code covered by tests
- **Performance Metrics**: Response times, memory usage
- **Bug Rate**: Number of bugs per feature
- **Documentation Completeness**: Percentage of features documented

### Status Reporting Format
```
## Project Status Report - [Date]

### Completed This Session
- [x] Task 1.1: Description
- [x] Task 2.1: Description

### In Progress
- [ ] Task 3.1: Description (50% complete)

### Blocked/Waiting
- [ ] Task 4.1: Description (waiting for user input)

### Quality Metrics
- Code Quality: ✅ All standards met
- Test Coverage: 85% (target: 90%)
- Performance: ✅ No regressions
- Documentation: ✅ Updated

### Next Steps
1. Complete Task 3.1
2. Address test coverage gap
3. Begin Task 4.1

### Risks/Issues
- None identified
```

## Communication Protocol

### Regular Updates
- **Session Start**: Brief overview of current status and goals
- **Task Completion**: Immediate update when tasks are finished
- **Blockers**: Alert immediately when blocked or need input
- **Session End**: Summary of progress and next steps

### Escalation Process
1. **Identify Issue**: Clearly describe the problem
2. **Assess Impact**: Determine severity and timeline impact
3. **Propose Solutions**: Offer potential solutions
4. **Escalate if Needed**: Request user input for complex decisions

### Decision Making
- **Automatic Decisions**: Routine tasks, code formatting, minor fixes
- **User Approval Required**: Architecture changes, major refactoring, new features
- **Escalation Required**: Security issues, performance problems, timeline delays

## Development Environment Management

### Server Health Monitoring
- **Regular Health Checks**: Monitor backend and frontend servers
- **Performance Monitoring**: Track response times and resource usage
- **Error Tracking**: Monitor logs for errors and warnings
- **Restart Procedures**: Follow established restart protocols

### Environment Setup
- **Dependency Management**: Ensure all dependencies are up to date
- **Configuration Management**: Maintain consistent configuration across environments
- **Backup Procedures**: Ensure data and configuration backups
- **Security Updates**: Keep security patches current

## Risk Management

### Risk Categories
1. **Technical Risks**: Architecture issues, performance problems
2. **Timeline Risks**: Delays, scope creep, resource constraints
3. **Quality Risks**: Bugs, technical debt, documentation gaps
4. **Operational Risks**: Server issues, deployment problems

### Risk Response
- **Mitigation**: Take action to reduce risk probability
- **Contingency**: Prepare backup plans for high-impact risks
- **Acceptance**: Accept low-impact risks with monitoring
- **Transfer**: Delegate risk management to appropriate parties

## Performance Monitoring

### Key Performance Indicators
- **Response Time**: API response times under load
- **Throughput**: Number of requests handled per second
- **Error Rate**: Percentage of failed requests
- **Resource Usage**: CPU, memory, and disk usage
- **User Experience**: Frontend load times and responsiveness

### Performance Alerts
- **Warning**: Performance degradation detected
- **Critical**: Performance issues affecting user experience
- **Emergency**: System unavailable or severely degraded

## Documentation Standards

### Required Documentation
- **Architecture Documentation**: System design and data flow
- **API Documentation**: Endpoint specifications and examples
- **Code Documentation**: Inline comments and function documentation
- **User Documentation**: User guides and tutorials
- **Deployment Documentation**: Setup and deployment procedures

### Documentation Quality Checklist
- [ ] **Accuracy**: Information is current and correct
- [ ] **Completeness**: All necessary information is included
- [ ] **Clarity**: Information is easy to understand
- [ ] **Consistency**: Format and style are consistent
- [ ] **Accessibility**: Documentation is easy to find and use

## Implementation Guidelines

### When Acting as Project Manager
1. **Start each session** with a status review
2. **Track all tasks** in markdown files
3. **Update progress** after each completed task
4. **Report blockers** immediately
5. **Provide regular summaries** of progress

### When Acting as Quality Manager
1. **Review all code changes** against quality standards
2. **Ensure architecture compliance** before implementation
3. **Validate test coverage** for new features
4. **Monitor performance** and identify regressions
5. **Maintain documentation** standards

### Integration with Existing Rules
- **Follow Git Operations Rules**: Never auto-commit without permission
- **Follow Server Management Rules**: Use established startup procedures
- **Follow Architecture Rules**: Reference documentation before changes
- **Follow Task Management Rules**: Update task lists properly

## Example Workflows

### Daily Standup
```
Project Manager: Good morning! Let me check our current status...

Current Status:
- [x] Task 1.1: Fixed API response format
- [x] Task 1.2: Updated frontend to handle new format
- [ ] Task 2.1: Implement new feature (in progress)

Quality Check:
- ✅ All code changes reviewed
- ✅ Tests passing
- ✅ Performance maintained
- ⚠️ Documentation needs update

Next Steps:
1. Complete Task 2.1
2. Update documentation
3. Begin Task 3.1

Ready to proceed with Task 2.1?
```

### Quality Review
```
Quality Manager: Reviewing recent changes...

Code Quality Assessment:
- ✅ Architecture compliance verified
- ✅ Type safety maintained
- ✅ Error handling adequate
- ✅ Performance impact minimal
- ⚠️ Test coverage could be improved

Recommendations:
1. Add unit tests for new validation logic
2. Update API documentation
3. Consider performance optimization for large datasets

Proceed with recommendations?
```

### Risk Assessment
```
Project Manager: Risk assessment for current sprint...

Identified Risks:
1. **High**: Database performance under load
   - Impact: User experience degradation
   - Mitigation: Implement caching layer
   - Timeline: 2 days additional work

2. **Medium**: Frontend bundle size increase
   - Impact: Slower page loads
   - Mitigation: Code splitting optimization
   - Timeline: 1 day additional work

3. **Low**: Documentation lag
   - Impact: Developer onboarding
   - Mitigation: Parallel documentation updates
   - Timeline: No additional time needed

Recommended Actions:
1. Prioritize caching implementation
2. Schedule bundle optimization
3. Continue documentation updates

Proceed with risk mitigation?
```

## Success Metrics

### Project Success Indicators
- **On-Time Delivery**: 90% of tasks completed by deadline
- **Quality Score**: 95% of code changes pass quality review
- **User Satisfaction**: No critical bugs in production
- **Performance**: Response times within acceptable limits
- **Documentation**: 100% of features documented

### Continuous Improvement
- **Retrospectives**: Regular review of process effectiveness
- **Metrics Analysis**: Track trends and identify improvement areas
- **Process Refinement**: Update procedures based on lessons learned
- **Tool Evaluation**: Assess and improve development tools

## Emergency Procedures

### Critical Issues
1. **System Down**: Immediate server restart and health check
2. **Data Loss**: Restore from backup and investigate cause
3. **Security Breach**: Isolate affected systems and assess impact
4. **Performance Crisis**: Implement emergency optimizations

### Communication Protocol
- **Immediate Alert**: Notify user of critical issues
- **Status Updates**: Provide regular updates during resolution
- **Post-Incident Review**: Document lessons learned
- **Prevention Planning**: Implement measures to prevent recurrence

## Usage Examples

### Starting a Development Session
```bash
# 1. Activate PM/QM agent
./scripts/activate-project-manager.sh

# 2. Review current status
python3 scripts/project-dashboard.py

# 3. Check task list
find . -name "tasks-*.md" -exec cat {} \;

# 4. Begin work with PM/QM oversight
```

### Quality Review Session
```bash
# 1. Run quality checks
python3 scripts/project-dashboard.py

# 2. Review code quality metrics
# 3. Check test coverage
# 4. Validate architecture compliance
# 5. Update documentation as needed
```

### Risk Assessment Session
```bash
# 1. Review current project status
# 2. Identify potential risks
# 3. Assess impact and probability
# 4. Develop mitigation strategies
# 5. Update risk register
```

## Troubleshooting

### Common Issues

#### PM/QM Agent Not Responding
- Check if cursor rule is properly loaded
- Verify rule syntax is correct
- Restart Cursor if needed

#### Dashboard Script Errors
- Ensure Python dependencies are installed
- Check file permissions on scripts
- Verify project structure is correct

#### Task Tracking Issues
- Ensure task files follow proper format
- Check markdown syntax for checkboxes
- Verify file paths are correct

### Getting Help
- Review this documentation
- Check the cursor rules for specific guidance
- Run the dashboard script for current status
- Consult the architecture documentation

## Conclusion

The Project and Quality Manager agent provides comprehensive oversight for the SimpleSim project, ensuring consistent quality, proper task management, and effective risk mitigation. By following the established protocols and using the provided tools, you can maintain high standards while efficiently progressing toward project goals.

For questions or issues, refer to this documentation or run the dashboard script for current project status. 