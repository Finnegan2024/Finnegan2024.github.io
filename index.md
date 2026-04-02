---
layout: default
title: Home
---

# Portfolio

Welcome to my GitHub Pages site.

## Posts

<ul>
  {% raw %}{% for post in site.posts %}{% endraw %}
    <li>
      <a href="{% raw %}{{ post.url }}{% endraw %}">{% raw %}{{ post.title }}{% endraw %}</a>
      <small>— {% raw %}{{ post.date | date: "%B %d, %Y" }}{% endraw %}</small>
    </li>
  {% raw %}{% endfor %}{% endraw %}
</ul>
