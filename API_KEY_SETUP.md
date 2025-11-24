# API Key Setup Guide

This guide explains how to set up your Google GenAI API key for the Game Master Agent project.

## 🔑 Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (it starts with something like `AIza...`)

## 📍 Where to Add the API Key

### Option 1: Kaggle Notebooks (RECOMMENDED)

1. In your Kaggle notebook, click **Add** → **Secrets**
2. Click **Add new secret**
3. Set:
   - **Name**: `GOOGLE_GENAI_API_KEY`
   - **Value**: Your API key (paste it here)
4. Click **Save**
5. In the notebook, uncomment Option 1 in the API key configuration cell:

```python
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
api_key = user_secrets.get_secret("GOOGLE_GENAI_API_KEY")
```

### Option 2: Google Colab (RECOMMENDED)

1. In Colab, click the **key icon** (🔑) in the left sidebar
2. Click **Add new secret**
3. Set:
   - **Name**: `GOOGLE_GENAI_API_KEY`
   - **Value**: Your API key (paste it here)
4. Click **Save**
5. In the notebook, uncomment Option 2 in the API key configuration cell:

```python
from google.colab import userdata
api_key = userdata.get('GOOGLE_GENAI_API_KEY')
```

### Option 3: Direct in Code (NOT RECOMMENDED for sharing)

⚠️ **Warning**: Don't use this if you plan to share your notebook publicly!

In the notebook cell, uncomment and set:

```python
api_key = "your-api-key-here"  # Replace with your actual key
```

### Option 4: Environment Variable (Local Jupyter)

#### Method A: Terminal/Command Prompt

**Windows (PowerShell):**
```powershell
$env:GOOGLE_GENAI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_GENAI_API_KEY=your-api-key-here
```

**Mac/Linux:**
```bash
export GOOGLE_GENAI_API_KEY="your-api-key-here"
```

#### Method B: Create .env File

1. Create a file named `.env` in the project root directory
2. Add this line:
   ```
   GOOGLE_GENAI_API_KEY=your-api-key-here
   ```
3. The notebook will automatically load it with `load_dotenv()`

**Important**: Add `.env` to `.gitignore` to avoid committing your API key!

## ✅ Verify Setup

After setting your API key, run the configuration cell. You should see:

```
✅ API key configured successfully!
   Key preview: AIzaSy****...
```

If you see a warning instead, check:
- Did you uncomment the correct option for your platform?
- Is the API key name spelled correctly? (must be `GOOGLE_GENAI_API_KEY`)
- Did you save the secret/key properly?

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
   - Add `.env` to `.gitignore`
   - Don't hardcode keys in shared notebooks

2. **Use Secrets/Environment Variables**
   - Kaggle Secrets or Colab Secrets are the safest options
   - Environment variables are good for local development

3. **Rotate keys if exposed**
   - If you accidentally share a key, revoke it and create a new one

## 🆘 Troubleshooting

### "API key not set" error
- Make sure you uncommented the correct option for your platform
- Verify the secret/key name is exactly `GOOGLE_GENAI_API_KEY`
- Restart the kernel and run the cell again

### "Invalid API key" error
- Check that you copied the entire key (no extra spaces)
- Verify the key is active in Google AI Studio
- Make sure you're using a GenAI API key, not a different Google API key

### Key not loading from .env file
- Make sure `.env` is in the same directory as the notebook
- Check that the file is named exactly `.env` (not `.env.txt`)
- Verify the format: `GOOGLE_GENAI_API_KEY=your-key` (no spaces around `=`)

## 📚 Additional Resources

- [Google AI Studio](https://makersuite.google.com/app/apikey) - Get/manage API keys
- [Google GenAI Python SDK Docs](https://ai.google.dev/docs) - API documentation
- [Kaggle Secrets Guide](https://www.kaggle.com/docs/notebooks#secrets) - Kaggle-specific help

---

**Need help?** Check the notebook comments or refer to the README.md file.

