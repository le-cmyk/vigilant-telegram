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
  const CLIENT_ID = "YOUR_CLIENT_ID_HERE";
  const REDIRECT_URI = window.location.origin + '/oauth-callback.html';
  const SCOPE = "repo";

  async function handleOAuthCallback() {
    const params = new URLSearchParams(location.search);
    if (params.has('code')) {
      const code = params.get('code');
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
        location.href = `https://github.com/login/oauth/authorize?client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${SCOPE}`;
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
      await octokit.request('POST /repos/{owner}/{repo}/issues', { owner: '<your-username>', repo: '<your-repo>', title: `[Add Plant] ${name}`, labels: ['add-plant'], body: `name: ${name}\nstart_date: ${start}\nfrequency_days: ${freq}` });
      document.getElementById('status').textContent = '✅ Add request sent.';
      e.target.reset();
    };
    document.getElementById('remove-form').onsubmit = async e => {
      e.preventDefault();
      const name = document.getElementById('name-remove').value;
      document.getElementById('status').textContent = 'Sending remove request…';
      await octokit.request('POST /repos/{owner}/{repo}/issues', { owner: '<your-username>', repo: '<your-repo>', title: `[Remove Plant] ${name}`, labels: ['remove-plant'], body: `name: ${name}` });
      document.getElementById('status').textContent = '✅ Remove request sent.';
      e.target.reset();
    };
  }

  initUI();
</script>
