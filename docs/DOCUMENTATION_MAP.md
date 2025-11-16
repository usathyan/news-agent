# Documentation Map

A guide to all documentation in the news-agent project.

## Quick Navigation

### For Users
- **README.md** - Start here! Installation, quick start, usage examples, CLI reference
- **config.toml** - Configuration options and defaults

### For Developers
- **docs/DEVELOPER_GUIDE.md** - Complete architecture, system design, code organization
- **docs/LANGSMITH_IMPLEMENTATION.md** - Telemetry implementation details and debugging

### For DevOps/Infrastructure
- **Makefile** - Build targets, installation, testing, formatting
- **.env.example** - Environment variables template

---

## Document Details

### README.md (Overview & Usage)
**Purpose**: First point of contact for users
**Contents**:
- Features overview
- Quick start guide
- Installation instructions
- Configuration reference
- CLI usage and examples
- Telemetry & observability setup
- Development guidelines
- Troubleshooting
- Project structure

**Key Sections**:
- ✅ Installation
- ✅ Quick Start
- ✅ Configuration
- ✅ Telemetry & Observability (Enhanced)
- ✅ CLI Reference
- ✅ Development

**Read if**:
- You're new to the project
- You want to run the agent
- You want to configure settings
- You want to see example output

---

### docs/DEVELOPER_GUIDE.md (Architecture & Implementation)
**Purpose**: Complete technical reference for developers
**Size**: ~25KB, 700+ lines
**Contents**:
1. **Architecture Overview** - High-level system design
2. **System Design** - Component interaction diagrams
3. **Code Organization** - File structure and organization
4. **Execution Flow** - Main pipeline and detailed flows
5. **LangSmith Implementation** - Telemetry setup
6. **Tracing in Detail** - Trace hierarchy and content
7. **Key Components** - NewsAgent, LLMProvider, Data Clients, Scorers
8. **Data Flow** - GitHub, HN, Analysis flows
9. **Development Patterns** - TDD, error handling, telemetry patterns
10. **Contributing Guidelines** - Code review and commit standards

**Includes**:
- 15+ Mermaid diagrams
- Code examples
- Sequence diagrams
- File-by-purpose reference table
- Performance considerations
- Quick reference guides

**Read if**:
- You want to understand the system design
- You're implementing new features
- You want to understand execution flow
- You need to debug issues
- You're reviewing code

---

### docs/LANGSMITH_IMPLEMENTATION.md (Telemetry Deep Dive)
**Purpose**: Complete guide to LangSmith integration
**Size**: ~16KB, 500+ lines
**Contents**:
1. **Overview** - Why LangSmith, quick start
2. **Implementation Details** - File changes, code locations
3. **Trace Architecture** - Hierarchy, levels, structure
4. **How It Works** - Step-by-step execution with tracing
5. **Viewing Traces** - Dashboard navigation, examples
6. **Implementation Journey** - Problem, investigation, solution
7. **Debugging Guide** - Troubleshooting checklist
8. **Performance Impact** - Overhead analysis
9. **Advanced Usage** - Custom metadata, manual traces
10. **Best Practices** - Naming, error context, security

**Includes**:
- Sequence diagrams
- Trace hierarchy visualizations
- Dashboard navigation screenshots descriptions
- Example trace content (JSON)
- Debugging checklist
- Performance benchmarks
- Before/after comparison

**Read if**:
- Traces not appearing
- You want to understand telemetry
- You're debugging LLM behavior
- You want to monitor costs
- You're integrating with LangSmith

---

### config.toml (Configuration)
**Purpose**: User-facing configuration file
**Contents**:
- LLM provider settings
- Analysis depth configuration
- Data source settings
- Ranking strategies
- Caching configuration
- Output settings
- Retry behavior
- Telemetry settings

**Read if**:
- You want to change LLM provider
- You want to adjust analysis depth
- You want to enable/disable sources
- You want to configure caching
- You want to change ranking strategy

---

### .env.example (Environment Template)
**Purpose**: Template for environment variables
**Contents**:
- API keys templates
- LangSmith configuration
- Optional service keys

**Read if**:
- You're setting up for the first time
- You need to configure a new API
- You want to enable/disable services

---

### docs/plans/ (Architecture Documents)
**Purpose**: Design and implementation planning documents
**Contents**:
- Design decisions
- Implementation phases
- Architecture evolution

