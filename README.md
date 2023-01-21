# Geopardie

Geopardie is a Discord bot used to play a Family-Feud style game.

# Game Modes

## Anonymous Poll

* Host asks, lists answers
* Players vote
* Host reveals results

## Family Feud

* Host asks
* Players submit text answers
* Host reveals results

# Usage

## Environment Variables

* `DISCORD_TOKEN` - Discord bot token

* `DEFAULT_GUILD_ID` - Discord guild ID

## Running

This entire repo is installable as a package which can be executed.

First time setup:

```bash
pip install git+https://github.com/itchono/geopardie
```

Afterwards:

```bash
python -m geopardie
```

Alternatively, if you are integrating this into some system that requires an entry point, use `src/geoardie/__main__.py` as the entry point.
