# Replit Removal Summary

This document summarizes all Replit-specific code that has been removed from the Gear Exchange Hub application.

## Files Removed
- `server/replit_integrations/` - Entire directory (can be deleted)
- `shared/models/auth.ts` - Merged into `shared/schema.ts` (can be deleted)
- `.replit` - Replit configuration file (can be deleted if not using Replit)

## Code Changes

### 1. `vite.config.ts`
**Removed:**
- `@replit/vite-plugin-runtime-error-modal` import and usage
- `@replit/vite-plugin-cartographer` conditional import
- `@replit/vite-plugin-dev-banner` conditional import
- `process.env.REPL_ID` check

**Result:** Clean vite config with only React plugin

### 2. `package.json`
**Removed from devDependencies:**
- `@replit/vite-plugin-cartographer`
- `@replit/vite-plugin-dev-banner`
- `@replit/vite-plugin-runtime-error-modal`

### 3. `shared/schema.ts`
**Changed:**
- Comment: `// === AUTH TABLES (Mandatory for Replit Auth) ===` → `// === AUTH TABLES ===`
- Merged auth fields from `shared/models/auth.ts` into main users table
- Added `password` field for local authentication

### 4. `server/storage.ts`
**Removed:**
- `getUserByReplitId(replitId: string)` method from interface
- Implementation of `getUserByReplitId` method

### 5. `server/routes.ts`
**Changed:**
- Import: `from "./replit_integrations/auth"` → `from "./auth"`
- Removed `registerAuthRoutes(app)` call
- Simplified `getInternalUser()` to use local session instead of Replit claims

### 6. `server/db.ts`
**Removed:**
- Import: `import * as authSchema from "@shared/models/auth"`
- Removed authSchema spread from drizzle config

### 7. `server/index.ts`
**Added:**
- Manual `.env` file loading (no dependency on external packages)

### 8. `server/auth.ts` (NEW)
**Created:**
- Local authentication with username/password
- Password hashing using Node.js crypto (scrypt)
- Session management
- `/api/register`, `/api/login`, `/api/logout`, `/api/user` endpoints

## Authentication Changes

### Before (Replit Auth):
- OAuth-based authentication via Replit
- User identified by `googleId` (Replit user ID)
- Session managed by Replit's OIDC provider
- Required `ISSUER_URL` and `REPL_ID` environment variables

### After (Local Auth):
- Username/password authentication
- Passwords hashed with scrypt
- Session managed locally with express-session
- Only requires `DATABASE_URL` and `SESSION_SECRET`

## Environment Variables

### Removed:
- `ISSUER_URL` - Replit OIDC issuer URL
- `REPL_ID` - Replit project ID

### Required:
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Session encryption key
- `PORT` - Server port (optional, defaults to 5000)
- `NODE_ENV` - Environment mode (optional, defaults to development)

## Next Steps

1. **Delete unused files:**
   ```bash
   rm -rf server/replit_integrations
   rm shared/models/auth.ts
   rm .replit  # Optional, only if not using Replit
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Update database schema:**
   ```bash
   npm run db:push
   ```

4. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Fill in your database credentials
   - Generate a secure SESSION_SECRET

5. **Start the application:**
   ```bash
   npm run dev
   ```

## Database Schema Changes

The `users` table now includes:
- `password` (text) - Hashed password for local auth
- `firstName` (text) - User's first name
- `lastName` (text) - User's last name
- `profileImageUrl` (text) - Profile image URL

The `googleId` field is retained for backward compatibility but is now optional.

## API Endpoints

### New Authentication Endpoints:
- `POST /api/register` - Register new user with username/password
- `POST /api/login` - Login with username/password
- `POST /api/logout` - Logout current user
- `GET /api/user` - Get current authenticated user

### Removed Endpoints:
- `/api/login` (Replit OAuth redirect)
- `/api/callback` (Replit OAuth callback)
- `/api/logout` (Replit logout redirect)

## Notes

- All authentication is now self-contained and doesn't rely on external services
- The application can run on any hosting platform, not just Replit
- TypeScript lint errors about missing modules are expected until `npm install` is run
- The application is now truly "hardcoded" with no external auth dependencies
