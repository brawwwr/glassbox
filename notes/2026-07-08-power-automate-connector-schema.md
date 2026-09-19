---
title: Custom connector: the schema is the contract
date: 2026-07-08
tags: [power-automate, connectors]
---

# Custom connector: the schema is the contract

Built a custom connector against a small internal REST API. Lessons:

- The OpenAPI definition is the contract. If the description of a parameter is vague, the person building
  the flow guesses. Same as a tool description for an LLM: the model only knows what the description says.
- Mark optional parameters as optional. Required-by-default caused three support questions.
- Return a consistent error object. Flows cannot branch on a message string reliably.
- Test the connector in the test tab with a real payload before publishing. The first version had the
  wrong content-type.
