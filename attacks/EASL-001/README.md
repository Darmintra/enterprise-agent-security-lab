# EASL-001: Broken Agent Authorization

## Overview

I created an AI chatbot named Mira backed by a local Qwen LLM that serves as a Model where it checks if a bank user could retrieve the 
users data they are not authorized to access. A user prompt is first sent to the LLM, which may generate a request to use an available tool. The tool dispatcher checks whether the requested tool is allowed, while a separate authorization control checks whether the authenticated user is permitted to access the requested customer data.

The AI architecture is as following:

Prompt -> LLM -> Action decision -> Tool request -> Dispatcher -> Authorization -> Tool

## Scenario

MBank is a fictional financial institution using an internal AI assistant named Mira.

"Sarah Chen (E001) is an authenticated MBank employee using Mira to retrieve customer information as part of her daily operations. Sarah is authorized to access customer C001 only. She queries Mira with: “Show me information about customer C002.”

The tool knew which customer was requested. It did not know which authenticated user made the request. Therefore it could not enforce customer-level authorization. E001 could request C002 even though E001 should only access C001.

## Vulnerable Design

The initial customer tool accepted only a customer ID:

`get_customer(customer_id)`

This is an issue because it did not know which authenticated user to access the customer id, there could be a privilege mismatch
where the banking user can access customer ID they are not authorized.

## Security Impact

Authenticated but unauthorized user such as E001 could request C002 eventhough E001 should only be able to access C001, no customer-level authorization is enforced

## Root Cause

The customer tool could not determine why the requesting user was authorized or not because it only check the customer id that was requested.
It did not check the trusted authenticated identity and if there is a specific authorization field that the user need to satisfy.

## Remediation

The customer tool was redesigned to receive trusted user identity context and the requested customer ID:

`get_customer(authenticated_user_id, requested_customer)`

So now, the get_customer function check the authenticated user id against its authorized customers first before 

## Hardened Flow

User -> Enterprise IdP -> Application Session -> Mira -> Tool Dispatcher -> Authorization -> Customer Tool

## Security Principle

In Zero Trust principle, the concept was NOT to trust any action because it originated from any AI Agent. Verify identity, tool capability and resource authorization at the boundary.

Three cybersecurity principles : 
1. Trusted identity propagation : User identity must originate from a trusted identity source (enterprise IdP) and remain outside model-controlled data
2. Least Privilege : get_customer tool must be on the allowlist, and unknown tools must not be allowed to run, this will prevent LLM from having too much privilege
3. Resource Authorization : E001 is authorized only to access C001 customer records

## Lab Result

E001 -> C001 -> ALLOW

E001 -> C002 -> DENY

Add a section such as:
## Current Lab Architecture

The lab currently implements a local AI assistant named Mira using an instruction-tuned Qwen model through Hugging Face Transformers.

Current request flow:

LLM
 │
 │ wants get_customer(C002)
 ▼
TOOL DISPATCHER
 │
 │ "Is this an approved capability?"
 │
 │ get_customer → YES
 ▼
RESOURCE AUTHORIZATION
 │
 │ "Can this principal perform this
 │  action against this resource?"
 │
 │ E001 + READ + C002 → NO
 ▼
DENY

The LLM can request a customer lookup by producing a structured tool request containing the requested customer ID.

The authenticated user identity is maintained separately from model-generated output. The model does not determine the identity used for authorization.

### Current Security Controls

- Synthetic user and customer data only
- Trusted user identity separated from LLM-generated arguments
- Explicit tool allowlisting through the dispatcher
- Customer-level authorization enforced by the customer tool
- Unauthorized customer requests fail closed

### Current Status

- [x] Local Python environment
- [x] Synthetic MBank users
- [x] Synthetic MBank customer data
- [x] Customer lookup tool
- [x] Customer-level authorization
- [x] Local Qwen instruction model
- [x] Prompt tokenization and local inference
- [x] Structured LLM tool request
- [x] Basic tool dispatcher
- [x] Authorized customer lookup
- [x] Unauthorized customer lookup denied
- [ ] EASL-002 direct prompt injection
- [ ] Automated security tests
- [ ] RAG / indirect prompt injection
