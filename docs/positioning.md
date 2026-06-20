# OpenACCP Positioning

OpenACCP is an open workflow protocol for coordinating multi-agent software work.

It is the coordination layer for teams using Codex, Claude Code, Aider, OpenHands, SWE-agent, LangGraph, CrewAI, AutoGen, the OpenAI Agents SDK, or their own agent stack on real software projects.

OpenACCP helps when the workflow has moved beyond one agent and one prompt:

- source facts need classification before agents act,
- multiple agents need clear lanes,
- handoffs need consume,
- reviewers need evidence,
- Frontiers need to keep closing B0/B1/B2 work,
- final acceptance needs a clear owner.

## Short Version

A prompt tells one agent what to try next.

A loop keeps one agent moving until a check passes.

A spec tells agents what the product should become.

OpenACCP coordinates the project around all of that: facts, roles, authority, task cards, worktrees, handoffs, reviews, return wake, consume results, and final acceptance.

## Where It Fits

OpenACCP fits around:

- an agent tool,
- an IDE assistant,
- a prompt collection,
- a project management app,
- tests, CI, review, and human ownership.

## Compared With Coding Assistants

Aider, Codex-style coding agents, and IDE assistants help edit code. OpenACCP gives that code work a source pack, CARDs, task cards, authority boundary, handoff path, reviewer evidence, return wake, and acceptance gate.

## Compared With Agent Frameworks

LangGraph, CrewAI, AutoGen, and the OpenAI Agents SDK help build agent systems. OpenACCP adds the delivery layer around those systems: source status, authority, task cards, handoffs, reviews, consume results, and status reporting.

## Compared With Autonomous SWE Tools

OpenHands and SWE-agent can produce repository changes. OpenACCP makes those changes reviewable and bounded through task cards, worktree discipline, handoffs, and final-authority consume.

## Compared With Agent Loops

Agent loops keep one lane of work alive. OpenACCP keeps multiple lanes aligned. It helps teams decide which facts count, which agent owns the lane, which return needs consume, which reviewer evidence matters, and which decision stays with Primary or the human owner.

## Compared With Workflow Prompting Systems

Claude Workflow and SuperClaude provide reusable modes and command patterns. OpenACCP focuses on cross-agent evidence governance: source packs, authority charters, handoff states, reviewer evidence, return wake, validator gates, and final acceptance.
