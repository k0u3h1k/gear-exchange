# Environment Variables Setup Guide

This file documents all environment variables needed for the Gear Exchange Hub application.

## Required Environment Variables

### Database Configuration
**DATABASE_URL**
- **Description**: PostgreSQL database connection string
- **Format**: `postgresql://username:password@host:port/database_name`
- **Example**: `postgresql://user:password@localhost:5432/gear_exchange_hub`
- **Required**: Yes
- **Notes**: Make sure your PostgreSQL server is running and accessible

### Session Security
**SESSION_SECRET**
- **Description**: Secret key used to sign and encrypt session cookies
- **Format**: Any random string (minimum 32 characters recommended)
- **Example**: `your_super_secret_session_key_change_this_in_production`
- **Required**: Yes
- **Notes**: Generate a secure random string for production. You can use: `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`

### Server Configuration
**PORT**
- **Description**: Port number the server will listen on
- **Format**: Number
- **Example**: `5000`
- **Required**: No (defaults to 5000)
- **Notes**: Make sure this port is not already in use

**NODE_ENV**
- **Description**: Application environment mode
- **Format**: `development` or `production`
- **Example**: `development`
- **Required**: No (defaults to development)
- **Notes**: Set to `production` when deploying to production servers

## Setup Instructions

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file** with your actual values:
   - Replace the DATABASE_URL with your PostgreSQL connection string
   - Generate a secure SESSION_SECRET
   - Adjust PORT if needed

3. **Verify your database is running**:
   ```bash
   # For local PostgreSQL
   psql -U your_username -d gear_exchange_hub
   ```

4. **Run database migrations**:
   ```bash
   npm run db:push
   ```

## Security Notes

⚠️ **IMPORTANT**: 
- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- Use different secrets for development and production
- Rotate your SESSION_SECRET periodically in production

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `pg_isready`
- Check your connection string format
- Ensure the database exists: `createdb gear_exchange_hub`
- Verify user permissions

### Session Issues
- Make sure SESSION_SECRET is set
- Clear browser cookies if experiencing login issues
- Check that the sessions table exists in your database
