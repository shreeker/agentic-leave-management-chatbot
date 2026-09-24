# Agentic Architecture

## The key distinction

### Workflow

```text
request
  -> check balance
  -> check policy
  -> check calendar
  -> ask manager
  -> create request
```

The application determines the sequence.

### Agent

```text
goal
  -> model reasons about what is missing
  -> model selects a tool
  -> observe result
  -> model reasons again
  -> select another tool if needed
  -> change plan when evidence changes
  -> finish / ask user / wait for human
```

The application provides capabilities and guardrails; the model determines the next useful action.

## Why the code uses a generic loop

The `Agent.run()` method contains only:

```text
reason -> execute requested tools -> observe -> reason again
```

It does NOT encode leave-business sequencing.

The model can therefore do:

```text
policy -> balance
```

or

```text
balance -> calendar -> policy
```

or:

```text
calendar -> ask user
```

depending on the request and observations.

## Where deterministic logic belongs

Deterministic:
- identity/authentication
- authorization
- leave balance calculation
- working-day calculation
- database writes
- approval state transitions
- audit logging

Agentic:
- interpreting the user's goal
- deciding which tools are relevant
- deciding what information is missing
- deciding when policy retrieval is necessary
- deciding whether additional investigation is useful
- adapting the plan after tool results
- deciding when to ask the employee
- deciding when the goal is complete

## Production hardening

1. Put the API behind enterprise identity.
2. Inject authenticated employee ID from the token/session.
3. Use service-to-service IAM/OIDC rather than trusting an LLM-supplied identity.
4. Replace SQLite with Aurora PostgreSQL.
5. Replace demo calendar with Microsoft Graph/Google Workspace/corporate calendar.
6. Replace lightweight policy retrieval with OpenSearch, Bedrock Knowledge Bases, or a managed vector store.
7. Add idempotency keys to every write tool.
8. Add tool-level authorization.
9. Require explicit human approval for sensitive operations.
10. Persist agent state/checkpoints in a durable LangGraph checkpointer.
11. Add LangSmith tracing and evaluation datasets.
12. Add rate limits, timeouts, retries, circuit breakers, and audit trails.
