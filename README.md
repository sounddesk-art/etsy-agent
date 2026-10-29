# Sounddesk Etsy Agent

Private Etsy seller automation for creating coherent digital-product listings as drafts.

## Safety defaults
- Draft listings only
- No automatic publishing
- Minimum OAuth scopes: `listings_r listings_w listings_d shops_r`
- Shared secret and refresh token are never committed
- Copyright/IP imitation is forbidden; generic archetypes are allowed, recognizable franchise copies are not

## One-time Etsy setup

### 1. Redirect URL
In the Etsy Developer Portal, set the OAuth redirect URI exactly to:

`https://sounddesk-art.github.io/etsy-agent/oauth-callback.html`

Etsy requires an exact HTTPS redirect match.

### 2. GitHub Actions secrets
Open:

Repository → Settings → Secrets and variables → Actions → New repository secret

Create these three secrets:

- `ETSY_KEYSTRING`
- `ETSY_SHARED_SECRET`
- `ETSY_REFRESH_TOKEN`

Never put these values in a committed file.

### 3. Authorize the shop
Open:

`https://sounddesk-art.github.io/etsy-agent/oauth.html`

Enter only the Etsy API Keystring. The helper creates PKCE values locally and requests:

`listings_r listings_w listings_d shops_r`

After approval, the callback attempts to exchange the one-time authorization code for OAuth tokens. Copy the returned refresh token into the GitHub secret `ETSY_REFRESH_TOKEN`.

If the browser blocks token exchange, the callback displays the temporary code and PKCE verifier for a fallback exchange.

### 4. Test
Run GitHub Actions → **Etsy connection test** → Run workflow.

A successful run prints only non-secret connection information such as:
- user ID
- shop ID
- shop name
- granted scope

### 5. Create a draft
The agent writes a listing package JSON plus image/download assets into the repo/workspace.

Run GitHub Actions → **Create Etsy draft** and provide the listing-package JSON path.

The script:
1. refreshes OAuth access
2. discovers the authenticated seller's shop
3. creates a digital draft listing
4. uploads listing images
5. uploads digital files
6. leaves the listing as **draft**

It never activates/publishes the listing.

## Agent configuration
- `config/shop_profile.md`
- `config/style_guide.md`
- `config/niche_rules.md`
- `prompts/etsy_master_prompt.md`
- `data/niche_queue.csv`

## Continuous efficiency rule
After each production run, the agent should reduce redundant reasoning, duplicate research and unnecessary image generations while preserving or improving quality. Quality, commercial usefulness, IP safety and visual consistency always outrank token savings.
