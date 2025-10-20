# Google Calendar API Setup Guide

This guide will help you set up Google Calendar API integration for Hiya Guard.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "Hiya Guard")
4. Click "Create"

## Step 2: Enable Google Calendar API

1. In your project dashboard, click "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: Hiya Guard
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Skip this (click "Save and Continue")
   - Test users: Add your Google account email
   - Click "Save and Continue"

4. Back to "Create OAuth client ID":
   - Application type: Desktop app
   - Name: Hiya Guard Desktop
   - Click "Create"

## Step 4: Download Credentials

1. After creating, you'll see your client ID and secret
2. Click "Download JSON"
3. Rename the downloaded file to `credentials.json`
4. Move `credentials.json` to your Hiya Guard project root directory

## Step 5: First-Time Authentication

1. Run the application: `python main.py`
2. A browser window will open automatically
3. Select your Google account
4. Click "Continue" (you may see a warning that the app isn't verified - this is normal for personal projects)
5. Click "Continue" again to grant permissions
6. The browser will show "The authentication flow has completed"
7. Close the browser and return to your terminal

## Step 6: Token Storage

After successful authentication:
- A `token.pickle` file will be created automatically
- This file contains your access token and refresh token
- Future runs will use this file (no browser auth needed)
- Token automatically refreshes when expired

## Troubleshooting

### "credentials.json not found"
- Make sure `credentials.json` is in the project root directory
- Check the filename spelling (must be exactly `credentials.json`)

### "Access blocked: Authorization Error"
- Make sure you added your email as a test user in OAuth consent screen
- Try setting OAuth consent screen to "Internal" if you have a Google Workspace account

### Token expired errors
- Delete `token.pickle` and run the application again to re-authenticate

## Security Notes

- Never commit `credentials.json` or `token.pickle` to version control
- These files are already in `.gitignore`
- Keep your credentials secure and private

