# Sounddesk Etsy Agent

Private Etsy seller automation for creating coherent digital-product listings as drafts.

## Safety defaults
- Draft listings only
- No automatic publishing
- Normal draft-operation OAuth scopes: `listings_r listings_w shops_r`
- `listings_d` is optional and only needed for an explicitly owner-approved API deletion/cleanup
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

`listings_r listings_w shops_r`

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


## Cross-chat and resource-reuse rule

Before requesting Etsy setup, OAuth reauthorization, a new secret, manual upload, or a replacement workflow, first inspect the existing repository, GitHub Actions, current granted scopes, recent successful runs, Drive archive and the private `sounddesk-art/enterprise-agent` bootstrap rules.

Do not ask the owner to reauthorize merely because `listings_d` is absent. Normal draft creation/editing does not require delete scope. If deletion is not part of the current task, continue with the existing draft workflow.

The canonical general rule is maintained in `sounddesk-art/enterprise-agent/docs/CROSS_CHAT_BOOTSTRAP.md`.

## Image asset storage standard

Google Drive is the durable archive for generated Etsy image masters. GitHub is only temporary staging when the Etsy workflow needs repository-local files.

Standard path:

```text
Generate/approve image in ChatGPT
→ assign stable numbered filename
→ archive original in Google Drive
→ copy temporarily into GitHub staging
→ create Etsy listing as DRAFT only
→ verify Etsy listing ID, image upload and digital file upload
→ remove temporary GitHub image binary
→ keep Drive archive + small GitHub manifest/audit metadata
```

Rules:

- Never delete the Drive archive automatically as part of GitHub cleanup.
- Never remove the temporary GitHub image until the Etsy draft and required uploads are verified.
- Keep titles, tags, descriptions, Drive references, checksums/status and Etsy listing IDs in lightweight manifests where useful.
- Large image binaries should not remain permanently in GitHub unless there is a specific documented reason.
- Draft creation is allowed inside the approved Etsy experiment; activation/publication remains disabled unless separately approved.

## Bulk generation and timeout-safe operation

Etsy image jobs follow the Sounddesk bulk standard in sounddesk-art/enterprise-agent/docs/BULK_TIMEOUT_EXECUTION.md.

Default behavior for large ChatGPT-generated image jobs:

1. Treat the full request as one master job.
2. Split generation into deterministic batches of up to 10 images.
3. Number files globally across the master job, not separately per chat.
4. Upload each completed batch to Google Drive immediately.
5. Persist/update the master manifest after every batch.
6. Never regenerate a batch already durably archived and verified.
7. When the owner asks for generation first, use collect_then_process:
   - generate all requested batches;
   - confirm ALL_ASSETS_READY;
   - only then trigger the Drive/GitHub/Hetzner -> Etsy draft workflow.
8. The external workflow may continue independently of the chat after it is triggered.
9. A chat timeout is not an owner action. Resume from Drive + manifests.
10. Notify the owner only at complete master-job success or when a verified owner-only blocker exists, when low-interruption execution was requested.

Recommended master-job state lives in lightweight JSON manifests. Full-resolution images remain in Drive; GitHub stores only temporary staging binaries plus durable lightweight state/receipts.
