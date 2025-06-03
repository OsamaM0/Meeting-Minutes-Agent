# Setting Up Gmail Authentication

This guide will help you set up Gmail authentication for the Meeting Minutes application.

## Error Message You're Seeing

If you're seeing an error message in Arabic that says:
> وإذا كان مطوِّر التطبيق أنت، عليك تسجيل معرّف الموارد المنتظم (URI) الخاص بإعادة التوجيه في Google Cloud Console.

This translates to:
> If you are the application developer, you need to register the redirect URI in Google Cloud Console.

## Steps to Fix the Issue

### 1. Update Your Google Cloud Console Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **API & Services** > **Credentials**
3. Find your OAuth 2.0 Client ID and click the edit button (pencil icon)
4. In the **Authorized redirect URIs** section, add:
   ```
   http://localhost:62366
   ```
5. Click **Save**

### 2. Update Your Local Credentials File

You have two options:

#### Option 1: Use the Fix Script

Run the fix_gmail_credentials.py script:
```bash
python fix_gmail_credentials.py
```

#### Option 2: Manual Update

1. Open the credentials.json file in your text editor
   (Located at `src/meeting_minutes/crews/gmailcrew/tools/credentials.json`)
2. Make sure the "redirect_uris" array includes `"http://localhost:62366"`
3. Save the file

### 3. Test Your Gmail Authentication

Run the Gmail authentication test:
```bash
python test_gmail_auth.py
```

This will verify that your authentication flow is working correctly.

### 4. Common Issues and Solutions

1. **Port is already in use**:
   - Change the port in `src/meeting_minutes/config/app_config.py` to an available port
   - Make sure to update both LLM_SERVER and GOOGLE_OAUTH port settings
   - Update your Google Cloud Console settings with the new port

2. **Token expired error**:
   - Delete the `token.json` file in `src/meeting_minutes/crews/gmailcrew/tools/` folder
   - Run the test again to generate a fresh token

3. **Permission errors**:
   - Make sure you've enabled the Gmail API in your Google Cloud project
   - Ensure the scopes in the script match the ones approved in your Google Cloud project
