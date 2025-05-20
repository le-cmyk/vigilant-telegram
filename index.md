---
layout: default
---

# 🌱 Plant Watering Schedule

| Plant      | Last Watered | Frequency (days) | Next Watering |
| ---------- | ------------ | ---------------- | ------------- |
{% raw %}{% for p in site.data.plants.plants %}{% endraw %}
| **{{ p.name }}** | {{ p.last_watered }} | {{ p.frequency_days }} |{% raw %}
  {% assign last = p.last_watered | date: "%s" %}
  {% assign next = last | plus: p.frequency_days | times: 86400 %}
  {{ next | date: "%Y-%m-%d" }} {% endraw %}|
{% raw %}{% endfor %}{% endraw %}

---

<section id="manage-plants">
  <h2>🌿 Manage Plants</h2>
  <button onclick="showAdd()">Add a New Plant</button>
  <button onclick="showRemove()">Remove a Plant</button>

  <form id="add-form" style="display:none">
    <h3>Add Plant</h3>
    <label>Name <input type="text" id="name-add" required></label>
    <label>Start date <input type="date" id="start_date-add" required></label>
    <label>Frequency (days) <input type="number" id="frequency_days-add" required min="1"></label>
    <button type="submit">Add</button>
  </form>

  <form id="remove-form" style="display:none">
    <h3>Remove Plant</h3>
    <label>Name <input type="text" id="name-remove" required placeholder="Exact plant name"></label>
    <button type="submit">Remove</button>
  </form>

  <div id="status"></div>
</section>

<script src="https://cdn.jsdelivr.net/npm/@octokit/core/dist-web/index.js"></script>
<script>
  const CLIENT_ID = "YOUR_CLIENT_ID_HERE"; // You still need to replace this if using OAuth form
  const REDIRECT_URI = window.location.origin + '/oauth-callback.html';
  const SCOPE = "repo";

  async function handleOAuthCallback() {
    const params = new URLSearchParams(location.search);
    if (params.has('code')) {
      const code = params.get('code');
      // You still need to replace this if using OAuth form
      const resp = await fetch(`https://your-token-exchange.example.com/exchange?code=${code}`);
      const { token } = await resp.json();
      localStorage.setItem('gh_token', token);
      window.location.href = '/';
    }
  }

  function showAdd() {
    document.getElementById('add-form').style.display = 'block';
    document.getElementById('remove-form').style.display = 'none';
  }
  function showRemove() {
    document.getElementById('remove-form').style.display = 'block';
    document.getElementById('add-form').style.display = 'none';
  }

  function initUI() {
    handleOAuthCallback().then(() => {
      const token = localStorage.getItem('gh_token');
      if (!token) {
        // Consider if OAuth flow should be initiated automatically or via a button
        // location.href = `https://github.com/login/oauth/authorize?client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${SCOPE}`;
      } else {
        setupForms(token);
      }
    });
  }

  function setupForms(token) {
    const octokit = new Octokit.Core({ auth: token });
    document.getElementById('add-form').onsubmit = async e => {
      e.preventDefault();
      const name = document.getElementById('name-add').value;
      const start = document.getElementById('start_date-add').value;
      const freq = document.getElementById('frequency_days-add').value;
      document.getElementById('status').textContent = 'Sending add request…';
      await octokit.request('POST /repos/{owner}/{repo}/issues', { owner: 'le-cmyk', repo: 'vigilant-telegram', title: `[Add Plant] ${name}`, labels: ['add-plant'], body: `name: ${name}\nstart_date: ${start}\nfrequency_days: ${freq}` });
      document.getElementById('status').textContent = '✅ Add request sent.';
      e.target.reset();
    };
    document.getElementById('remove-form').onsubmit = async e => {
      e.preventDefault();
      const name = document.getElementById('name-remove').value;
      document.getElementById('status').textContent = 'Sending remove request…';
      await octokit.request('POST /repos/{owner}/{repo}/issues', { owner: 'le-cmyk', repo: 'vigilant-telegram', title: `[Remove Plant] ${name}`, labels: ['remove-plant'], body: `name: ${name}` });
      document.getElementById('status').textContent = '✅ Remove request sent.';
      e.target.reset();
    };
  }

  // Check if OAuth is intended before automatically redirecting or setting up forms
  // For now, let's assume the user might not have OAuth set up, so we don't auto-redirect.
  // If you have CLIENT_ID and the exchange endpoint, you can uncomment the redirect in initUI.
  // initUI(); // Call this if you want the OAuth flow to start or forms to be active
  
  // Fallback or alternative: If not using OAuth, the forms won't work.
  // Consider adding a message here if OAuth is not configured.
  // Or, if OAuth is optional, ensure the page is still useful without it.
  // For now, the buttons will show, but forms won't submit without a token.
  // You might want to hide the forms or provide a login button if no token.
  
  // If you want to enable the forms without OAuth immediately (e.g. for testing issue creation directly)
  // you would need a different mechanism or a pre-configured token, which is not secure for client-side.
  // The current design relies on OAuth for the site forms.
  // The GitHub Issue forms will work independently.

  // To make the "Add" and "Remove" buttons visible and forms functional *if* a token exists (e.g. from a previous OAuth login):
  if (localStorage.getItem('gh_token')) {
    setupForms(localStorage.getItem('gh_token'));
  } else {
    // Optionally, guide user to log in or explain that forms are disabled.
    // For example, disable buttons or show a message:
    // document.getElementById('status').textContent = "Please log in via GitHub to manage plants from this page.";
    // Or, if you want to attempt OAuth flow:
    // initUI();
  }
  // Making showAdd/showRemove globally accessible for the buttons
  window.showAdd = showAdd;
  window.showRemove = showRemove;

</script>
