---
layout: default
title: Home
---

# Portfolio

Welcome to my GitHub Pages site. For detailed information regarding my enhancement plan to each artifact, [click this link](https://github.com/Finnegan2024/Finnegan2024.github.io/blob/main/enhancement_plan.md).

For an overview of my professional assessment, [click this link](https://github.com/Finnegan2024/Finnegan2024.github.io/blob/main/professional_assessment.md).

## Posts

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
      <small>— {{ post.date | date: "%B %d, %Y" }}</small>
    </li>
  {% endfor %}
</ul>
