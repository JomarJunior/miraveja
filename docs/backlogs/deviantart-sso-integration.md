# DeviantArt SSO Integration Backlog

This document outlines the backlog of tasks required to implement DeviantArt SSO as the first authentication method for MiraVeja.

## Status Legend

- ✅ Completed
- 🔄 In Progress
- ⏱️ Pending
- ❌ Blocked

## Phase 1: Research & Planning

### Task 1.1: Research DeviantArt OAuth 2.0/OpenID Connect API

- **Status**: ✅ Completed
- **Goal**: Understand DeviantArt's authentication flow, scopes, and API requirements
- **Dependencies**: None
- **Risks**: DeviantArt may have unique requirements or limitations not covered by standard OAuth flows
- **Deliverables**: Documentation of required endpoints, scopes, and authentication flow diagrams

### Task 1.2: Keycloak Configuration Analysis

- **Status**: ✅ Completed
- **Goal**: Determine how to configure Keycloak to work as an identity broker for DeviantArt
- **Dependencies**: Task 1.1
- **Risks**: Keycloak version compatibility with DeviantArt's OAuth implementation
- **Deliverables**: Configuration plan document including required client ID/secret fields, callback URLs, and token handling approach

### Task 1.3: Architecture Integration Decision

- **Status**: ✅ Completed
- **Goal**: Decide how authentication will flow between frontend, API, and Keycloak
- **Dependencies**: Tasks 1.1, 1.2
- **Risks**: Incorrect flow could introduce security vulnerabilities
- **Deliverables**: Authentication flow diagram showing request/response paths between all services

## Phase 2: DeviantArt Developer Setup

### Task 2.1: Register MiraVeja Application in DeviantArt

- **Status**: ✅ Completed
- **Goal**: Create a developer account and register the application with DeviantArt
- **Dependencies**: None
- **Risks**: Approval process may take time; production and development environments need separate registrations
- **Deliverables**: Developer account credentials, Application client ID and client secret

### Task 2.2: Configure OAuth Callback URLs

- **Status**: ✅ Completed
- **Goal**: Set up proper redirect URIs in the DeviantArt developer console
- **Dependencies**: Task 2.1
- **Risks**: Mismatched callback URLs will break the authentication flow
- **Deliverables**: Configured redirect URIs for both development and production environments

### Task 2.3: Define Required User Information Scopes

- **Status**: ✅ Completed
- **Goal**: Determine and configure the data MiraVeja needs from DeviantArt users
- **Dependencies**: Task 2.1
- **Risks**: Requesting too many permissions may reduce user conversion; too few may limit functionality
- **Deliverables**: List of scopes to request from users (profile info, email, etc.)

## Phase 3: Keycloak Configuration

### Task 3.1: Set Up Keycloak Realm for MiraVeja

- **Status**: ✅ Completed
- **Goal**: Create a dedicated realm for the application with appropriate settings
- **Dependencies**: Docker environment running with Keycloak
- **Risks**: Misconfiguration could impact security or user experience
- **Deliverables**: Configured Keycloak realm with appropriate settings (token lifetimes, required actions)

### Task 3.2: Configure DeviantArt as Identity Provider

- **Status**: ✅ Completed
- **Goal**: Set up DeviantArt as an external identity provider in Keycloak
- **Dependencies**: Tasks 2.1, 2.2, 2.3, 3.1
- **Risks**: OAuth flow may require custom mappers or configuration
- **Deliverables**: Working identity provider configuration in Keycloak

### Task 3.3: Configure User Attribute Mapping

- **Status**: ⏱️ Pending
- **Goal**: Map DeviantArt user attributes to Keycloak user attributes
- **Dependencies**: Task 3.2
- **Risks**: Missing critical user information could impact application functionality
- **Deliverables**: Attribute mapping configuration ensuring required user data is properly stored

### Task 3.4: Create Keycloak Client for API Service

- **Status**: ⏱️ Pending
- **Goal**: Configure a client for the API service to validate tokens
- **Dependencies**: Task 3.1
- **Risks**: Incorrect client configuration could lead to security issues
- **Deliverables**: Configured client with appropriate access type, valid redirect URIs, and client roles

### Task 3.5: Create Keycloak Client for Frontend

- **Status**: ✅ Completed
- **Goal**: Configure a client for the React frontend
- **Dependencies**: Task 3.1
- **Risks**: Improper public client configuration can introduce security issues
- **Deliverables**: Configured public client with appropriate settings for SPA authentication

## Phase 4: Backend Integration

### Task 4.1: Configure Keycloak Integration in FastAPI

- **Status**: 🔄 In Progress
- **Goal**: Set up JWT validation and user extraction in the API service
- **Dependencies**: Task 3.4
- **Risks**: Token validation issues could cause authentication failures
- **Deliverables**: Configured JWT validation middleware using Keycloak's public key

### Task 4.2: Implement Protected Routes

- **Status**: ⏱️ Pending
- **Goal**: Secure API endpoints that require authentication
- **Dependencies**: Task 4.1
- **Risks**: Over or under-protecting routes can impact security or usability
- **Deliverables**: Properly secured API endpoints with appropriate permission checks

### Task 4.3: Create User Profile Endpoints

- **Status**: ⏱️ Pending
- **Goal**: Develop API endpoints to retrieve and manage user profile information
- **Dependencies**: Task 4.2
- **Risks**: Need to handle cases where DeviantArt profile information is incomplete
- **Deliverables**: API endpoints for retrieving user information from authenticated requests

