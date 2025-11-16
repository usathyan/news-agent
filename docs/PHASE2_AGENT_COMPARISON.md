# Phase 2: Agent Framework Comparison
## LangChain Deep Agents vs Claude Agent SDK

**Date:** November 16, 2025
**Status:** Architecture Decision - Needs Selection

---

## Executive Summary

You're at a critical decision point for Phase 2 implementation. Your current news-agent is built on a **manual ReACT pattern** with a custom Tool Registry. You can migrate to either:

1. **Claude Agent SDK** (Anthropic's official SDK)
2. **LangChain Deep Agents** (LangGraph-based planning framework)

Both are valid. This document compares them against your specific use case.

---

## Your Current State

### Architecture
- **Pattern:** Manual ReACT (Reasoning + Acting)
- **Orchestration:** Custom control flow in react_agent.py
- **Tools:** Tool Registry pattern (dict of callables)
- **LLM:** LiteLLM abstraction (multi-provider support)
- **Observability:** LangSmith tracing
- **Scope:** News aggregation with fixed workflow

### Phase 2 Ambitions
- MCP integration (GitHub, Hacker News)
- Additional data sources (Reddit, X.com)
- Scheduling and automation
- Email delivery
- Optional: Web dashboard

---

## Deep Dive: LangChain Deep Agents

### What It Is
Built on **LangGraph** (state machine framework), Deep Agents provides:
- **Planning/decomposition** via built-in `write_todos` tool
- **Context management** via file system (`ls`, `read_file`, `edit_file`)
- **Subagent coordination** via `task` tool for spawning specialized agents
- **Long-term memory** via LangGraph Store persistence

### Strengths for Your Use Case

#### 1. **Subagent Delegation** ⭐⭐⭐⭐⭐
```python
# Spawn specialized agents for each data source
task("Fetch and analyze GitHub trending", context={...})
task("Fetch and analyze Hacker News", context={...})
task("Fetch Reddit data", context={...})
```
- **Perfect for:** Adding new sources (Priority 2)
- **Benefit:** Each source gets dedicated agent without polluting main context
- **Your case:** GitHub, HN, Reddit, X.com can be independent subagents

#### 2. **Planning Capabilities** ⭐⭐⭐⭐⭐
```python
# Agent auto-plans complex workflows
agent.write_todos([
    "Fetch all data sources",
    "Score and rank items",
    "Generate report",
    "Schedule delivery"
])
```
- **Perfect for:** Complex sequences (Phase 2 enhancements)
- **Benefit:** Agent decomposes tasks, adapts plan as it learns
- **Your case:** Scheduling, email delivery, dashboard become first-class agents

#### 3. **Context Management** ⭐⭐⭐⭐
- Automatically spills data to files when context gets heavy
- Prevents "context explosion" as you add more sources
- Agent can `read_file()`, `edit_file()`, `ls()` for data management
- **Your case:** Managing 5+ data sources without losing context

#### 4. **Extensibility** ⭐⭐⭐⭐
- Add new tools without touching agent logic
- Subagents inherit tool set automatically
- **Your case:** New data sources (Reddit, X) are just new agents + tools

### Weaknesses for Your Use Case

#### 1. **Multi-Provider LLM Support** ⚠️
- LangGraph defaults to OpenAI models
- Your LiteLLM abstraction enables Anthropic, OpenAI, Ollama, etc.
- **Risk:** May need custom wrapper to preserve multi-provider support

#### 2. **LangSmith Tracing Needs Work** ⚠️
- Deep Agents built on LangGraph which has tracing
- But workflow is more complex (subagents, planning, etc.)
- **Risk:** Tracing hierarchy becomes harder to understand

#### 3. **Opinionated Framework** ⚠️
- Deep Agents has specific patterns (planning, subagents, todos)
- Your current manual approach has 100% control
- **Risk:** May add complexity for simple workflows

#### 4. **No MCP Support** ❌
- Deep Agents doesn't provide built-in MCP integration
- You'd still need custom MCP client wrappers
- **Risk:** Doesn't solve MCP integration problem

#### 5. **Newer/Less Stable** ⚠️
- LangChain is stable (OpenAI preferred framework)
- Deep Agents is newer (community-driven)
- **Risk:** API changes, fewer StackOverflow answers

### Example Implementation

```python
from langgraph.prebuilt import create_tool_calling_agent
from langchain_community.tools import tool

@tool
def fetch_github_trending(time_range: str = "daily"):
    """Fetch GitHub trending repos"""
    # Your existing GitHub client code
    return github_data

@tool
def fetch_hacker_news():
    """Fetch Hacker News posts"""
    return hn_data

# Create agent with planning
agent = create_tool_calling_agent(
    model=ChatAnthropic(model="claude-3-5-sonnet-20241022"),
    tools=[fetch_github_trending, fetch_hacker_news, score_relevance],
    # Adds: write_todos, task, file_system tools automatically
)

# Agent can now:
# - Plan: "Break down this into subagents for each source"
# - Execute: spawn subagents via task() tool
# - Manage: write results to files, read them back
# - Learn: adapt plan based on results
```

---

## Deep Dive: Claude Agent SDK

### What It Is
Anthropic's official SDK providing:
- **Tool-use loop** - Automatic handling of tool invocation
- **Extended thinking** - Claude reasons about complex problems
- **Standardized tools** - JSON schema-based definitions
- **MCP integration** - Native Model Context Protocol support
- **Automatic tracing** - Built-in observability

### Strengths for Your Use Case

#### 1. **First-Class MCP Support** ⭐⭐⭐⭐⭐
```python
# Future: Connect MCP servers directly
mcp_server = MCPClient.connect("github://...")
tools = mcp_server.list_tools()  # Automatic tool discovery

# vs Deep Agents: Need custom wrapper
```
- **Perfect for:** Your Phase 2 goal (MCP integration)
- **Benefit:** Official GitHub MCP server integration out of box
- **Your case:** Direct MCP → tool conversion

#### 2. **Extended Thinking** ⭐⭐⭐⭐
- Claude reasons through complex problems step-by-step
- Better for multi-step analysis workflows
- **Your case:** Ranking, relevance scoring, report generation
- **Benefit:** More nuanced understanding of content

#### 3. **Streamlined Tool Loop** ⭐⭐⭐⭐
```python
# SDK handles everything:
# 1. Claude reasons about which tool to call
# 2. Invokes tool with validated inputs
# 3. Parses response, continues reasoning
# 4. Returns final result
```
- Replaces your manual tool-use loop in react_agent.py
- Less orchestration code to maintain
- Fewer bugs in tool invocation

#### 4. **Native Multi-Provider Avoidance** ⚠️
- SDK is Claude-specific (no OpenAI fallback)
- But your LiteLLM wrapper becomes simpler
- **Your case:** Stick with LiteLLM for non-Anthropic providers

#### 5. **Anthropic's Official Docs** ⭐⭐⭐⭐
- Direct support from Anthropic team
- Guaranteed compatibility with latest Claude models
- **Your case:** Peace of mind for production use

### Weaknesses for Your Use Case

#### 1. **No Native Subagent Coordination** ❌
- SDK doesn't have `task()` tool for spawning subagents
- You'd build it manually (more work)
- **Risk:** Adding Reddit, X.com requires custom subagent framework

#### 2. **No Built-in Planning** ❌
- SDK doesn't have `write_todos` planning tool
- Agent must manage its own plan (less structured)
- **Risk:** Complex workflows become harder to manage

#### 3. **No File System Tools** ❌
- SDK doesn't provide `read_file`, `write_file` automatically
- You'd need to add them manually
- **Risk:** Context management burden on you

#### 4. **Claude-Only** ⚠️
- If you want to switch LLM providers (OpenAI, etc.), SDK doesn't help
- LiteLLM is generic; SDK is Anthropic-specific
- **Risk:** Less flexibility if Anthropic availability/cost becomes issue

#### 5. **Tool Invocation is "Dumb"** ⚠️
- SDK handles tool loop, but doesn't do planning
- Each tool call is reactive (no lookahead planning)
- **Risk:** Can't say "plan out all steps then execute"

### Example Implementation

```python
from anthropic import Anthropic

client = Anthropic()

tools = [
    {
        "name": "fetch_github_trending",
        "description": "Fetch GitHub trending repositories",
        "input_schema": {
            "type": "object",
            "properties": {
                "time_range": {"type": "string", "enum": ["daily", "weekly", "monthly"]}
            }
        }
    },
    # ... more tools
]

messages = [
    {
        "role": "user",
        "content": "Fetch trending content from GitHub and Hacker News, score relevance, generate report"
    }
]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    tools=tools,
    messages=messages
)

# SDK automatically:
# - Claude reasons about workflow
# - Calls fetch_github_trending tool
# - Calls fetch_hacker_news tool
# - Calls score_relevance tool
# - Returns final result
```

---

## Comparative Matrix

| Feature | Deep Agents | Claude SDK | Your Current |
|---------|-------------|-----------|--------------|
| **Planning** | ✅ Built-in `write_todos` | ❌ Manual | Manual |
| **Subagents** | ✅ Built-in `task` tool | ❌ Manual | N/A |
| **File System** | ✅ Built-in (ls, read, write) | ❌ Manual | N/A |
| **MCP Support** | ❌ Requires wrapper | ⭐ Native (upcoming) | Manual |
| **Extended Thinking** | ⚠️ Via LLM choice | ✅ Built-in | Manual |
| **Multi-Provider** | ✅ LangGraph generic | ❌ Claude-only | ✅ LiteLLM |
| **Context Management** | ✅ Automatic | ❌ Manual | Manual |
| **Tool Loop** | Via LangGraph | ✅ Automatic | Manual |
| **LangSmith Tracing** | ✅ (Complex) | ✅ (Simpler) | ✅ Works now |
| **Learning Curve** | Moderate | Low | Flat (you know it) |
| **Production Readiness** | ✅ (LangGraph stable) | ✅ (Anthropic backed) | ✅ Works today |

---

## Decision Framework

### Choose **Deep Agents** If:

1. ✅ You want to add many data sources (Reddit, X, LinkedIn, etc.)
   - Subagent coordination scales beautifully

2. ✅ You want sophisticated planning and task breakdown
   - `write_todos` tool enables complex workflows

3. ✅ You expect complex multi-step analysis
   - Planning + subagents handle it naturally

4. ✅ Context management becomes a pain point
   - Automatic file system spilling saves you

5. ✅ You're open to losing some multi-provider flexibility
   - LangGraph is generic but less abstracted

### Choose **Claude Agent SDK** If:

1. ✅ MCP integration is your top Phase 2 priority
   - Official GitHub/HN MCP servers coming

2. ✅ You want minimal framework overhead
   - Just tool-use loop, nothing fancy

3. ✅ You need guaranteed Anthropic support
   - Official SDK = official support channel

4. ✅ Your current architecture is working fine
   - Small incremental step (tool loop automation)

5. ✅ Multi-provider support is important to you
   - Keep LiteLLM abstraction intact

### Choose **Status Quo** (Manual ReACT) If:

1. ✅ Phase 2 isn't urgent
   - Current implementation works and is tested

2. ✅ You want maximum control
   - No framework lock-in

3. ✅ Your workflow is simple (won't get much simpler)
   - Adding 2-3 sources is manageable manually

4. ⚠️ But: You'll eventually hit complexity ceiling
   - Eventually want planning, subagents, or MCP

---

## My Recommendation

**For your specific case, I'd recommend:**

### **Immediate (Phase 2a): Claude Agent SDK**
- Replace manual tool-use loop with SDK
- Keep LiteLLM abstraction (for multi-provider fallback)
- Await official MCP integration (announced but not released)
- **Timeline:** 1-2 weeks, minimal code changes
- **Result:** Better observability, cleaner code, MCP-ready

### **Future (Phase 2b): Migrate to Deep Agents**
- After adding 3+ data sources (Reddit, X, LinkedIn)
- When manual subagent coordination becomes painful
- When file system context management is critical
- **Timeline:** When codebase > 500 LOC, team > 1 person
- **Result:** Sophisticated multi-source workflow, automatic planning

---

## Action Items

### If You Choose Claude Agent SDK:

1. **Update react_agent.py**
   - Initialize `Anthropic()` client
   - Convert Tool Registry to SDK tool definitions
   - Replace manual tool-use loop with SDK loop

2. **Keep LiteLLM Wrapper**
   - For non-Anthropic provider support
   - Or deprecate if full Claude commitment

3. **Update Tests**
   - Test SDK tool invocation
   - Test with mocked tools

4. **Wait for MCP Release**
   - Anthropic announced MCP support
   - Will enable direct GitHub MCP server integration

### If You Choose Deep Agents:

1. **Add LangGraph Dependency**
   - `uv pip install langchain langgraph`

2. **Refactor to LangGraph Structure**
   - Define state machine for workflow
   - Create agent from `create_tool_calling_agent`

3. **Implement Subagents**
   - GitHub source = subagent
   - HN source = subagent
   - Scoring = subagent
   - Ranking = subagent

4. **Replace Tool Registry**
   - Convert to @tool decorators
   - Deep Agents automatically adds planning, file system, task tools

5. **Update Documentation**
   - New architecture diagram (state machine)
   - Subagent coordination explained

---

## Code Skeleton Comparison

### Claude Agent SDK Approach
```python
from anthropic import Anthropic

class NewsAgent:
    def __init__(self, config, cache, llm_provider):
        self.client = Anthropic()
        self.tools = self._define_tools()

    def run(self):
        messages = [{
            "role": "user",
            "content": "Fetch and analyze news from GitHub, HN. Score relevance. Generate report."
        }]

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=self.tools,
            messages=messages
        )

        # SDK handles tool loop automatically
        # Just process final response
        return self._process_response(response)
```

### Deep Agents Approach
```python
from langgraph.prebuilt import create_tool_calling_agent
from langchain_core.tools import tool

class NewsAgent:
    def __init__(self, config, cache, llm_provider):
        self.tools = [
            fetch_github_tool,
            fetch_hn_tool,
            score_relevance_tool,
            generate_report_tool,
            # Automatically added by Deep Agents:
            # - write_todos (planning)
            # - task (subagents)
            # - file system (ls, read, write, edit)
        ]
        self.agent = create_tool_calling_agent(
            model=ChatAnthropic(...),
            tools=self.tools
        )

    def run(self):
        # Agent handles planning, subagent coordination automatically
        result = self.agent.invoke({
            "messages": [{
                "role": "user",
                "content": "Aggregate news from all sources, analyze, report"
            }]
        })
        return result
```

---

## Next Steps

**Decision Required:**
1. Which framework appeals more to your vision?
2. What's your timeline for Phase 2?
3. How many data sources do you plan to support?

Once you decide, I can:
- Create detailed migration plan with exact code changes
- Implement the migration with full testing
- Update documentation and architecture diagrams
- Provide before/after comparison

**My recommendation: Start with Claude Agent SDK** (simpler, safer bet) then evaluate Deep Agents once you need subagents.
