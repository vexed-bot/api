# Vex V2.4

A fluent, minimal builder library for Discord Components V2 (Layout Views) in Python. Vex wraps the discord.py V2 primitives with chainable APIs and ships with paginators, confirmation flows, modals, entity pickers, argument converters, cooldown utilities, a command help registry, wizards, live views, polls, and a full theming system.

Vex is a single file with no extra dependencies beyond discord.py.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core View](#core-view)
- [Builders](#builders)
  - [ButtonBuilder](#buttonbuilder)
  - [SelectBuilder](#selectbuilder)
  - [SelectOptionBuilder](#selectoptionbuilder)
  - [TypedSelectBuilder](#typedselectbuilder)
  - [ActionRowBuilder](#actionrowbuilder)
  - [SectionBuilder](#sectionbuilder)
  - [GalleryBuilder](#gallerybuilder)
  - [ContainerBuilder](#containerbuilder)
  - [FileBuilder](#filebuilder)
  - [TableBuilder](#tablebuilder)
  - [TextInputBuilder](#textinputbuilder)
  - [ModalBuilder](#modalbuilder)
  - [PollBuilder](#pollbuilder)
- [Commands and Checks](#commands-and-checks)
- [Converters](#converters)
- [Bot and Cog](#bot-and-cog)
- [Pagination](#pagination)
- [Confirmation Flows](#confirmation-flows)
- [Choice and Select Prompts](#choice-and-select-prompts)
- [Entity Pickers](#entity-pickers)
- [Modals](#modals)
- [Wizard](#wizard)
- [Live View](#live-view)
- [Media Collector](#media-collector)
- [Help Registry](#help-registry)
- [Cooldowns](#cooldowns)
- [Utility Cards](#utility-cards)
- [Themes](#themes)
- [Presence](#presence)
- [Persistence](#persistence)
- [Error Constants](#error-constants)
- [Utility Functions](#utility-functions)
- [Factory Functions](#factory-functions)
- [License](#license)

## Installation

Vex is distributed as a single file. Download `vex.py` and place it in your bot's main directory, next to the file that starts your bot.

```
your-bot/
  main.py
  vex.py
  requirements.txt
  cogs/
    tickets.py
    giveaways.py
```

Because `vex.py` sits beside `main.py`, you can `import vex` from anywhere in your project. No pip install or package step is required.

## Quick Start

```python
import vex

view = (
    vex.vex()
    .h2("Hello World")
    .text("This is a Components V2 message.")
    .button(
        vex.button()
        .label("Click me")
        .primary()
        .on_click(lambda i: i.response.send_message("Clicked!", ephemeral=True))
    )
)

await view.send_to(channel)
```

## Core View

### Vex

Inherits `discord.ui.LayoutView`. The primary canvas for V2 messages.

| Method | Description |
|--------|-------------|
| `lock_to(*user_ids, message="...")` | Restrict interaction to specific user IDs. |
| `unlock()` | Remove the user lock. |
| `on_timeout_do(callback)` | Set a coroutine or callable to run on timeout. |
| `text(content, id=None)` | Add a `TextDisplay` component. |
| `write / line / paragraph / display / label / put / emit` | Aliases for `text`. |
| `heading(content, level=1, id=None)` | Add a markdown heading. |
| `h1 / h2 / h3` | Shorthand for `heading` with fixed levels. |
| `bold(content, id=None)` | Bold text. |
| `italic(content, id=None)` | Italic text. |
| `underline(content, id=None)` | Underlined text. |
| `strikethrough(content, id=None)` | Strikethrough text. |
| `code(content, lang="", id=None)` | Code block. |
| `inline_code(content, id=None)` | Inline code. |
| `quote / blockquote(content, id=None)` | Blockquote line. |
| `field(name, value, id=None)` | Key-value line. |
| `kv(key, value, id=None)` | Alias for `field`. |
| `fields(mapping)` | Batch add fields from a dict. |
| `mention_user(user_id, id=None)` | User mention string. |
| `mention_role(role_id, id=None)` | Role mention string. |
| `mention_channel(channel_id, id=None)` | Channel mention string. |
| `timestamp(dt_or_ts, fmt="f", id=None)` | Discord timestamp. |
| `relative(dt_or_ts, id=None)` | Relative timestamp. |
| `separator(large=False, visible=True, id=None)` | Add a `Separator`. |
| `divider / rule / hr` | Visible separator aliases. |
| `gap / spacer / pad` | Invisible separator aliases. |
| `large_separator / large_divider / large_gap / small_separator` | Size shorthands. |
| `section(builder)` | Add a built `Section`. |
| `aside / panel / sidebar` | Aliases for `section`. |
| `action_row(builder)` | Add a built `ActionRow`. |
| `row / buttons / controls / toolbar / actions` | Aliases for `action_row`. |
| `gallery(builder)` | Add a built `MediaGallery`. |
| `images / media / photos / grid` | Aliases for `gallery`. |
| `container(builder)` | Add a built `Container`. |
| `box / card / block / frame / embed / group / wrap` | Aliases for `container`. |
| `send_to(target, content=None, files=None, allowed_mentions=None)` | Send to a messageable. |
| `send / dispatch / publish / post` | Aliases for `send_to`. |
| `reply_to(interaction, ephemeral=False, files=None, allowed_mentions=None)` | Reply to an interaction. |
| `respond / answer / reply / fire` | Aliases for `reply_to`. |
| `edit(interaction, allowed_mentions=None)` | Edit the interaction message. |
| `update / patch / refresh / mutate` | Aliases for `edit`. |
| `defer(interaction, ephemeral=False, thinking=False)` | Safely defer. |
| `delete(interaction)` | Safely delete the interaction response. |
| `cooldown(rate, per, bucket=BucketType.user)` | Attach a cooldown mapping. |
| `slow / limit / throttle / ratelimit` | Aliases for `cooldown`. |
| `reset_cooldown(message)` | Reset the cooldown bucket. |
| `clear_cooldown(message)` | Alias for `reset_cooldown`. |
| `get_cooldown(message)` | Get the `Cooldown` bucket. |
| `is_cooled(message)` | Check if currently rate-limited. |
| `retry_after(message)` | Get remaining cooldown seconds. |

## Builders

### ButtonBuilder

Chainable builder for `discord.ui.Button`.

| Method | Description |
|--------|-------------|
| `label(text)` / `text / caption / title / name` | Set the button label. |
| `primary()` / `blurple / blue` | Set style to primary. |
| `secondary()` / `grey / gray / muted` | Set style to secondary. |
| `success()` / `green / confirm / positive` | Set style to success. |
| `danger()` / `red / destructive / negative / warning` | Set style to danger. |
| `premium(sku_id)` / `sku(sku_id)` | Set style to premium with a SKU. |
| `link(url)` / `url / href / navigate` | Set style to link with a URL. |
| `emoji(value)` / `icon / reaction` | Set emoji. |
| `disabled(state=True)` / `locked / inactive` | Disable the button. |
| `enabled(state=True)` / `unlocked / active` | Enable the button. |
| `row(value)` / `position / slot` | Set the action row slot. |
| `id(value)` | Set component ID. |
| `custom_id(value)` / `cid` | Set custom ID. |
| `on_click(callback)` / `handler / action / callback` | Attach an interaction callback. |
| `once()` / `fire_once / single_use` | Allow the callback to fire only once. |
| `debounce(seconds)` / `throttle / cooldown(seconds)` | Rate-limit clicks per user. |
| `busy(message)` | Show a temporary busy message while the handler runs. |
| `build()` | Return `discord.ui.Button`. |

### SelectBuilder

Chainable builder for `discord.ui.Select` (string select).

| Method | Description |
|--------|-------------|
| `option(label, value)` | Start a `SelectOptionBuilder`. |
| `add(label, value, description=None, emoji=None, default=False)` | Add an option directly. |
| `choice / item` | Aliases for `add`. |
| `placeholder(text)` / `hint / prompt` | Set placeholder. |
| `custom_id(value)` / `cid` | Set custom ID. |
| `min(value)` | Set `min_values`. |
| `max(value)` | Set `max_values`. |
| `range(min_val, max_val)` | Set both values. |
| `multi(max_val=25)` | Set `max_values` for multi-select. |
| `disabled(state=True)` / `locked` | Disable the select. |
| `row(value)` | Set row slot. |
| `on_select(callback)` / `handler / callback` | Attach callback. |
| `build()` | Return `discord.ui.Select`. |

### SelectOptionBuilder

| Method | Description |
|--------|-------------|
| `description(text)` / `desc` | Set option description. |
| `emoji(value)` / `icon` | Set option emoji. |
| `default(state=True)` / `selected` | Mark as default. |
| `build()` | Return `discord.SelectOption`. |

### TypedSelectBuilder

Builder for `ChannelSelect`, `UserSelect`, `RoleSelect`, and `MentionableSelect`.

| Method | Description |
|--------|-------------|
| `placeholder / hint / prompt` | Set placeholder. |
| `custom_id / cid` | Set custom ID. |
| `min / max / range / multi` | Value constraints. |
| `channel_types(*types)` | Restrict channel types. |
| `text_only()` | Restrict to text channels. |
| `voice_only()` | Restrict to voice channels. |
| `defaults(values)` | Set default selected values. |
| `disabled / locked` | Disable. |
| `row(value)` | Set row. |
| `on_select / handler / callback` | Attach callback. |
| `build()` | Return the typed select instance. |

### ActionRowBuilder

| Method | Description |
|--------|-------------|
| `add / push / insert / append / put / attach(item)` | Add a button or select. |
| `button(builder)` / `btn` | Build and add a `ButtonBuilder`. |
| `select(builder)` / `dropdown` | Build and add a `SelectBuilder`. |
| `channel_select / user_select / role_select / mentionable_select(builder)` | Build and add typed selects. |
| `id(value)` | Set component ID. |
| `build()` | Return `discord.ui.ActionRow`. |

### SectionBuilder

Builds `discord.ui.Section` (a text list plus an accessory).

| Method | Description |
|--------|-------------|
| `text / line / write / paragraph / add / put / push(content)` | Add text lines. |
| `display(item)` | Add a `TextDisplay` directly. |
| `bold / italic(content)` | Styled text. |
| `code(content, lang="")` | Code block. |
| `quote(content)` | Blockquote. |
| `heading(content, level=2)` | Heading. |
| `accessory(item)` / `aside / attachment` | Set accessory (button or thumbnail). |
| `thumbnail(url, description="", spoiler=False, id=None)` | Set a thumbnail accessory. |
| `image / photo / icon / avatar` | Aliases for `thumbnail`. |
| `button_accessory(builder)` / `button` | Build a button and set as accessory. |
| `id(value)` | Set component ID. |
| `build()` | Return `discord.ui.Section`. |

### GalleryBuilder

Builds `discord.ui.MediaGallery`.

| Method | Description |
|--------|-------------|
| `add(media, description="", spoiler=False)` | Add a `MediaGalleryItem`. |
| `image / animated / gif / photo / media` | Aliases for `add` with a URL. |
| `attach / upload(file, description="")` | Add a `discord.File`. |
| `push / insert / append` | Aliases for `add` with a URL. |
| `spoiler / hidden(url, description="")` | Add with `spoiler=True`. |
| `id(value)` | Set component ID. |
| `build()` | Return `discord.ui.MediaGallery`. |

### ContainerBuilder

Builds `discord.ui.Container`, the V2 card wrapper.

| Method | Description |
|--------|-------------|
| `add / push / append / insert / attach(component)` | Add any resolved component. |
| `text / write / line / paragraph / display(content, id=None)` | Add `TextDisplay`. |
| `heading / h1 / h2 / h3` | Add headings. |
| `bold / italic / underline / strikethrough` | Styled text. |
| `code / inline_code` | Code blocks. |
| `quote` | Blockquote. |
| `field / kv(name, value)` | Key-value line. |
| `fields(mapping)` | Batch fields. |
| `separator(large=False, visible=True, id=None)` | Add separator. |
| `divider / rule / gap / spacer / large_separator / large_divider / large_gap / small_separator` | Separator aliases. |
| `section(builder)` | Add a `SectionBuilder`. |
| `action_row(builder)` / `row` | Add an `ActionRowBuilder`. |
| `button(builder, inline=True)` | Add a button, auto-bundled into an inline `ActionRow` when possible. |
| `btn` | Alias for `button`. |
| `gallery(builder)` | Add a `GalleryBuilder`. |
| `file(builder)` | Add a `FileBuilder`. |
| `table(builder)` | Add a rendered `TableBuilder`. |
| `nest / child / inner(builder)` | Nest a `ContainerBuilder`. |
| `accent(color)` / `color / colour / border / tint / hue` | Set accent color. |
| `hex(value)` | Set accent from a hex string. |
| `rgb(r, g, b)` | Set accent from RGB. |
| `spoiler / hidden(state=True)` | Mark as spoiler. |
| `id(value)` | Set component ID. |
| `build()` | Return `discord.ui.Container`. |

### FileBuilder

Builds `discord.ui.File`, which renders an attached file inside a V2 message.

| Method | Description |
|--------|-------------|
| `reference(filename)` / `ref / name` | Reference an uploaded file by `attachment://filename`. |
| `url(value)` | Reference a file by URL. |
| `source(media)` | Set the media source directly. |
| `spoiler(state=True)` | Mark as spoiler. |
| `id(value)` | Set component ID. |
| `build()` | Return `discord.ui.File`. |

### TableBuilder

Renders aligned tabular text for use inside a container or text display.

| Method | Description |
|--------|-------------|
| `headers(*names)` | Set column headers. |
| `row(*cells)` | Add a row of cells. |
| `rows(iterable)` | Add multiple rows. |
| `align(*modes)` | Per-column alignment. |
| `build()` | Return the rendered string. |

### TextInputBuilder

Builds `discord.ui.TextInput` for modals.

| Method | Description |
|--------|-------------|
| `label(text)` | Set label. |
| `short()` / `line` | Set style to short. |
| `paragraph()` / `long / multiline` | Set style to paragraph. |
| `placeholder / hint(text)` | Set placeholder. |
| `default / prefill(text)` | Set default value. |
| `required(state=True)` | Set required. |
| `optional()` | Set not required. |
| `min / max / length(min, max)` | Length constraints. |
| `build()` | Return `discord.ui.TextInput`. |

### ModalBuilder

Builds a `discord.ui.Modal`.

| Method | Description |
|--------|-------------|
| `title / name(text)` | Set modal title. |
| `timeout(seconds)` | Set timeout. |
| `custom_id / cid(value)` | Set custom ID. |
| `field(key, label, **kwargs)` | Add a text input field. |
| `short(key, label, **kwargs)` | Add a short field. |
| `paragraph(key, label, **kwargs)` | Add a paragraph field. |
| `input / add(builder)` | Add a `TextInputBuilder`. |
| `on_submit / handler(callback)` | Set submit callback `(interaction, values_dict)`. |
| `on_error(callback)` | Set error callback. |
| `build()` | Return the modal instance. |
| `send / open / prompt(interaction)` | Send the modal. |

### PollBuilder

Builds a native Discord poll.

| Method | Description |
|--------|-------------|
| `question(text)` | Set the poll question. |
| `answer(text, emoji=None)` / `option / choice` | Add an answer. |
| `duration(hours)` | Set how long the poll runs. |
| `multiple(state=True)` | Allow multiple selections. |
| `build()` | Return the `discord.Poll`. |

## Commands and Checks

Vex provides decorators for slash, hybrid, and grouped commands, plus checks that apply to both application and prefix commands. Inside a `vex.Cog` these register automatically.

### Command Decorators

| Decorator | Description |
|-----------|-------------|
| `slash_cmd(name=None, description=None, guild=None, guilds=None, nsfw=False, category=None)` | Define an application (slash) command. |
| `hybrid_cmd(name=None, description=None, aliases=None, ...)` | Define a command usable as slash and prefix. |
| `slash_group(name, description="...", guild_only=False, nsfw=False)` | Create a slash command group. Aliases: `group`, `command_group`. |
| `hybrid_group(name, ...)` | Create a hybrid command group. |
| `cmd(name=None, aliases=None)` | Define a classic prefix command. |

A `SlashGroup` exposes its own `.slash_cmd()` for subcommands, producing commands like `/panel create`. Discord allows a single level of nesting, so a group's subcommands cannot themselves be groups.

### Checks

| Check | Description |
|-------|-------------|
| `owner_only` | Only the bot owner may run the command. |
| `guild_only` | Disallow use in DMs. |
| `dm_only` | Only usable in direct messages. |
| `nsfw_only` | Only usable in age-restricted channels. |
| `has_permissions(**perms)` | Require the user to hold the given permissions. |
| `bot_has_permissions(**perms)` | Require the bot to hold the given permissions. |
| `has_role(role)` | Require a specific role by ID or name. |
| `has_any_role(*roles)` | Require at least one of the listed roles. |
| `cooldown(rate, per, bucket="user")` | Rate-limit the command. |
| `guild_cooldown(rate, per)` | Cooldown shared across a guild. |
| `check(predicate)` | Custom check from any predicate callable. |

```python
class Tickets(vex.Cog):
    panel = vex.slash_group("panel", description="Manage ticket panels.", guild_only=True)

    @vex.slash_cmd(description="Close the current ticket.")
    @vex.guild_only
    @vex.cooldown(1, 10)
    async def close(self, interaction: discord.Interaction, reason: str = None):
        await interaction.response.send_message("Closing...")

    @panel.slash_cmd(description="Create a new panel.")
    @vex.has_permissions(administrator=True)
    async def create(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(f"Created {name}")
```

## Converters

`vex.convert` provides argument converters that resolve a mention, raw ID, or name into a Discord object. Each works as a type annotation in both slash and prefix commands at once, and falls back to a REST fetch when the target is not cached.

| Annotation | Resolves | Accepts |
|------------|----------|---------|
| `vex.convert.user()` | User | Mention, ID, username, display name, prefix match, REST fetch fallback. |
| `vex.convert.member()` | Member | Same as user, narrowed to the current guild. |
| `vex.convert.role()` | Role | Role mention, ID, exact name, prefix match. |
| `vex.convert.channel()` | Channel | Channel mention, ID, name. |
| `vex.convert.duration(minimum=, maximum=)` | int seconds | Strings like `1d12h`, `90m`, `2h30m`. |
| `vex.convert.emoji()` | str or Emoji | Unicode and custom emoji. |

| Option | Description |
|--------|-------------|
| `optional=True` | Make the parameter non-required and return `None` on a miss instead of raising. |
| `minimum` / `maximum` | Duration only. Reject values outside the range, in seconds. |

In slash commands, `user`, `member`, `role`, and `channel` register as native Discord option types, so the client shows the proper picker. A failed conversion raises `vex.ConvertError`, which subclasses both `commands.BadArgument` and `app_commands.AppCommandError`.

```python
class Mod(vex.Cog):
    @vex.slash_cmd(description="Look up a member.")
    async def whois(self, interaction: discord.Interaction, target: vex.convert.user()):
        await interaction.response.send_message(f"{target} ({target.id})")

    @vex.slash_cmd(description="Start a timed giveaway.")
    async def gw(self, interaction: discord.Interaction,
                 length: vex.convert.duration(minimum=30),
                 host: vex.convert.member(optional=True) = None):
        host = host or interaction.user
        await interaction.response.send_message(f"{length}s giveaway by {host}")
```

### Standalone Helpers

| Helper | Description |
|--------|-------------|
| `await vex.convert.to_user(source, value)` | Resolve a user from a context or interaction plus a string. |
| `await vex.convert.to_member(source, value)` | Resolve a member. |
| `await vex.convert.to_role(source, value)` | Resolve a role. |
| `await vex.convert.to_channel(source, value)` | Resolve a channel. |
| `vex.convert.to_duration(value, minimum=, maximum=)` | Parse a duration string to seconds, or `None`. |
| `vex.convert.to_emoji(value)` | Normalize an emoji string, or `None`. |

## Bot and Cog

| Object | Description |
|--------|-------------|
| `Bot` | A `commands.Bot` subclass that auto-loads module-level commands, groups, and persistent views. |
| `bot(command_prefix="!", **kwargs)` | Factory returning a configured `Bot`. |
| `client(command_prefix="!", **kwargs)` | Alias for `bot`. |
| `Cog` | A `commands.Cog` base whose decorated commands and groups register automatically. |
| `SlashGroup` | An `app_commands.Group` subclass exposing `.slash_cmd()` for subcommands. |

```python
class Greetings(vex.Cog):
    @vex.slash_cmd(description="Say hello.")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello")

async def setup(bot):
    await bot.add_cog(Greetings(bot))
```

## Pagination

### Paginator

Standard page wrapper with first, previous, next, and last buttons.

| Property / Method | Description |
|-------------------|-------------|
| `current` | Current page index. |
| `total` | Total pages. |
| `at_start / at_end` | Boundary booleans. |
| `current_page` | Current page data. |
| `jump(index)` / `seek / go_to / page` | Jump to an index. |
| `send_to / send / dispatch(target, files=None)` | Send to a channel. |
| `reply_to / respond / answer / reply(interaction, ephemeral=None, files=None)` | Reply to an interaction. |

### JumpSelectPaginator

Extends `Paginator` with a dropdown to jump to any page.

### GroupedPaginator

Tabbed paginator switching between `PageGroup` objects.

| Property / Method | Description |
|-------------------|-------------|
| `current_group` | Active `PageGroup`. |
| `current_page` | Active page within the group. |
| `send_to(target)` | Send to a channel. |
| `reply_to / respond(interaction, ephemeral=None)` | Reply to an interaction. |

### InfinitePaginator

Async data pagination. Accepts a `fetch(offset)` coroutine and caches pages on demand.

| Method | Description |
|--------|-------------|
| `send_to(target)` | Send after building the first page. |
| `reply_to / respond(interaction)` | Reply to an interaction. |

### ScrollPaginator

Minimal previous/next with a page counter text display.

| Method | Description |
|--------|-------------|
| `jump(index)` | Jump to a page. |
| `send_to / reply_to / respond` | Send and reply methods. |

## Confirmation Flows

### ConfirmView

Yes or no confirmation with two buttons.

| Property / Method | Description |
|-------------------|-------------|
| `result` | `True`, `False`, or `None`. |
| `confirmed / cancelled` | Boolean checks. |
| `wait_result()` | Awaitable boolean result. |
| `send_to(target)` | Send and wait. |
| `reply_to / respond / ask / prompt_user / confirm(interaction)` | Reply and wait. |

### MultiConfirmView

Requires a threshold of distinct users to confirm.

| Property / Method | Description |
|-------------------|-------------|
| `confirmed_by` | Set of user IDs who confirmed. |
| `cancelled` | Whether cancelled. |
| `wait_result()` | Awaitable boolean. |
| `reply_to / respond / send_to` | Send and reply methods. |

### TimedConfirmView

Countdown confirmation that updates every second.

| Property / Method | Description |
|-------------------|-------------|
| `result` | `True`, `False`, or `None`. |
| `wait_result()` | Awaitable boolean. |
| `reply_to / respond / send_to` | Send and reply methods. |

### TypedConfirmView

Requires the user to type a confirmation phrase before the confirm button enables.

| Property / Method | Description |
|-------------------|-------------|
| `result` | `True`, `False`, or `None`. |
| `wait_result()` | Awaitable boolean. |
| `reply_to / respond / send_to` | Send and reply methods. |

## Choice and Select Prompts

### ChoiceView

Presents up to five buttons mapped to choice keys.

| Property / Method | Description |
|-------------------|-------------|
| `result` | Selected key string or `None`. |
| `wait_result()` | Awaitable result. |
| `reply_to / respond / send_to` | Send and reply methods. |

### SelectMenu

Presents a dropdown and returns the chosen values.

| Property / Method | Description |
|-------------------|-------------|
| `result` | List of selected value strings or `None`. |
| `wait_result()` | Awaitable result. |
| `reply_to / respond / send_to` | Send and reply methods. |

## Entity Pickers

| View | Returns |
|------|---------|
| `RolePickerView` | A list of `discord.Role` objects. |
| `ChannelPickerView` | A list of channel objects. Accepts a `channel_types` filter. |
| `UserPickerView` | A list of `discord.Member` or `discord.User` objects. |

All pickers support `reply_to`, `respond`, `send_to`, `wait_result`, and `owner_id` locking.

## Modals

Modals are built with [ModalBuilder](#modalbuilder). The underlying modal collects `TextInput` values and exposes them to your submit callback.

| Method | Description |
|--------|-------------|
| `values()` | Returns a `{custom_id: value}` dict. |
| `on_submit(interaction)` | Calls the registered submit callback. |
| `on_error(interaction, error)` | Calls the registered error callback or the default. |

## Wizard

Multi-step flows that collect input across several screens.

| Object / Method | Description |
|-----------------|-------------|
| `wizard(...)` | Build a `Wizard` from a list of `WizardStep` definitions. |
| `WizardStep` | A single step with its prompt and input handling. |
| `result` | The collected values once finished. |
| `wait_result()` | Awaitable final result. |
| `reply_to / respond / send_to` | Send and reply methods. |

## Live View

A `Vex` subclass that re-renders on an interval from a render callback.

| Object / Method | Description |
|-----------------|-------------|
| `live(...)` | Build a `LiveView` from a render coroutine and interval. |
| `start()` | Begin the refresh loop. |
| `stop()` | Stop refreshing. |
| `send_to / reply_to` | Send and reply methods. |

## Media Collector

Collects uploaded files or media from follow-up messages.

| Method | Description |
|--------|-------------|
| `collect(channel, user=None)` | Wait for media and return the collected items. |
| `media_collector()` / `collector()` | Factory functions. |

## Help Registry

### CommandInfo

Metadata container for commands.

| Field | Description |
|-------|-------------|
| `name` | Command name. |
| `func` | Callable. |
| `description` | Help description. |
| `syntax` | Usage syntax. |
| `example` | Example usage. |
| `category` | Category string. |
| `hidden` | Whether hidden from help. |
| `aliases` | List of alias strings. |

### HelpRegistry

Scans objects for command metadata.

| Method | Description |
|--------|-------------|
| `scan(obj)` | Scan an instance or class for decorated commands. |
| `get(name)` | Retrieve `CommandInfo` by name. |
| `list(category=None, include_hidden=False)` | List commands. |
| `help_card(name)` | Return a `ContainerBuilder` with command details. |
| `help_all(...)` | Return a list of help card containers. |
| `paginator(...)` | Return a `Paginator` of help cards. |

### Help Decorators

| Decorator | Description |
|-----------|-------------|
| `cmd(name=None, aliases=None)` | Attach `CommandInfo` to a function. |
| `cmd_desc(text)` | Set description. |
| `cmd_syntax(text)` | Set syntax. |
| `cmd_example(text)` | Set example. |
| `cmd_category(text)` | Set category. |
| `cmd_hidden(state=True)` | Set hidden flag. |
| `cmd_alias(alias)` | Append an alias. |

### Registry Helpers

| Function | Description |
|----------|-------------|
| `search_commands(registry, query, limit=5, include_hidden=False)` | Fuzzy search by name, alias, or description. |
| `registry_to_select(registry, placeholder="...", category=None)` | Build a `SelectBuilder` of commands. |
| `registry_category_select(registry, placeholder="...")` | Build a `SelectBuilder` of categories. |
| `registry_categories(registry)` | Return a list of category strings. |

## Cooldowns

### CooldownStore

Per-message cooldown bucket wrapper.

| Method | Description |
|--------|-------------|
| `check(message)` | Update the rate limit and return retry-after seconds. |
| `is_limited(message)` | Boolean check. |
| `reset(message)` | Reset the bucket. |
| `retry_after(message)` | Get retry-after without mutating. |
| `remaining(message)` | Approximate remaining uses. |

### GlobalCooldown

Named cooldown stores sharing the same rate and period.

| Method | Description |
|--------|-------------|
| `store(name)` | Get or create a `CooldownStore` by name. |
| `check(name, message)` | Check a named store. |
| `is_limited(name, message)` | Boolean check. |
| `reset(name, message)` | Reset a named store. |
| `reset_all(message)` | Reset every store for the message. |

### CooldownCard

Pre-styled container for cooldown messages.

| Method | Description |
|--------|-------------|
| `build(retry_after, title="Slow down")` | Return a styled `ContainerBuilder`. |
| `from_store(store, message)` | Build from a `CooldownStore`, or return `None`. |

## Utility Cards

Pre-styled `ContainerBuilder` factories for common UI patterns.

| Function | Description |
|----------|-------------|
| `error_card(message, title="Error")` | Red accent container. |
| `success_card(message, title="Success")` | Green accent container. |
| `info_card(message, title="Info")` | Blue accent container. |
| `warning_card(message, title="Warning")` | Yellow accent container. |
| `audit_card(action, actor, target=None, reason=None, fields=None, color=None)` | Audit log style container. |
| `diff_card(title="Changes", before={}, after={}, color=None)` | Before and after diff container. |

## Themes

A theming system controls the default accent colors used by the utility cards and builders.

| Function | Description |
|----------|-------------|
| `theme()` | Return the active `Theme`. |
| `set_theme(**colors)` | Override theme colors by name. |
| `use_theme(custom)` | Apply a custom `Theme` instance. |

## Presence

Spoof the gateway identify properties so the bot appears on a chosen platform.

| Function / Method | Description |
|-------------------|-------------|
| `presence(profile, bot=None)` | Apply a presence profile by name or dict. |
| `PresenceHandler.desktop / mac / linux / mobile / android / vr / web / embedded(bot=None)` | Apply a named profile. |
| `PresenceHandler.custom(bot=None, **props)` | Apply custom identify properties. |
| `PresenceHandler.restore(bot=None)` | Restore the original behavior. |
| `PresenceHandler.profiles()` | List available profile names. |

## Persistence

Register LayoutViews so they survive restarts and continue handling interactions after a reboot.

Requirements:

- The view must be created with `timeout=None`.
- Every interactive component must have a `custom_id`.

| Function | Description |
|----------|-------------|
| `persist(view, bot)` | Validate and register a view with the bot. |
| `register_view(view, bot)` | Alias for `persist`. |
| `make_persistent(view, bot)` | Alias for `persist`. |

```python
view = vex.vex(timeout=None)
view.button(
    vex.button().label("Open Ticket").primary().custom_id("ticket_btn").on_click(open_ticket)
)
vex.persist(view, bot)
```

## Error Constants

`VexError` provides static strings for common bot error responses, grouped by category.

- Permissions: `MISSING_PERMISSIONS`, `BOT_MISSING_PERMISSIONS`, `FORBIDDEN`, `OWNER_ONLY`, `HIERARCHY_ERROR`, `USER_HIERARCHY_ERROR`
- Context: `SERVER_ONLY`, `DM_ONLY`, `NSFW_ONLY`
- Not Found: `NOT_FOUND`, `CHANNEL_NOT_FOUND`, `ROLE_NOT_FOUND`, `MEMBER_NOT_FOUND`, `USER_NOT_FOUND`, `GUILD_NOT_FOUND`, `MESSAGE_NOT_FOUND`, `EMOJI_NOT_FOUND`
- Arguments: `INVALID_ARGUMENT`, `MISSING_ARGUMENT`, `TOO_MANY_ARGUMENTS`, `BAD_UNION`, `CONVERSION_FAILED`, `EXPECTED_INT`, `EXPECTED_FLOAT`, `EXPECTED_BOOL`, `VALUE_TOO_LONG`, `VALUE_TOO_SHORT`, `VALUE_OUT_OF_RANGE`
- State: `ALREADY_EXISTS`, `ALREADY_BANNED`, `NOT_BANNED`, `ALREADY_MUTED`, `NOT_MUTED`, `SELF_ACTION`, `BOT_ACTION`, `ALREADY_IN_VOICE`, `NOT_IN_VOICE`, `BOT_NOT_IN_VOICE`, `VOICE_CHANNEL_FULL`
- Interaction: `TIMED_OUT`, `INTERACTION_FAILED`, `ALREADY_RESPONDED`, `UNKNOWN_INTERACTION`, `CONFIRM_CANCELLED`, `CONFIRM_TIMEOUT`, `NOT_CONFIRMED`
- External: `HTTP_ERROR`, `RATE_LIMITED`, `FORBIDDEN_RESPONSE`, `NOT_FOUND_RESPONSE`, `API_ERROR`, `API_TIMEOUT`, `PARSE_ERROR`, `DATABASE_ERROR`
- Config: `CONFIG_MISSING`, `FEATURE_DISABLED`, `SETUP_REQUIRED`, `PREMIUM_REQUIRED`, `VERIFICATION_REQUIRED`, `AGE_RESTRICTED`, `TERMS_REQUIRED`
- Access: `BLACKLISTED`, `SERVER_BLACKLISTED`, `MAINTENANCE`
- Input: `ATTACHMENT_REQUIRED`, `INVALID_ATTACHMENT`, `ATTACHMENT_TOO_LARGE`, `NO_RESULTS`, `EMPTY_INPUT`, `DUPLICATE_INPUT`, `NUMERIC_ONLY`, `TEXT_ONLY`, `URL_REQUIRED`, `INVALID_URL`, `IMAGE_REQUIRED`, `INVALID_IMAGE`, `INVALID_COLOR`, `INVALID_DATE`, `INVALID_TIME`, `INVALID_DURATION`, `INVALID_ID`, `INVALID_MENTION`, `INVALID_COMMAND`, `SUBCOMMAND_REQUIRED`, `UNKNOWN_SUBCOMMAND`
- Catch-all: `UNEXPECTED`, `UNKNOWN`

## Utility Functions

| Function | Description |
|----------|-------------|
| `edit_to_v2(message, view)` | Edit a message to V2, clearing content and embeds. |
| `disable_all(view)` | Walk all children and set `disabled=True`. |
| `freeze_view(view, interaction)` | Disable all components and edit the interaction message. |
| `safe_defer(interaction, ephemeral=False, thinking=False)` | Defer only if not already responded. |
| `safe_edit(interaction, view=None, allowed_mentions=None)` | Edit safely, swallowing HTTP exceptions. |
| `safe_delete(interaction)` | Delete the original response safely. |
| `progress(value, maximum, ...)` | Render a progress bar string. |
| `bar(value, maximum, ...)` / `meter(...)` | Aliases for `progress`. |
| `text_file(content, filename="message.txt", spoiler=False)` | Build a `discord.File` from text. |
| `bytes_file / file_from_text` | Aliases for `text_file`. |

### PromptInput

Message-based user input collector.

| Method | Description |
|--------|-------------|
| `ask(channel, user=None)` | Wait for a message and return it, or `None` on timeout. |
| `wait / collect(channel, user=None)` | Aliases. `collect` returns the message content string. |

### AutoDeleteView

Extends `Vex` and deletes its own message on timeout.

| Method | Description |
|--------|-------------|
| `send_to(...)` | Send and store the message reference. |
| `reply_to(...)` | Reply and store the message reference. |

### GradientColours

Helper for role color gradients.

| Method | Description |
|--------|-------------|
| `to_kwargs()` | Return a `colour`, `secondary_colour`, `tertiary_colour` dict. |
| `apply(role, reason=None)` | Awaitable role edit. |

## Factory Functions

Top-level convenience constructors.

| Function | Returns |
|----------|---------|
| `vex(timeout=180)` / `new / build / create / make / layout / view / message` | `Vex` |
| `button()` / `btn()` | `ButtonBuilder` |
| `select()` / `dropdown()` | `SelectBuilder` |
| `channel_select()` / `channel_picker()` | `TypedSelectBuilder` (channel) |
| `user_select()` / `user_picker()` | `TypedSelectBuilder` (user) |
| `role_select()` / `role_picker()` | `TypedSelectBuilder` (role) |
| `mentionable_select()` | `TypedSelectBuilder` (mentionable) |
| `action_row(id=None)` / `row(id=None)` | `ActionRowBuilder` |
| `section()` / `aside()` / `panel()` | `SectionBuilder` |
| `gallery(id=None)` / `images / media(id=None)` | `GalleryBuilder` |
| `container(id=None)` / `box / card / frame(id=None)` | `ContainerBuilder` |
| `file(id=None)` / `file_component / document(id=None)` | `FileBuilder` |
| `table(title=None)` / `leaderboard(title=None)` | `TableBuilder` |
| `gradient(primary, secondary=None, tertiary=None)` | `GradientColours` |
| `paginator(...)` / `paginate(...)` / `pages(...)` | `Paginator` |
| `grouped_paginator(...)` | `GroupedPaginator` |
| `scroll_paginator(...)` | `ScrollPaginator` |
| `modal(title="Form")` / `form / prompt(title="Form")` | `ModalBuilder` |
| `text_input(key, label)` / `field_input(key, label)` | `TextInputBuilder` |
| `poll(question="")` / `survey(question="")` | `PollBuilder` |
| `confirm_view(...)` / `confirm(...)` / `ask(...)` | `ConfirmView` |
| `multi_confirm(...)` | `MultiConfirmView` |
| `timed_confirm(...)` | `TimedConfirmView` |
| `typed_confirm(...)` | `TypedConfirmView` |
| `choice_view(...)` / `choice(...)` | `ChoiceView` |
| `select_menu(...)` / `pick(...)` | `SelectMenu` |
| `role_picker(...)` | `RolePickerView` |
| `channel_picker_view(...)` | `ChannelPickerView` |
| `user_picker_view(...)` | `UserPickerView` |
| `prompt_input(...)` / `wait_input(...)` | `PromptInput` |
| `auto_delete(timeout=30)` | `AutoDeleteView` |
| `wizard(...)` | `Wizard` |
| `live(...)` | `LiveView` |
| `media_collector()` / `collector()` | `MediaCollector` |
| `cooldown_store(...)` | `CooldownStore` |
| `global_cooldown(...)` | `GlobalCooldown` |
| `cooldown_card(...)` | `ContainerBuilder` |
| `audit_card(...)` | `ContainerBuilder` |
| `diff_card(...)` | `ContainerBuilder` |
| `convert.user / member / role / channel / duration / emoji(...)` | Argument converters |

## License

MIT
