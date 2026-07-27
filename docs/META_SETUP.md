# Meta setup — getting the Page + Instagram keys

**Do this at the PC.** Takes about 20–30 minutes. You only do it once.

---

## First, the thing people get wrong

**You never give this system your Facebook username or password.**
Nowhere. Not in a file, not in a message, not to an agent. Meta does not
let apps log in that way, and anything that asks you for your password is
either broken or a scam.

What you get instead is an **access token** — a long random string that
means:

> *"This one app may post to THIS Page and THIS Instagram account, and
> nothing else."*

You can revoke it at any time from Facebook settings, and revoking it
changes nothing about your personal account. That is the whole point.

## What you need before starting

- [ ] A Facebook **Page** for the business (not your personal profile)
- [ ] An **Instagram Business** or **Creator** account
      (Instagram app → Settings → Account type → switch to Business — free)
- [ ] The Instagram account **linked to the Page**
      (Page → Settings → Linked accounts → Instagram)

The link in step 3 is the part most people miss, and without it the
Instagram half simply will not work.

## Do NOT create an ad account

You will see Meta invite you to set up billing and run ads. **Skip all of
it.** Meta prohibits paid promotion of smoking paraphernalia, and this
system enforces that ban in code (`POLICY-META-ADS-001`). We post
organically to our own Page, Instagram and groups. No ad account means no
accidental spend and nothing to get banned.

---

## Step 1 — Create the app

1. Go to **developers.facebook.com** → log in with your normal Facebook
   account (this is just to identify you — it is not shared with anything).
2. Top right: **My Apps** → **Create App**.
3. Use case: choose **Other** → app type **Business**.
4. Name it something obvious like `Faridunhill Poster`. Only you see this.
5. Create it. You now land on the app dashboard.

## Step 2 — Add the products

On the dashboard, find and **Add** these two:

- **Facebook Login for Business**
- **Instagram Graph API**

You do not need to configure them beyond adding them.

## Step 3 — Collect the four values

Write these down as you go. Four values, that is all.

| # | Value | Where to find it |
|---|---|---|
| 1 | **App ID** | App dashboard → Settings → Basic (a long number) |
| 2 | **App Secret** | Same page → click **Show** next to App Secret |
| 3 | **Page Access Token** | See below — Graph API Explorer |
| 4 | **Instagram Business Account ID** | See below — Graph API Explorer |

### Getting the Page Access Token (#3)

1. Go to **Tools → Graph API Explorer** (top-right menu on the dashboard).
2. In the right panel, **Meta App** = the app you just made.
3. Click **Generate Access Token** → approve the popup → pick your Page.
4. Under **Permissions**, add these five:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_content_publish`
5. Click **Generate Access Token** again so the permissions apply.
6. Copy the long string. **That is your Page Access Token.**

### Getting the Instagram Business Account ID (#4)

Still in Graph API Explorer, put this in the query box and press Send:

```
me/accounts?fields=name,instagram_business_account
```

In the response, find your Page and copy the `instagram_business_account`
→ `id` value. It is a long number. **That is #4.**

If `instagram_business_account` is missing, the Instagram account is not
linked to the Page — go back and do that (see prerequisites), then retry.

## Step 4 — Make the token long-lived

The token from Step 3 expires in about **1 hour**. Swap it for one that
lasts ~60 days. In Graph API Explorer, run:

```
oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN
```

Replace `APP_ID`, `APP_SECRET` and `SHORT_TOKEN` with your values. The
response contains a new, longer token — **use that one**.

> Page tokens derived from a long-lived user token generally do not
> expire, but treat ~60 days as the assumption and re-check if posting
> starts failing with an auth error.

## Step 5 — Put them on the PC (never in the repo)

Create a file called `.env` in the project folder:

```
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here
META_PAGE_ACCESS_TOKEN=your_long_lived_token_here
META_PAGE_ID=your_page_id_here
META_IG_BUSINESS_ID=your_instagram_business_id_here
```

`.env` is already in `.gitignore`, so it never reaches GitHub. Do not
paste these values into chat, a commit, or an issue. If one leaks, go to
App Dashboard → Settings → Basic → **Reset App Secret**, and the old one
dies immediately.

## Step 6 — Tell the builder

Say **"Meta credentials are on the PC"** and the publisher gets switched
from `DryRunPublisher` (records what it *would* post, touches nothing)
to the live one. Until then the system stays in dry-run — by design, so
nothing posts by accident while you are mid-setup.

---

## Review before going live

Meta may ask for **App Review** before `pages_manage_posts` and
`instagram_content_publish` work for a wider audience. For posting to a
Page **you own**, the token usually works immediately in development
mode — which is our whole use case. If a post is rejected with a
permissions error, that is the App Review prompt, and it is a form you
fill in describing what the app does ("posts our own product photos to
our own Page").

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `instagram_business_account` missing | IG not linked, or still a personal account | Switch IG to Business, link to the Page |
| Token works then dies after an hour | Skipped Step 4 | Do the long-lived exchange |
| `(#200) Permissions error` | Missing scope | Re-generate the token with all five permissions |
| `(#10) requires permission` | Needs App Review | Submit the review form, or verify you own the Page |

## Rate limits (why the walls exist)

Meta allows roughly **25 Instagram posts per 24 hours** per account, and
throttles Pages that post aggressively. Our standing wall of **1 post per
group per day** sits far below anything Meta objects to. Any account
warning pauses the channel and emails you — one email, no silent retries.