**Read if**:
- You want historical context
- You're evaluating design decisions
- You're planning major changes

---

## Reading Recommendations by Role

### New Developer (First Time)
1. **README.md** - Understand what the project does
2. **docs/DEVELOPER_GUIDE.md** - Understand architecture
3. **src/news_agent/cli.py** - Start reading code
4. **src/news_agent/agent/react_agent.py** - Main orchestration
5. **src/news_agent/llm/provider.py** - LLM integration

**Time**: ~2-3 hours

---

### Feature Developer
1. **docs/DEVELOPER_GUIDE.md** - Code organization section
2. **docs/DEVELOPER_GUIDE.md** - Key Components section
3. **Specific source files** - For your feature area
4. **tests/unit/** - Look at existing tests
5. **Contributing Guidelines** - Before submitting PR

**Time**: 1-2 hours + implementation time

---

### Telemetry/DevOps Engineer
1. **README.md** - Telemetry section
2. **docs/LANGSMITH_IMPLEMENTATION.md** - Complete guide
3. **src/news_agent/cli.py** - How telemetry is enabled
4. **src/news_agent/agent/react_agent.py** - @traceable decorators
5. **test_langsmith_tracing.py** - Simple example

**Time**: 1-2 hours

---

### DevOps/Infrastructure
1. **Makefile** - Build and deployment targets
2. **docker-compose.yml** - If provided
3. **.env.example** - Environment setup
4. **README.md** - Installation section

**Time**: 30 minutes

---

### Code Reviewer
1. **Contributing Guidelines** - In DEVELOPER_GUIDE.md
2. **src/** - The specific files being changed
3. **tests/** - Related tests
4. **Commit message** - Should follow conventions

**Time**: Varies by PR size

---

### Debugger (Something's Broken)
1. **README.md** - Troubleshooting section
2. **docs/LANGSMITH_IMPLEMENTATION.md** - If trace-related
3. **docs/DEVELOPER_GUIDE.md** - Execution flow section
4. **src/** - Trace through code execution

**Time**: 1-3 hours depending on issue

---

## Documentation Statistics

```
Total Documentation: ~5,100 lines
├── README.md: ~410 lines
├── DEVELOPER_GUIDE.md: ~700 lines
└── LANGSMITH_IMPLEMENTATION.md: ~500 lines

Visual Elements:
- 15+ Mermaid diagrams
- Multiple sequence diagrams
- Timeline visualizations
- Code examples throughout

Code Examples: 30+
Tables/References: 15+
Sections: 50+
```

---

## How to Update Documentation

### When Adding Features
1. Update README.md if user-facing
2. Add to DEVELOPER_GUIDE.md (Architecture)
3. Update code comments
4. Document configuration changes

### When Changing Architecture
1. Update system design section in DEVELOPER_GUIDE.md
2. Update Mermaid diagrams
3. Update code organization section
4. Update file-by-purpose reference table

### When Implementing Telemetry
1. Update LANGSMITH_IMPLEMENTATION.md
2. Add trace decorator to code
3. Update README.md telemetry section if user-facing
4. Document in code comments

### When Fixing Bugs
1. Add to troubleshooting section
2. Document root cause in code comments
3. Update relevant guide if pattern-related

---

## Accessing Documentation

### Online
- GitHub repository: `docs/`
- README.md: Repository root

### Locally
```bash
# View README
cat README.md

# View guides
cat docs/DEVELOPER_GUIDE.md
cat docs/LANGSMITH_IMPLEMENTATION.md
```

### Via Make Target
```bash
# Open docs in editor (if configured)
make docs
```

---

## Contributing to Documentation

### Style Guide
- Use markdown for all documents
- Use Mermaid for diagrams
- Include code examples
- Keep sections focused
- Use clear headings
- Add quick reference sections

### Review Checklist
- [ ] Grammar and spelling correct
- [ ] Code examples tested
- [ ] Diagrams render correctly
- [ ] Links work
- [ ] Tone matches rest of docs
- [ ] Cross-references accurate

---

## Document Maintenance

### Regular Updates
- README.md: Update when features change
- DEVELOPER_GUIDE.md: Update when architecture changes
- LANGSMITH_IMPLEMENTATION.md: Update when telemetry changes

### Annual Review
- Check all links
- Verify code examples still work
- Review for outdated information
- Update statistics

---

**Last Updated**: November 16, 2025
**Maintenance**: Active
**Status**: Complete and comprehensive
