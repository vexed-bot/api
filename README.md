# Vex V2

A fluent, minimal builder library for Discord Components V2 (Layout Views) in Python. Vex wraps `discord.py`'s V2 primitives with chainable APIs, pre-built paginators, confirmation flows, modals, cooldown utilities, and a lightweight command help registry.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Core View](#core-view)
- [Builders](#builders)
  - [ButtonBuilder](#buttonbuilder)
  - [SelectBuilder](#selectbuilder)
  - [TypedSelectBuilder](#typedselectbuilder)
  - [ActionRowBuilder](#actionrowbuilder)
  - [SectionBuilder](#sectionbuilder)
  - [GalleryBuilder](#gallerybuilder)
  - [ContainerBuilder](#containerbuilder)
  - [TextInputBuilder](#textinputbuilder)
  - [ModalBuilder](#modalbuilder)
- [Pagination](#pagination)
- [Confirmation Flows](#confirmation-flows)
- [Choice & Select Prompts](#choice--select-prompts)
- [Entity Pickers](#entity-pickers)
- [Modals](#modals)
- [Help Registry](#help-registry)
- [Cooldowns](#cooldowns)
- [Utility Cards](#utility-cards)
- [Error Constants](#error-constants)
- [Utility Functions](#utility-functions)
- [Factory Functions](#factory-functions)

---

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

---

## Core View

### `Vex`

Inherits `discord.ui.LayoutView`. The primary canvas for V2 messages.

| Method | Description |
|--------|-------------|
| `lock_to(*user_ids, message="...")` | Restrict interaction to specific user IDs. |
| `unlock()` | Remove the user lock. |
| `on_timeout_do(callback)` | Set a coroutine/callable to run on timeout. |
| `text(content, id=None)` | Add a `TextDisplay` component. |
| `write / line / paragraph / display / label / put / emit` | Aliases for `text`. |
| `heading(content, level=1, id=None)` | Add a markdown heading (`#` / `##` / `###`). |
| `h1 / h2 / h3` | Shorthand for `heading` with fixed levels. |
| `bold(content, id=None)` | Bold text. |
| `italic(content, id=None)` | Italic text. |
| `underline(content, id=None)` | Underlined text. |
| `strikethrough(content, id=None)` | Strikethrough text. |
| `code(content, lang="", id=None)` | Code block. |
| `inline_code(content, id=None)` | Inline code. |
| `quote / blockquote(content, id=None)` | Blockquote line. |
| `field(name, value, id=None)` | Key-value line (`**name:** value`). |
| `kv(key, value, id=None)` | Alias for `field`. |
| `fields(mapping)` | Batch add fields from a dict. |
| `mention_user(user_id, id=None)` | User mention string. |
| `mention_role(role_id, id=None)` | Role mention string. |
| `mention_channel(channel_id, id=None)` | Channel mention string. |
| `timestamp(dt_or_ts, fmt="f", id=None)` | Discord timestamp. |
| `relative(dt_or_ts, id=None)` | Relative timestamp (`R`). |
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

---

## Builders

### `ButtonBuilder`

Chainable builder for `discord.ui.Button`.

| Method | Description |
|--------|-------------|
| `label(text)` / `text / caption / title / name` | Set the button label. |
| `primary()` / `blurple / blue` | Set style to `primary`. |
| `secondary()` / `grey / gray / muted` | Set style to `secondary`. |
| `success()` / `green / confirm / positive` | Set style to `success`. |
| `danger()` / `red / destructive / negative / warning` | Set style to `danger`. |
| `premium(sku_id)` / `sku(sku_id)` | Set style to `premium` with SKU. |
| `link(url)` / `url / href / navigate` | Set style to `link` with URL. |
| `emoji(value)` / `icon / reaction` | Set emoji. |
| `disabled(state=True)` / `locked / inactive` | Disable the button. |
| `enabled(state=True)` / `unlocked / active` | Enable the button. |
| `row(value)` / `position / slot` | Set the action row slot. |
| `id(value)` | Set component ID. |
| `custom_id(value)` / `cid` | Set custom ID. |
| `on_click(callback)` / `handler / action / callback` | Attach an interaction callback. |
| `build()` | Return `discord.ui.Button`. |

### `SelectBuilder`

Chainable builder for `discord.ui.Select` (string select).

| Method | Description |
|--------|-------------|
| `option(label, value)` | Start a `SelectOptionBuilder` (captures on `build()`). |
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

### `SelectOptionBuilder`

| Method | Description |
|--------|-------------|
| `description(text)` / `desc` | Set option description. |
| `emoji(value)` / `icon` | Set option emoji. |
| `default(state=True)` / `selected` | Mark as default. |
| `build()` | Return `discord.SelectOption`. |

### `TypedSelectBuilder`

Builder for `ChannelSelect`, `UserSelect`, `RoleSelect`, `MentionableSelect`.

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

### `ActionRowBuilder`

| Method | Description |
|--------|-------------|
| `add / push / insert / append / put / attach(item)` | Add a button or select. |
| `button(builder)` / `btn` | Build and add a `ButtonBuilder`. |
| `select(builder)` / `dropdown` | Build and add a `SelectBuilder`. |
| `channel_select / user_select / role_select / mentionable_select(builder)` | Build and add typed selects. |
| `id(value)` | Set component ID. |
| `build()` | Return `discord.ui.ActionRow`. |

### `SectionBuilder`

Builds `discord.ui.Section` (text list + accessory).

| Method | Description |
|--------|-------------|
| `text / line / write / paragraph / add / put / push(content)` | Add text lines. |
| `display(item)` | Add a `TextDisplay` directly. |
| `bold / italic(content)` | Styled text. |
| `code(content, lang="")` | Code block. |
| `quote(content)` | Blockquote. |
| `heading(content, level=2)` | Heading. |
| `accessory(item)` / `aside / attachment` | Set accessory (Button or Thumbnail). |
| `thumbnail(url, description="", spoiler=False, id=None)` | Set a thumbnail accessory. |
| `image / photo / icon / avatar` | Aliases for `thumbnail`. |
| `button_accessory(builder)` / `button` | Build a button and set as accessory. |
| `id(value)` | Set component ID. |
| `build()` | Return `discord.ui.Section`. |

### `GalleryBuilder`

Builds `discord.ui.MediaGallery`.

| Method | Description |
|--------|-------------|
| `add(media, description="", spoiler=False)` | Add a `MediaGalleryItem`. |
| `image / animated / gif / photo / media` | Aliases for `add` with URL. |
| `attach / upload(file, description="")` | Add a `discord.File`. |
| `push / insert / append` | Aliases for `add` with URL. |
| `spoiler / hidden(url, description="")` | Add with `spoiler=True`. |
| `id(value)` | Set component ID. |
| `build()` | Return `discord.ui.MediaGallery`. |

### `ContainerBuilder`

Builds `discord.ui.Container` (the V2 card wrapper).

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
| `divider / rule / gap / spacer / large_separator / large_divider / large_gap / small_separator` | Aliases. |
| `section(builder)` | Add a `SectionBuilder`. |
| `action_row(builder)` / `row` | Add an `ActionRowBuilder`. |
| `button(builder, inline=True)` | Add a button; auto-bundles into inline `ActionRow` if possible. |
| `btn` | Alias for `button`. |
| `gallery(builder)` | Add a `GalleryBuilder`. |
| `nest / child / inner(builder)` | Nest a `ContainerBuilder`. |
| `accent(color)` / `color / colour / border / tint / hue` | Set accent color. |
| `hex(value)` | Set accent from hex string. |
| `rgb(r, g, b)` | Set accent from RGB. |
| `spoiler / hidden(state=True)` | Mark as spoiler. |
| `id(value)` | Set component ID. |
| `build()` | Return `discord.ui.Container`. |

### `TextInputBuilder`

Builds `discord.ui.TextInput` for modals.

| Method | Description |
|--------|-------------|
| `label(text)` | Set label. |
| `short()` / `line` | Set style to `short`. |
| `paragraph()` / `long / multiline` | Set style to `paragraph`. |
| `placeholder / hint(text)` | Set placeholder. |
| `default / prefill(text)` | Set default value. |
| `required(state=True)` | Set required. |
| `optional()` | Set not required. |
| `min / max / length(min, max)` | Length constraints. |
| `build()` | Return `discord.ui.TextInput`. |

### `ModalBuilder`

Builds `discord.ui.Modal` via `_VexModal`.

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

---

## Pagination

### `Paginator`

Standard page wrapper with first/prev/next/last buttons.

| Property / Method | Description |
|-------------------|-------------|
| `current` | Current page index. |
| `total` | Total pages. |
| `at_start / at_end` | Boundary booleans. |
| `current_page` | Current page data. |
| `jump(index)` / `seek / go_to / page` | Jump to index. |
| `send_to / send / dispatch(target, files=None)` | Send to channel. |
| `reply_to / respond / answer / reply(interaction, ephemeral=None, files=None)` | Reply to interaction. |

### `JumpSelectPaginator`

Extends `Paginator` with a dropdown to jump to any page.

### `GroupedPaginator`

Tabbed paginator switching between `PageGroup` objects.

| Property / Method | Description |
|-------------------|-------------|
| `current_group` | Active `PageGroup`. |
| `current_page` | Active page within group. |
| `send_to(target)` | Send to channel. |
| `reply_to / respond(interaction, ephemeral=None)` | Reply to interaction. |

### `InfinitePaginator`

Async data pagination. Accepts a `fetch(offset)` coroutine and caches pages on demand.

| Method | Description |
|--------|-------------|
| `send_to(target)` | Send after building first page. |
| `reply_to / respond(interaction)` | Reply to interaction. |

### `ScrollPaginator`

Minimal prev/next with a page counter text display.

| Method | Description |
|--------|-------------|
| `jump(index)` | Jump to page. |
| `send_to / reply_to / respond` | Send/reply methods. |

---

## Confirmation Flows

### `ConfirmView`

Yes/no confirmation with two buttons.

| Property / Method | Description |
|-------------------|-------------|
| `result` | `True`, `False`, or `None`. |
| `confirmed / cancelled` | Boolean checks. |
| `wait_result()` | Awaitable boolean result. |
| `send_to(target)` | Send and wait. |
| `reply_to / respond / ask / prompt_user / confirm(interaction)` | Reply and wait. |

### `MultiConfirmView`

Requires a threshold of distinct users to confirm.

| Property / Method | Description |
|-------------------|-------------|
| `confirmed_by` | Set of user IDs who confirmed. |
| `cancelled` | Whether cancelled. |
| `wait_result()` | Awaitable boolean. |
| `reply_to / respond / send_to` | Send/reply methods. |

### `TimedConfirmView`

Countdown confirmation that updates every second.

| Property / Method | Description |
|-------------------|-------------|
| `result` | `True`, `False`, or `None`. |
| `wait_result()` | Awaitable boolean. |
| `reply_to / respond / send_to` | Send/reply methods. |

---

## Choice & Select Prompts

### `ChoiceView`

Presents up to 5 buttons mapped to choice keys.

| Property / Method | Description |
|-------------------|-------------|
| `result` | Selected key string or `None`. |
| `wait_result()` | Awaitable result. |
| `reply_to / respond / send_to` | Send/reply methods. |

### `SelectMenu`

Presents a `Select` dropdown and returns the chosen values.

| Property / Method | Description |
|-------------------|-------------|
| `result` | List of selected value strings or `None`. |
| `wait_result()` | Awaitable result. |
| `reply_to / respond / send_to` | Send/reply methods. |

---

## Entity Pickers

### `RolePickerView`

Returns a list of `discord.Role` objects.

### `ChannelPickerView`

Returns a list of channel objects. Accepts `channel_types` filter.

### `UserPickerView`

Returns a list of `discord.Member` or `discord.User` objects.

All pickers support `reply_to`, `respond`, `send_to`, `wait_result`, and `owner_id` locking.

---

## Modals

### `_VexModal`

Internal modal subclass that collects `TextInput` values.

| Method | Description |
|--------|-------------|
| `values()` | Returns `{custom_id: value}` dict. |
| `on_submit(interaction)` | Calls the registered submit callback. |
| `on_error(interaction, error)` | Calls the registered error callback or falls back to default. |

---

## Help Registry

### `CommandInfo`

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

### `HelpRegistry`

Scans objects for `__vex_help__` metadata.

| Method | Description |
|--------|-------------|
| `scan(obj)` | Scan an instance/class for decorated commands. |
| `get(name)` | Retrieve `CommandInfo` by name. |
| `list(category=None, include_hidden=False)` | List commands. |
| `help_card(name)` | Return a `ContainerBuilder` with command details. |
| `help_all(...)` | Return a list of help card containers. |
| `paginator(...)` | Return a `Paginator` of help cards. |

### Decorators

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
| `search_commands(registry, query, limit=5, include_hidden=False)` | Fuzzy search by name/alias/description. |
| `registry_to_select(registry, placeholder="...", category=None)` | Build a `SelectBuilder` of commands. |
| `registry_category_select(registry, placeholder="...")` | Build a `SelectBuilder` of categories. |
| `registry_categories(registry)` | Return list of category strings. |

---

## Cooldowns

### `CooldownStore`

Per-message cooldown bucket wrapper.

| Method | Description |
|--------|-------------|
| `check(message)` | Update rate limit; returns retry-after seconds. |
| `is_limited(message)` | Boolean check. |
| `reset(message)` | Reset the bucket. |
| `retry_after(message)` | Get retry-after without mutating. |
| `remaining(message)` | Approximate remaining uses. |

### `GlobalCooldown`

Named cooldown stores sharing the same rate/period.

| Method | Description |
|--------|-------------|
| `store(name)` | Get or create a `CooldownStore` by name. |
| `check(name, message)` | Check a named store. |
| `is_limited(name, message)` | Boolean check. |
| `reset(name, message)` | Reset a named store. |
| `reset_all(message)` | Reset every store for the message. |

### `CooldownCard`

Pre-styled container for cooldown messages.

| Method | Description |
|--------|-------------|
| `build(retry_after, title="Slow down")` | Return a yellow `ContainerBuilder`. |
| `from_store(store, message)` | Build from a `CooldownStore` or return `None`. |

---

## Utility Cards

Pre-styled `ContainerBuilder` factories for common UI patterns.

| Function | Description |
|----------|-------------|
| `error_card(message, title="Error")` | Red accent container. |
| `success_card(message, title="Success")` | Green accent container. |
| `info_card(message, title="Info")` | Blue accent container. |
| `audit_card(action, actor, target=None, reason=None, fields=None, color=None)` | Audit log style container. |
| `diff_card(title="Changes", before={}, after={}, color=None)` | Before/after diff container. |

---

## Error Constants

`VexError` provides static strings for common bot error responses. Categories include:

- **Permissions**: `MISSING_PERMISSIONS`, `BOT_MISSING_PERMISSIONS`, `FORBIDDEN`, `OWNER_ONLY`, `HIERARCHY_ERROR`, `USER_HIERARCHY_ERROR`
- **Context**: `SERVER_ONLY`, `DM_ONLY`, `NSFW_ONLY`
- **Not Found**: `NOT_FOUND`, `CHANNEL_NOT_FOUND`, `ROLE_NOT_FOUND`, `MEMBER_NOT_FOUND`, `USER_NOT_FOUND`, `GUILD_NOT_FOUND`, `MESSAGE_NOT_FOUND`, `EMOJI_NOT_FOUND`
- **Arguments**: `INVALID_ARGUMENT`, `MISSING_ARGUMENT`, `TOO_MANY_ARGUMENTS`, `BAD_UNION`, `CONVERSION_FAILED`, `EXPECTED_INT`, `EXPECTED_FLOAT`, `EXPECTED_BOOL`, `VALUE_TOO_LONG`, `VALUE_TOO_SHORT`, `VALUE_OUT_OF_RANGE`
- **State**: `ALREADY_EXISTS`, `ALREADY_BANNED`, `NOT_BANNED`, `ALREADY_MUTED`, `NOT_MUTED`, `SELF_ACTION`, `BOT_ACTION`, `ALREADY_IN_VOICE`, `NOT_IN_VOICE`, `BOT_NOT_IN_VOICE`, `VOICE_CHANNEL_FULL`
- **Interaction**: `TIMED_OUT`, `INTERACTION_FAILED`, `ALREADY_RESPONDED`, `UNKNOWN_INTERACTION`, `CONFIRM_CANCELLED`, `CONFIRM_TIMEOUT`, `NOT_CONFIRMED`
- **External**: `HTTP_ERROR`, `RATE_LIMITED`, `FORBIDDEN_RESPONSE`, `NOT_FOUND_RESPONSE`, `API_ERROR`, `API_TIMEOUT`, `PARSE_ERROR`, `DATABASE_ERROR`
- **Config**: `CONFIG_MISSING`, `FEATURE_DISABLED`, `SETUP_REQUIRED`, `PREMIUM_REQUIRED`, `VERIFICATION_REQUIRED`, `AGE_RESTRICTED`, `TERMS_REQUIRED`
- **Access**: `BLACKLISTED`, `SERVER_BLACKLISTED`, `MAINTENANCE`
- **Input**: `ATTACHMENT_REQUIRED`, `INVALID_ATTACHMENT`, `ATTACHMENT_TOO_LARGE`, `NO_RESULTS`, `EMPTY_INPUT`, `DUPLICATE_INPUT`, `NUMERIC_ONLY`, `TEXT_ONLY`, `URL_REQUIRED`, `INVALID_URL`, `IMAGE_REQUIRED`, `INVALID_IMAGE`, `INVALID_COLOR`, `INVALID_DATE`, `INVALID_TIME`, `INVALID_DURATION`, `INVALID_ID`, `INVALID_MENTION`, `INVALID_COMMAND`, `SUBCOMMAND_REQUIRED`, `UNKNOWN_SUBCOMMAND`
- **Catch-all**: `UNEXPECTED`, `UNKNOWN`

---

## Utility Functions

| Function | Description |
|----------|-------------|
| `edit_to_v2(message, view)` | Edit a message to V2 (clears content/embeds, sets view). |
| `disable_all(view)` | Walk all children and set `disabled=True`. |
| `freeze_view(view, interaction)` | Disable all and edit the interaction message. |
| `safe_defer(interaction, ephemeral=False, thinking=False)` | Defer only if not already responded. |
| `safe_edit(interaction, view=None, allowed_mentions=None)` | Edit safely, swallowing HTTP exceptions. |
| `safe_delete(interaction)` | Delete original response safely. |

### `PromptInput`

Message-based user input collector.

| Method | Description |
|--------|-------------|
| `ask(channel, user=None)` | Wait for a message; return it or `None` on timeout. |
| `wait / collect(channel, user=None)` | Aliases; `collect` returns message content string. |

### `AutoDeleteView`

Extends `Vex`. Deletes its own message on timeout.

| Method | Description |
|--------|-------------|
| `send_to(...)` | Send and store message reference. |
| `reply_to(...)` | Reply and store message reference. |

### `GradientColours`

Helper for role colour gradients.

| Method | Description |
|--------|-------------|
| `to_kwargs()` | Return `colour`, `secondary_colour`, `tertiary_colour` dict. |
| `apply(role, reason=None)` | Awaitable role edit. |

---

## Factory Functions

Top-level convenience constructors.

| Function | Returns |
|----------|---------|
| `vex(timeout=180)` / `new / build / create / make / layout / view / message` | `Vex` |
| `button()` / `btn()` | `ButtonBuilder` |
| `select()` / `dropdown()` | `SelectBuilder` |
| `channel_select()` / `channel_picker()` | `TypedSelectBuilder("channel")` |
| `user_select()` / `user_picker()` | `TypedSelectBuilder("user")` |
| `role_select()` / `role_picker()` | `TypedSelectBuilder("role")` |
| `mentionable_select()` | `TypedSelectBuilder("mentionable")` |
| `action_row(id=None)` / `row(id=None)` | `ActionRowBuilder` |
| `section()` / `aside()` / `panel()` | `SectionBuilder` |
| `gallery(id=None)` / `images / media(id=None)` | `GalleryBuilder` |
| `container(id=None)` / `box / card / frame(id=None)` | `ContainerBuilder` |
| `gradient(primary, secondary=None, tertiary=None)` | `GradientColours` |
| `paginator(...)` / `paginate(...)` / `pages(...)` | `Paginator` |
| `modal(title="Form")` / `form / prompt(title="Form")` | `ModalBuilder` |
| `text_input(key, label)` / `field_input(key, label)` | `TextInputBuilder` |
| `confirm_view(...)` / `confirm(...)` / `ask(...)` | `ConfirmView` |
| `multi_confirm(...)` | `MultiConfirmView` |
| `timed_confirm(...)` | `TimedConfirmView` |
| `choice_view(...)` / `choice(...)` | `ChoiceView` |
| `select_menu(...)` / `pick(...)` | `SelectMenu` |
| `role_picker(...)` | `RolePickerView` |
| `channel_picker_view(...)` | `ChannelPickerView` |
| `user_picker_view(...)` | `UserPickerView` |
| `prompt_input(...)` / `wait_input(...)` | `PromptInput` |
| `auto_delete(timeout=30)` | `AutoDeleteView` |
| `cooldown_store(...)` | `CooldownStore` |
| `global_cooldown(...)` | `GlobalCooldown` |
| `cooldown_card(...)` | `ContainerBuilder` |
| `audit_card(...)` | `ContainerBuilder` |
| `diff_card(...)` | `ContainerBuilder` |
| `grouped_paginator(...)` | `GroupedPaginator` |
| `scroll_paginator(...)` | `ScrollPaginator` |

---

## License

MIT
