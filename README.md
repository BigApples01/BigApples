# BigApples

## Go live (static hosting)
This site is a single `index.html` plus the `Assets/` folder, so it can be deployed anywhere that hosts static files.

### 1) Update placeholders before deploying
Open `index.html` and replace:
- `PASTE_LEDGERSEDGE_LINK_HERE` with your real site URL.
- `YOUR_EMAIL_HERE` with your email address.

### 2) Deploy options
Pick one of the options below and follow the steps.

#### GitHub Pages
1. Push this repo to GitHub.
2. In GitHub, go to **Settings → Pages**.
3. Under **Build and deployment**, choose:
   - **Source:** Deploy from a branch
   - **Branch:** `main` (or the branch you pushed), **/ (root)**
4. Save. GitHub will publish a URL like `https://<user>.github.io/<repo>/`.

#### Netlify
1. Create a Netlify site from this GitHub repo (or drag-and-drop the folder).
2. Build settings:
   - **Build command:** (leave blank)
   - **Publish directory:** `/` (root)
3. Deploy and use the provided URL.

#### Vercel
1. Import the repo into Vercel.
2. Framework preset: **Other**.
3. Build command: none.
4. Output directory: `.` (root).
5. Deploy.
