# Keycloak Configuration Analysis

## Overview

- **version**: Keycloak 26.4.0
- **JVM**: 21.0.8 (Red Hat, Inc. OpenJDK 64-Bit Server VM 21.0.8+9-LTS)
- **OS**: Linux 5.15.167.4-microsoft-standard-WSL2 amd64

## Introduction

This document analyzes the configuration of Keycloak as an identity broker. The primary goal is to enable users to authenticate with their DeviantArt accounts to access the application. Keycloak acts as an intermediary, connecting to DeviantArt's OAuth 2.0 API.

When a user chooses to log in via DeviantArt, the application redirects them to Keycloak. Keycloak then forwards the authentication request to DeviantArt. After the user successfully authenticates and grants consent on DeviantArt, they are redirected back to Keycloak. Keycloak, in turn, creates a session for the user and issues a token to the client application, completing the login process. This brokering pattern simplifies the application's authentication logic, as it only needs to trust Keycloak, which handles the specifics of the external identity provider.

## Prerequisites

You must have already created a DeviantArt application to obtain the Client ID and Client Secret. Follow the instructions in the [DeviantArt Developer Setup](./DeviantArt-Authentication.md) section to set up your application on DeviantArt's developer portal.

## Keycloak Configuration Steps

### Creating a Realm

A realm in Keycloak is equivalent to a tenant. Each realm allows an administrator to create isolated groups of applications and users. Initially, Keycloak includes a single realm, called **master**. Use this realm only for managing Keycloak and not for managing any applications.

1. Open the Keycloak Admin Console.
    > The default URL is `http://localhost:8080/` or `http://<your-domain>:8080/` if running on a server. To certify the URL, check the docker-compose.yml file for the port mapping of the Keycloak service.
    > For this project, we use Traefik as a reverse proxy, so the URL is <https://miraveja.127.0.0.1.nip.io/auth> and it serves as the base URL for Keycloak. Adjust accordingly if you are using a different domain or port.
2. Expand the dropdown in the top-left corner (it should say "Keycloak" or "master") and click on "Create Realm".
3. Enter a name for the new realm, e.g., `miraveja`, in the "Realm Name" field.
4. Click "Create".

### Creating an User

1. Verify that you are in the correct realm (e.g., `miraveja`).
2. Click on "Users" in the left-hand menu.
3. Click the "Create new user" button.
4. Fill in the required fields:
   - **Username**: Choose a username for the user.
   - **Email**: (Optional) Enter the user's email address.
   - **First Name** and **Last Name**: (Optional) Enter the user's first and last names.
5. Click the "Create" button.

The user will be created, but they will not be able to log in until you set a password:

1. Click **Credentials** at the top of the page.
2. Click the "Set Password" button.
3. Enter a new password in the "New Password" and "Password Confirmation" fields.
4. Toggle off the "Temporary" option if you want the user to keep this password (otherwise, they will be required to change it on first login).
5. Click the "Save" button.
6. Click the "Confirm" button in the confirmation dialog.

### Log in to the Account Console

