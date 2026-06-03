# Positioning

OpenACP is a coordination protocol and workflow kit for multi-agent engineering.

It is not:

- an agent runtime,
- an IDE assistant,
- a prompt collection,
- a project management app,
- a replacement for tests, CI, review, or human ownership.

## Compared With Coding Assistants

Aider, Codex-style coding agents, and IDE assistants help edit code. OpenACP defines when an agent may edit, what it may touch, what evidence it must return, and who may accept the result.

## Compared With Agent Frameworks

LangGraph, CrewAI, AutoGen, and the OpenAI Agents SDK help build agent systems. OpenACP defines source-of-truth handling, authority boundaries, task cards, handoffs, reviews, and status reporting around those systems.

## Compared With Autonomous SWE Tools

OpenHands and SWE-agent can produce repository changes. OpenACP makes those changes reviewable and bounded through task cards, worktree discipline, handoffs, and final-authority consume.

## Compared With Workflow Prompting Systems

Claude Workflow and SuperClaude provide reusable modes and command patterns. OpenACP focuses on cross-agent evidence governance: source packs, authority charters, handoff states, reviewer evidence, and validator gates.
