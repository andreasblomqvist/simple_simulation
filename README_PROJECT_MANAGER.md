# Project and Quality Manager Agent

## 🚀 Quick Start

The Project and Quality Manager (PM/QM) agent is a comprehensive system designed to oversee project execution, maintain quality standards, and ensure architectural consistency.

### Activate the Agent
```bash
# Quick status check
./scripts/activate-project-manager.sh

# Detailed dashboard
python3 scripts/project-dashboard.py
```

## 📋 What You Get

### 1. **Project Management**
- ✅ Task tracking and completion monitoring
- ✅ Progress reporting and milestone tracking
- ✅ Risk assessment and mitigation
- ✅ Resource coordination and timeline management

### 2. **Quality Assurance**
- ✅ Code review and architecture compliance
- ✅ Testing oversight and coverage monitoring
- ✅ Documentation standards enforcement
- ✅ Performance monitoring and optimization

### 3. **Process Management**
- ✅ Development workflow enforcement
- ✅ Git operations and version control
- ✅ Server health monitoring
- ✅ Integration testing oversight

## 🛠️ Components

### Cursor Rule (`cursor_rules/project-quality-manager.mdc`)
The core behavior definition that guides AI interactions:
- **Project Management**: Task tracking, progress reporting, resource coordination
- **Quality Assurance**: Code review, architecture compliance, testing oversight
- **Process Management**: Development workflow, git operations, server management

### Activation Script (`scripts/activate-project-manager.sh`)
Quick bash script for initial project assessment:
- Server health checks
- Git status monitoring
- Task file analysis
- System resource monitoring
- PM/QM recommendations

### Dashboard (`scripts/project-dashboard.py`)
Comprehensive Python dashboard with detailed metrics:
- Real-time server health monitoring
- Git activity and commit tracking
- Task completion analysis
- Code quality metrics
- System resource monitoring
- Automated recommendations

## 📊 Current Project Status

Based on the latest dashboard run:

### ✅ **Healthy Systems**
- **Backend Server**: Running and healthy (port 8000)
- **Frontend Server**: Running (port 3000)
- **Git Repository**: Active with recent commits
- **Task Management**: 22.1% overall completion (64/289 tasks)

### 📈 **Project Metrics**
- **Python Files**: 341
- **TypeScript Files**: 14,646
- **Test Files**: 283
- **Documentation**: 817 markdown files
- **Configuration**: 915 files

### ⚠️ **Action Items**
1. **Commit pending changes** (521+ files modified)
2. **Review task status** and update completion
3. **Monitor task completion rates** by file

## 🎯 How to Use

### Daily Development Workflow
```bash
# 1. Start your day with PM/QM check
./scripts/activate-project-manager.sh

# 2. Review detailed status
python3 scripts/project-dashboard.py

# 3. Check specific task files
find . -name "tasks-*.md" -exec cat {} \;

# 4. Begin development with PM/QM oversight
```

### Quality Review Session
```bash
# 1. Run comprehensive quality check
python3 scripts/project-dashboard.py

# 2. Review code quality metrics
# 3. Check test coverage
# 4. Validate architecture compliance
# 5. Update documentation as needed
```

### Risk Assessment
```bash
# 1. Review current project status
# 2. Identify potential risks
# 3. Assess impact and probability
# 4. Develop mitigation strategies
# 5. Update risk register
```

## 📋 Task Management Protocol

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

## 🔍 Quality Standards

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

## 📈 Status Reporting

### Standard Report Format
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

## 🚨 Emergency Procedures

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

## 🎯 Success Metrics

### Project Success Indicators
- **On-Time Delivery**: 90% of tasks completed by deadline
- **Quality Score**: 95% of code changes pass quality review
- **User Satisfaction**: No critical bugs in production
- **Performance**: Response times within acceptable limits
- **Documentation**: 100% of features documented

### Current Performance
- **Task Completion**: 22.1% (64/289 tasks)
- **Server Health**: ✅ Both servers running
- **Code Quality**: ✅ Architecture compliance maintained
- **Documentation**: ✅ Comprehensive documentation available

## 🔧 Troubleshooting

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
- Review the documentation in `docs/PROJECT_QUALITY_MANAGER.md`
- Check the cursor rules for specific guidance
- Run the dashboard script for current status
- Consult the architecture documentation

## 📚 Documentation

### Key Documents
- **Main Documentation**: `docs/PROJECT_QUALITY_MANAGER.md`
- **Cursor Rule**: `cursor_rules/project-quality-manager.mdc`
- **Architecture**: `docs/ARCHITECTURE.md`
- **API Documentation**: Backend and frontend docs

### Scripts
- **Activation**: `scripts/activate-project-manager.sh`
- **Dashboard**: `scripts/project-dashboard.py`
- **Server Management**: `scripts/restart-servers.sh`

## 🎉 Conclusion

The Project and Quality Manager agent provides comprehensive oversight for the SimpleSim project, ensuring consistent quality, proper task management, and effective risk mitigation. 

**Ready to manage your project with professional oversight! 🚀**

For questions or issues, refer to the documentation or run the dashboard script for current project status. 