1. Access the [Account Console](https://miraveja.127.0.0.1.nip.io/auth/realms/miraveja/account) (or replace `localhost` with your server's domain and/or the port if necessary).
2. Log in using the username and password of the user you just created.

As a user in the Account Console, you can manage your account including modifying your profile, adding two-factor authentication, and including identity provider accounts.

### Secure the First Application

To secure the first application, you start by registering the application with your Keycloak instance:

1. Open the [Keycloak Admin Console](https://miraveja.127.0.0.1.nip.io/auth/).
2. Ensure you are in the correct realm (e.g., `miraveja`).
3. Click on "Clients" in the left-hand menu.
4. Click the "Create client" button.
5. Fill in the required fields:
    - **Client Type**: Select `OpenID Connect` from the dropdown.
    - **Client ID**: A unique identifier for your application (e.g., `miraveja-client`).
6. Click the "Next" button.
7. Fill in the following fields on the next screen:
    - **Client authentication**: Enable this option if your application can securely store client credentials. Disable it for public clients like single-page applications (SPAs) or mobile apps.
    - **Authentication flow**: Choose the appropriate flow for your application. The default is usually sufficient. Make sure to select "Standard flow".
8. Click the "Next" button.
9. On the next screen, configure the following settings:
    - **Valid redirect URIs**: Specify the URIs to which Keycloak can redirect after authentication. For development, you might use `https://miraveja.127.0.0.1.nip.io/miraveja/` for frontend and `https://miraveja.127.0.0.1.nip.io/miraveja/api/` for backend. Adjust these URIs based on your actual deployment.
    - **Web Origins**: Specify the allowed web origins for CORS. Set it to `https://miraveja.127.0.0.1.nip.io`.
10. Click the "Save" button.

To confirm the client is created, you can use the SPA testing application on the [Keycloak website](https://www.keycloak.org/app/):

> *To allow this, you need to add `https://www.keycloak.org` to the "Web Origins" field in your client settings and `https://www.keycloak.org/app/*`* to the "Valid Redirect URIs" field.

1. Open the [Keycloak SPA Testing Application](https://www.keycloak.org/app/).
2. Fill in the fields:
    - **Keycloak URL**: `https://miraveja.127.0.0.1.nip.io/auth/` (or your server's domain and/or port).
    - **Realm**: `miraveja` (or your realm name).
    - **Client**: `miraveja-client` (or your client ID).
3. Click the "Save" button.
4. Click the "Sign in" button to authenticate to this application using the Keycloak server you started earlier.

*This did not work for me, I got "Failed to load resource: net::ERR_BLOCKED_BY_CLIENT" in the browser console.*

What worked was to use Insomnia to test the OAuth2 flow:

1. Open Insomnia and create a new request.
2. Select "Auth" tab.
3. Choose "OAuth 2.0" as the authentication type.
4. Fill in the fields:
    - **Enabled**: Toggle this on.
    - **Grant Type**: Authorization Code.
    - **Authorization URL**: `https://miraveja.127.0.0.1.nip.io/auth/realms/miraveja/protocol/openid-connect/auth`
    - **Access Token URL**: `https://miraveja.127.0.0.1.nip.io/auth/realms/miraveja/protocol/openid-connect/token`
    - **Client ID**: `miraveja-client`
    - **Client Secret**: (leave blank if "Client authentication" was disabled)
    - **Redirect URL**: `https://miraveja.127.0.0.1.nip.io/miraveja/` (or your actual redirect URI)
5. Click "Fetch Tokens".
6. A browser window should open, prompting you to log in. Use the credentials of the user you created earlier.
7. After logging in, you should be redirected back to Insomnia, and the access token should be populated, as well as the refresh token if applicable.

## URL Configuration

When deploying Keycloak behind a reverse proxy or load balancer, it's essential to configure the base URL and related settings correctly. This ensures that all redirects and links generated by Keycloak point to the correct external URL. Below are the key environment variables to set in your `.env` file:

```.env
KC_BASE_PATH=auth
KC_HOSTNAME=https://miraveja.127.0.0.1.nip.io/${KC_BASE_PATH}
KC_HTTP_ENABLED=true
KC_PROXY_HEADERS=xforwarded
KC_HTTP_RELATIVE_PATH=${KC_BASE_PATH}
```

- `KC_BASE_PATH`: This sets the base path for Keycloak. In this case, it's set to `auth`, meaning all Keycloak URLs will be prefixed with `/auth`.
- `KC_HOSTNAME`: This specifies the external hostname and protocol that users will use to access Keycloak. It should include the full URL, including the base path.
- `KC_HTTP_ENABLED`: This enables HTTP support. Set to `true` if you want Keycloak to accept HTTP requests (useful for local development). Since we are using Traefik with HTTPS, this can be set to `true`.
- `KC_PROXY_HEADERS`: This tells Keycloak to trust the `X-Forwarded-*` headers set by the reverse proxy. This is crucial for correct URL generation and handling of secure connections.
- `KC_HTTP_RELATIVE_PATH`: This sets the relative path for Keycloak. It should match the `KC_BASE_PATH`.

With these settings, Keycloak will generate URLs that correctly reflect the external access point, ensuring that users can authenticate and interact with the system without issues related to incorrect URL paths.

---
> **Authorization**: <https://miraveja.127.0.0.1.nip.io/auth/realms/miraveja/protocol/openid-connect/auth>
---
> **Token**: <https://miraveja.127.0.0.1.nip.io/auth/realms/miraveja/protocol/openid-connect/token>
---
> **Admin Console**: <https://miraveja.127.0.0.1.nip.io/auth/admin>
---

## Identity Provider Configuration

For this project, we are using DeviantArt as the external identity provider. To configure DeviantArt as an identity provider in Keycloak, follow these steps:

1. In the Keycloak Admin Console, certify you are in the correct realm (e.g., `miraveja`).
2. Click on "Identity Providers" in the left-hand menu.
3. From the "Add provider..." dropdown (or the list of providers that appears when no providers are configured), select "OAuth v2.0". (Keycloak version must be 26.4.0 or higher)
4. Fill in the required fields:
    - **Alias**: A unique name for this identity provider (e.g., `deviantart`).
    - **Display Name**: The name that will be shown to users on the login page (e.g., `DeviantArt`).
    - **Use discovery endpoint**: Disable this option.
    - **Authorization URL**: `https://www.deviantart.com/oauth2/authorize`
    - **Token URL**: `https://www.deviantart.com/oauth2/token`
    - **User Info URL**: `https://www.deviantart.com/api/v1/oauth2/user/whoami`
    - **Use PKCE**: Enable this option for enhanced security.
    - **PKCE Method**: Select `S256`.
    - **Client ID**: The client ID obtained from DeviantArt when you registered your application.
    - **Client Secret**: The client secret obtained from DeviantArt.
    - **ID Claim**: `userid`is the unique identifier for the user in DeviantArt.
    - **Username Claim**: `username` is the username of the user in DeviantArt.
    - **Email Claim**: `email` deviantArt does not provide email by default, the user must inform it on first login.
    - **Given name Claim**: `profile.real_name` is the real name of the user in DeviantArt.
    - **Scopes**: `basic`is the scope accepted by DeviantArt to access basic user information. This configuration is hidden under the "Advanced" section and only appears after saving the identity provider for the first time and editing it again.
5. Click the "Add" button.
6. After adding the identity provider, you can configure additional settings such as mappers to map user attributes from DeviantArt to Keycloak user attributes.

## Callback URL Flow

1. The user clicks "Login" button on the client application.
2. The client application redirects the user to Keycloak's authorization endpoint: `https://miraveja.127.0.0.1.nip.io/auth/realms/miraveja/protocol/openid-connect/auth`
3. Keycloak presents the login page, where the user selects "DeviantArt" as the identity provider.
4. Keycloak redirects the user to DeviantArt's authorization endpoint: `https://www.deviantart.com/oauth2/authorize`
5. The user logs in to DeviantArt and grants consent to the requested scopes.
6. DeviantArt redirects the user back to Keycloak with an authorization code: `https://miraveja.127.0.0.1.nip.io/auth/realms/miraveja/protocol/openid-connect/auth`
7. Keycloak exchanges the authorization code for tokens by making a POST request to DeviantArt's token endpoint: `https://www.deviantart.com/oauth2/token`
8. DeviantArt responds with an access token (and optionally a refresh token).
9. Keycloak retrieves user information from DeviantArt by making a GET request to the user info endpoint: `https://www.deviantart.com/api/v1/oauth2/user/whoami`
10. Keycloak creates a session for the user and issues its own tokens (ID token, access token, refresh token) to the client application.
11. The client application receives the tokens and sets a cookie or local storage for session management.
12. The user is now authenticated and can access protected resources in the client application.