### Task 4.4: Implement User Creation/Update Logic

- **Status**: ⏱️ Pending
- **Goal**: Store DeviantArt user data in Postgres when users first authenticate
- **Dependencies**: Task 4.3
- **Risks**: Race conditions in user creation; handling user data changes from DeviantArt
- **Deliverables**: Logic to create or update user records in Postgres based on authentication events

## Phase 5: Frontend Integration

### Task 5.1: Implement Keycloak JavaScript Adapter

- **Status**: ✅ Completed
- **Goal**: Integrate Keycloak JavaScript library with React
- **Dependencies**: Task 3.5
- **Risks**: Managing token refresh and session state can be complex in SPAs
- **Deliverables**: Authentication service/hook for React components to use

### Task 5.2: Create Login UI Components

- **Status**: ⏱️ Pending
- **Goal**: Develop login interface including DeviantArt SSO button
- **Dependencies**: Task 5.1
- **Risks**: UX issues could reduce conversion rate for logins
- **Deliverables**: Login components with DeviantArt branding according to their guidelines

### Task 5.3: Implement Protected Routes in React

- **Status**: ✅ Completed
- **Goal**: Secure frontend routes that require authentication
- **Dependencies**: Task 5.1
- **Risks**: Poor UX if authentication state is not properly managed
- **Deliverables**: Route protection mechanism with redirect to login when required

### Task 5.4: Create User Profile Components

- **Status**: ⏱️ Pending
- **Goal**: Display and manage user profile information
- **Dependencies**: Tasks 4.3, 5.3
- **Risks**: Need to handle partially filled profiles from DeviantArt
- **Deliverables**: User profile view with appropriate UI for DeviantArt-sourced information

## Phase 6: Testing

### Task 6.1: Develop Authentication Flow Tests

- **Status**: ⏱️ Pending
- **Goal**: Create end-to-end tests for the complete authentication flow
- **Dependencies**: Tasks 4.4, 5.4
- **Risks**: Difficult to mock DeviantArt authentication without significant setup
- **Deliverables**: Testing strategy document and basic authentication tests

### Task 6.2: Test Token Validation and Refresh

- **Status**: ⏱️ Pending
- **Goal**: Ensure tokens are properly validated and refreshed
- **Dependencies**: Tasks 4.1, 5.1
- **Risks**: Token expiration handling issues could cause poor user experience
- **Deliverables**: Tests for token validation, refresh, and expiration scenarios

### Task 6.3: Test Error Scenarios and Edge Cases

- **Status**: ⏱️ Pending
- **Goal**: Verify application handles authentication failures gracefully
- **Dependencies**: Tasks 4.4, 5.4
- **Risks**: Difficult to simulate all possible error conditions
- **Deliverables**: Tests for common error cases (network issues, permission denials)

## Phase 7: Documentation & Deployment

### Task 7.1: Update Architecture Documentation

- **Status**: ⏱️ Pending
- **Goal**: Document the authentication flow in project documentation
- **Dependencies**: All implementation tasks
- **Risks**: Documentation can become outdated if not maintained
- **Deliverables**: Updated architecture diagrams and documentation showing authentication flow

### Task 7.2: Create Developer Guide for Authentication

- **Status**: ⏱️ Pending
- **Goal**: Document how to work with the authentication system
- **Dependencies**: All implementation tasks
- **Risks**: Missing critical information could slow future development
- **Deliverables**: Developer guide explaining how to use authentication in new features

### Task 7.3: Prepare Production Deployment Plan

- **Status**: ⏱️ Pending
- **Goal**: Define steps to safely deploy the authentication system
- **Dependencies**: All implementation tasks
- **Risks**: Production environment differences could cause unexpected issues
- **Deliverables**: Deployment checklist with verification steps

### Task 7.4: Document User Login Process

- **Status**: ⏱️ Pending
- **Goal**: Create user-facing documentation for the login process
- **Dependencies**: Task 5.2
- **Risks**: Unclear instructions could increase support requests
- **Deliverables**: User guide for authentication with screenshots and troubleshooting tips

## Alternative Approaches Considered

### 1. Direct OAuth Implementation vs. Keycloak

- **Direct OAuth Implementation**:
  - *Pros*: Fewer components, potentially simpler architecture
  - *Cons*: Need to implement token storage, validation, refresh logic; harder to add additional providers later

- **Keycloak (Recommended)**:
  - *Pros*: Centralized auth management, easier to add more providers, built-in user management features
  - *Cons*: Additional service to maintain, slightly more complex initial setup

**Decision**: Using Keycloak as it aligns with the existing architecture and will simplify adding more auth providers later.

### 2. Frontend Authentication Approaches

- **Keycloak JavaScript Adapter**:
  - *Pros*: Official library, handles token management
  - *Cons*: Additional dependency, somewhat opinionated

- **Custom OAuth Implementation with React Libraries**:
  - *Pros*: More control over UI and flow
  - *Cons*: More code to maintain, potential security issues

**Decision**: Using Keycloak's JavaScript adapter for the frontend to leverage its built-in token management and refresh capabilities.

## How to Update Status

To mark a task as complete, change its status from "⏱️ Pending" to "✅ Completed". For tasks in progress, use "🔄 In Progress". For blocked tasks, use "❌ Blocked" and add a note explaining the blocker.
