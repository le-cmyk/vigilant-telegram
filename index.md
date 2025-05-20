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
