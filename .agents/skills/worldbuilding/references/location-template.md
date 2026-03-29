# Location Template

Use this template when creating a new location file at `worldbuilding/locations/{location-name-kebab}.md`.

```yaml
---
name: "{Location Name}"
type: {city|town|village|fortress|ruins|wilderness|landmark|region|continent|building|other}
region: "{Parent Region}"
population: {number or estimate}
controlled-by: {character-kebab or faction}
notable-characters:
  - {character-kebab}
tags:
  - {tag-1}
  - {tag-2}
status: {thriving|declining|abandoned|contested|hidden}
time-states:
  - era: {Current Year/Era}
    description: {Brief state identifier}
---
```

## Description

What the location looks, sounds, smells, and feels like. First impressions for someone arriving. Key sensory details that make it distinct.

## History

How the location came to be and key events that happened here. Only include history relevant to the story.

## Culture & Customs

The people who live here, their way of life, traditions, social norms. What makes this place culturally distinct.

## Notable Features

Specific landmarks, buildings, natural features, or points of interest within the location. Things characters would interact with.

## Time-States (Dynamic History)

Locations change over the course of the story. Detail the location's state in different eras based on the timeline:

### [{Era 1 e.g., 1937 - Occupation}]
What the location looks and feels like during this period. Political situation, who controls it.

### [{Era 2 e.g., 1938 - Liberation}]
How the location has changed after a major plot event. New administrators, visual changes, etc.
