# Star Wars Legion Unit Data (2.5 Live Dataset)

## Purpose
This repository provides **machine-readable data** for Star Wars: Legion (post-2.5 rules update), including:

- Unit stats (Rebel Alliance, Empire, etc.)
- Points costs (kept up to date with AMG changes)
- Keywords and abilities
- Genreal rules to play
- Upgrades

Designed for:
- AI / LLM usage
- army builders
- data analysis tools

---

## Data Structure Example

```json
{
  "name": "Darth Vader",
  "title": "Dark Lord of the Sith",
  "faction": "Galactic Empire",
  "rank": "Commander",
  "unit_type": "Trooper",
  "stats": {
    "health": 8,
    "courage": "Null",
    "speed": 1,
    "defense_die": "Red",
    "surges": {
      "attack": "Critical",
      "defense": "None"
    }
  },
  "keywords": [
    {
      "name": "Compel",
      "value": "Trooper"
    },
    {
      "name": "Deflect"
    },
    {
      "name": "Immune",
      "value": "Pierce"
    },
    {
      "name": "Master of the Force",
      "value": 1
    },
    {
      "name": "Relentless"
    }
  ],
  "weapons": [
    {
      "name": "Vader's Lightsaber",
      "range": "melee",
      "dice": {
        "red": 6,
        "black": 0,
        "white": 0
      },
      "keywords": [
        {
          "name": "Impact",
          "value": 3
        },
        {
          "name": "Pierce",
          "value": 3
        }
      ]
    }
  ],
  "upgrade_slots": {
    "Force": 3,
    "Command": 1
  }
}
  "upgrade_slots": {
    "Force": 3,
    "Command": 1
  }
}