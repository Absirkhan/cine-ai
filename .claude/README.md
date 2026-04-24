# .claude Directory

This directory contains context files for Claude Code sessions to maintain project continuity.

## 📄 Files

### `project_context.md` ⭐ **IMPORTANT**
**Always read this file at the start of each Claude session.**

This file contains:
- Current implementation status (what's done, what's pending)
- Complete project structure
- Key design decisions and rationale
- Technical patterns to follow
- Testing strategy
- Important notes for development
- Quick reference for APIs and dependencies

**Update this file whenever:**
- A new phase is completed
- A major design decision is made
- New patterns or conventions are established
- Project structure changes
- API integrations are added

### `settings.local.json`
Claude Code local settings (auto-generated, don't edit manually)

## 🔄 Workflow for Multi-Session Development

### Starting a New Session

1. **Read `project_context.md`** to understand current state
2. **Check** `IMPLEMENTATION_STATUS.md` in project root for detailed progress
3. **Review** `NEXT_STEPS.md` for immediate next tasks
4. **Continue** from where the last session left off

### Ending a Session

1. **Update `project_context.md`** with:
   - New completed components
   - New design decisions
   - Progress percentage
   - Last session summary
2. **Commit** changes with descriptive message
3. **Update** `IMPLEMENTATION_STATUS.md` if needed

## 📝 Context Maintenance Checklist

Before ending each session, ensure:

- [ ] `project_context.md` updated with new progress
- [ ] Implementation status percentages updated
- [ ] New files/directories documented
- [ ] Any API changes or new integrations noted
- [ ] Design decisions with rationale documented
- [ ] "Last Session Summary" updated

## 🎯 Quick Navigation

From any Claude session, ask Claude to:
- "Read the project context" → Opens `.claude/project_context.md`
- "Check implementation status" → Opens `IMPLEMENTATION_STATUS.md`
- "What's next?" → Opens `NEXT_STEPS.md`
- "Show project structure" → Reviews directory layout

## 💡 Best Practices

1. **Always start by reading context** - Don't assume you know the current state
2. **Update context incrementally** - Don't wait until end of long session
3. **Be specific in updates** - Include file paths, function names, key decisions
4. **Track blockers** - Note any issues that need resolution
5. **Document workarounds** - If you found a solution to a problem, document it

## 🔗 Related Files

- `/README.md` - User-facing project documentation
- `/IMPLEMENTATION_STATUS.md` - Detailed phase-by-phase status
- `/NEXT_STEPS.md` - Step-by-step guide for continuation
- `/backend/shared/schema.py` - **Critical**: Shared data structures
- `/backend/config.py` - Configuration and environment setup

---

**Remember:** This context file is your memory across sessions. Keep it accurate and up-to-date!
