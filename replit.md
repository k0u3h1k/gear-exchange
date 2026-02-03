# Gear Exchange Hub

## Overview

Gear Exchange Hub (Hobby-Hopper) is a local hobby gear trading platform that connects enthusiasts to exchange items they no longer use for gear they want. The application enables users to list hobby equipment (musical instruments, cameras, gaming gear, etc.), discover items from nearby users based on geolocation, initiate trade requests, and communicate through an integrated messaging system.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter (lightweight client-side routing)
- **State Management**: TanStack React Query for server state caching and synchronization
- **Styling**: Tailwind CSS with custom theming (teal & orange color scheme)
- **UI Components**: shadcn/ui component library (Radix primitives with custom styling)
- **Animations**: Framer Motion for page transitions and micro-interactions
- **Build Tool**: Vite with hot module replacement

### Backend Architecture
- **Runtime**: Node.js with Express.js
- **Language**: TypeScript (ES modules)
- **API Design**: RESTful endpoints with type-safe route definitions in `shared/routes.ts`
- **Authentication**: Replit Auth (OpenID Connect) with Passport.js
- **Session Management**: PostgreSQL-backed sessions via `connect-pg-simple`

### Data Layer
- **Database**: PostgreSQL
- **ORM**: Drizzle ORM with type-safe schema definitions
- **Schema Location**: `shared/schema.ts` (main app tables) and `shared/models/auth.ts` (auth tables)
- **Migrations**: Drizzle Kit with `db:push` command for schema synchronization

### Key Data Models
- **Users**: Profile with username, bio, geolocation coordinates
- **Items**: Tradeable gear with title, description, category, images, location data
- **Trades**: Trade requests between users with status tracking (pending/accepted/rejected/completed)
- **Messages**: In-trade messaging system
- **Sessions**: Authentication session storage

### Project Structure
```
client/           # React frontend
  src/
    components/   # Reusable UI components
    hooks/        # Custom React hooks for data fetching
    pages/        # Route page components
    lib/          # Utilities and query client
server/           # Express backend
  replit_integrations/auth/  # Replit Auth implementation
shared/           # Shared types, schemas, and route definitions
```

### Authentication Flow
The app uses Replit Auth for user authentication. Users authenticate via Replit's OpenID Connect provider, and the system maintains a parallel user record in the app's database linked via `googleId` (Replit user ID). Protected routes check authentication status and redirect unauthenticated users to the login flow.

### Geolocation Features
Items and users can have latitude/longitude coordinates. The dashboard supports filtering items by radius from the user's current location using the browser's Geolocation API.

## External Dependencies

### Database
- **PostgreSQL**: Primary data store, connection via `DATABASE_URL` environment variable

### Authentication
- **Replit Auth**: OpenID Connect provider for user authentication
- **Required Environment Variables**: `ISSUER_URL`, `REPL_ID`, `SESSION_SECRET`, `DATABASE_URL`

### Key NPM Packages
- `drizzle-orm` / `drizzle-kit`: Database ORM and migration tooling
- `express-session` / `connect-pg-simple`: Session management
- `passport` / `openid-client`: Authentication middleware
- `@tanstack/react-query`: Frontend data fetching and caching
- `zod` / `drizzle-zod`: Runtime validation and schema generation
- `framer-motion`: Animation library
- `date-fns`: Date formatting utilities

### Development Tools
- `tsx`: TypeScript execution for development
- `esbuild`: Production bundling for server
- `vite`: Frontend development server and build tool