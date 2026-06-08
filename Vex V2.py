from __future__ import annotations
import asyncio
import discord
from discord.ext import commands
from typing import Self, Callable, Awaitable, Any


class ButtonBuilder:
    def __init__(self) -> None:
        self._label: str = ""
        self._custom_id: str | None = None
        self._style: discord.ButtonStyle = discord.ButtonStyle.secondary
        self._emoji: str | discord.Emoji | discord.PartialEmoji | None = None
        self._url: str | None = None
        self._disabled: bool = False
        self._row: int | None = None
        self._id: int | None = None
        self._sku_id: int | None = None
        self._callback: Any = None

    def label(self, text: str) -> Self:
        self._label = text
        return self

    def text(self, text: str) -> Self:
        self._label = text
        return self

    def caption(self, text: str) -> Self:
        self._label = text
        return self

    def title(self, text: str) -> Self:
        self._label = text
        return self

    def name(self, text: str) -> Self:
        self._label = text
        return self

    def primary(self) -> Self:
        self._style = discord.ButtonStyle.primary
        return self

    def blurple(self) -> Self:
        self._style = discord.ButtonStyle.primary
        return self

    def blue(self) -> Self:
        self._style = discord.ButtonStyle.primary
        return self

    def secondary(self) -> Self:
        self._style = discord.ButtonStyle.secondary
        return self

    def grey(self) -> Self:
        self._style = discord.ButtonStyle.secondary
        return self

    def gray(self) -> Self:
        self._style = discord.ButtonStyle.secondary
        return self

    def muted(self) -> Self:
        self._style = discord.ButtonStyle.secondary
        return self

    def success(self) -> Self:
        self._style = discord.ButtonStyle.success
        return self

    def green(self) -> Self:
        self._style = discord.ButtonStyle.success
        return self

    def confirm(self) -> Self:
        self._style = discord.ButtonStyle.success
        return self

    def positive(self) -> Self:
        self._style = discord.ButtonStyle.success
        return self

    def danger(self) -> Self:
        self._style = discord.ButtonStyle.danger
        return self

    def red(self) -> Self:
        self._style = discord.ButtonStyle.danger
        return self

    def destructive(self) -> Self:
        self._style = discord.ButtonStyle.danger
        return self

    def negative(self) -> Self:
        self._style = discord.ButtonStyle.danger
        return self

    def warning(self) -> Self:
        self._style = discord.ButtonStyle.danger
        return self

    def premium(self, sku_id: int) -> Self:
        self._style = discord.ButtonStyle.premium
        self._sku_id = sku_id
        return self

    def sku(self, sku_id: int) -> Self:
        return self.premium(sku_id)

    def link(self, url: str) -> Self:
        self._style = discord.ButtonStyle.link
        self._url = url
        return self

    def url(self, url: str) -> Self:
        self._style = discord.ButtonStyle.link
        self._url = url
        return self

    def href(self, url: str) -> Self:
        self._style = discord.ButtonStyle.link
        self._url = url
        return self

    def navigate(self, url: str) -> Self:
        self._style = discord.ButtonStyle.link
        self._url = url
        return self

    def emoji(self, value: str | discord.Emoji | discord.PartialEmoji) -> Self:
        self._emoji = value
        return self

    def icon(self, value: str | discord.Emoji | discord.PartialEmoji) -> Self:
        self._emoji = value
        return self

    def reaction(self, value: str | discord.Emoji | discord.PartialEmoji) -> Self:
        self._emoji = value
        return self

    def disabled(self, state: bool = True) -> Self:
        self._disabled = state
        return self

    def enabled(self, state: bool = True) -> Self:
        self._disabled = not state
        return self

    def locked(self) -> Self:
        self._disabled = True
        return self

    def unlocked(self) -> Self:
        self._disabled = False
        return self

    def inactive(self) -> Self:
        self._disabled = True
        return self

    def active(self) -> Self:
        self._disabled = False
        return self

    def row(self, value: int) -> Self:
        self._row = value
        return self

    def position(self, value: int) -> Self:
        self._row = value
        return self

    def slot(self, value: int) -> Self:
        self._row = value
        return self

    def id(self, value: int) -> Self:
        self._id = value
        return self

    def custom_id(self, value: str) -> Self:
        self._custom_id = value
        return self

    def cid(self, value: str) -> Self:
        self._custom_id = value
        return self

    def on_click(self, callback: Any) -> Self:
        self._callback = callback
        return self

    def handler(self, callback: Any) -> Self:
        self._callback = callback
        return self

    def action(self, callback: Any) -> Self:
        self._callback = callback
        return self

    def callback(self, cb: Any) -> Self:
        self._callback = cb
        return self

    def build(self) -> discord.ui.Button:
        kwargs: dict[str, Any] = {
            "style": self._style,
            "label": self._label,
            "disabled": self._disabled,
        }
        if self._custom_id:
            kwargs["custom_id"] = self._custom_id
        if self._emoji:
            kwargs["emoji"] = self._emoji
        if self._url:
            kwargs["url"] = self._url
        if self._sku_id is not None:
            kwargs["sku_id"] = self._sku_id
        if self._row is not None:
            kwargs["row"] = self._row
        if self._id is not None:
            kwargs["id"] = self._id
        btn = discord.ui.Button(**kwargs)
        if self._callback:
            btn.callback = self._callback
        return btn


class SelectOptionBuilder:
    def __init__(self, label: str, value: str) -> None:
        self._label = label
        self._value = value
        self._description: str | None = None
        self._emoji: str | discord.Emoji | discord.PartialEmoji | None = None
        self._default: bool = False

    def description(self, text: str) -> Self:
        self._description = text
        return self

    def desc(self, text: str) -> Self:
        self._description = text
        return self

    def emoji(self, value: str | discord.Emoji | discord.PartialEmoji) -> Self:
        self._emoji = value
        return self

    def icon(self, value: str | discord.Emoji | discord.PartialEmoji) -> Self:
        self._emoji = value
        return self

    def default(self, state: bool = True) -> Self:
        self._default = state
        return self

    def selected(self, state: bool = True) -> Self:
        self._default = state
        return self

    def build(self) -> discord.SelectOption:
        kwargs: dict[str, Any] = {"label": self._label, "value": self._value}
        if self._description:
            kwargs["description"] = self._description
        if self._emoji:
            kwargs["emoji"] = self._emoji
        if self._default:
            kwargs["default"] = self._default
        return discord.SelectOption(**kwargs)


class SelectBuilder:
    def __init__(self) -> None:
        self._options: list[discord.SelectOption] = []
        self._placeholder: str | None = None
        self._custom_id: str | None = None
        self._min_values: int = 1
        self._max_values: int = 1
        self._disabled: bool = False
        self._row: int | None = None
        self._callback: Any = None

    def option(self, label: str, value: str) -> SelectOptionBuilder:
        builder = SelectOptionBuilder(label, value)
        self._options.append(None)  # type: ignore
        _idx = len(self._options) - 1

        original_build = builder.build

        def _capture() -> discord.SelectOption:
            opt = original_build()
            self._options[_idx] = opt
            return opt

        builder.build = _capture  # type: ignore
        return builder

    def add(self, label: str, value: str, *, description: str | None = None, emoji: Any = None, default: bool = False) -> Self:
        kwargs: dict[str, Any] = {"label": label, "value": value}
        if description:
            kwargs["description"] = description
        if emoji:
            kwargs["emoji"] = emoji
        if default:
            kwargs["default"] = default
        self._options.append(discord.SelectOption(**kwargs))
        return self

    def choice(self, label: str, value: str, *, description: str | None = None) -> Self:
        return self.add(label, value, description=description)

    def item(self, label: str, value: str, *, description: str | None = None) -> Self:
        return self.add(label, value, description=description)

    def placeholder(self, text: str) -> Self:
        self._placeholder = text
        return self

    def hint(self, text: str) -> Self:
        self._placeholder = text
        return self

    def prompt(self, text: str) -> Self:
        self._placeholder = text
        return self

    def custom_id(self, value: str) -> Self:
        self._custom_id = value
        return self

    def cid(self, value: str) -> Self:
        self._custom_id = value
        return self

    def min(self, value: int) -> Self:
        self._min_values = value
        return self

    def max(self, value: int) -> Self:
        self._max_values = value
        return self

    def range(self, min_val: int, max_val: int) -> Self:
        self._min_values = min_val
        self._max_values = max_val
        return self

    def multi(self, max_val: int = 25) -> Self:
        self._max_values = max_val
        return self

    def disabled(self, state: bool = True) -> Self:
        self._disabled = state
        return self

    def locked(self) -> Self:
        self._disabled = True
        return self

    def row(self, value: int) -> Self:
        self._row = value
        return self

    def on_select(self, callback: Any) -> Self:
        self._callback = callback
        return self

    def handler(self, callback: Any) -> Self:
        self._callback = callback
        return self

    def callback(self, cb: Any) -> Self:
        self._callback = cb
        return self

    def build(self) -> discord.ui.Select:
        kwargs: dict[str, Any] = {
            "options": [o for o in self._options if o is not None],
            "min_values": self._min_values,
            "max_values": self._max_values,
            "disabled": self._disabled,
        }
        if self._placeholder:
            kwargs["placeholder"] = self._placeholder
        if self._custom_id:
            kwargs["custom_id"] = self._custom_id
        if self._row is not None:
            kwargs["row"] = self._row
        sel = discord.ui.Select(**kwargs)
        if self._callback:
            sel.callback = self._callback
        return sel


class TypedSelectBuilder:
    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._placeholder: str | None = None
        self._custom_id: str | None = None
        self._min_values: int = 1
        self._max_values: int = 1
        self._disabled: bool = False
        self._row: int | None = None
        self._callback: Any = None
        self._channel_types: list[discord.ChannelType] | None = None
        self._default_values: list[Any] | None = None

    def placeholder(self, text: str) -> Self:
        self._placeholder = text
        return self

    def hint(self, text: str) -> Self:
        self._placeholder = text
        return self

    def prompt(self, text: str) -> Self:
        self._placeholder = text
        return self

    def custom_id(self, value: str) -> Self:
        self._custom_id = value
        return self

    def cid(self, value: str) -> Self:
        self._custom_id = value
        return self

    def min(self, value: int) -> Self:
        self._min_values = value
        return self

    def max(self, value: int) -> Self:
        self._max_values = value
        return self

    def range(self, min_val: int, max_val: int) -> Self:
        self._min_values = min_val
        self._max_values = max_val
        return self

    def multi(self, max_val: int = 25) -> Self:
        self._max_values = max_val
        return self

    def channel_types(self, *types: discord.ChannelType) -> Self:
        self._channel_types = list(types)
        return self

    def text_only(self) -> Self:
        self._channel_types = [discord.ChannelType.text]
        return self

    def voice_only(self) -> Self:
        self._channel_types = [discord.ChannelType.voice]
        return self

    def defaults(self, values: list[Any]) -> Self:
        self._default_values = values
        return self

    def disabled(self, state: bool = True) -> Self:
        self._disabled = state
        return self

    def locked(self) -> Self:
        self._disabled = True
        return self

    def row(self, value: int) -> Self:
        self._row = value
        return self

    def on_select(self, callback: Any) -> Self:
        self._callback = callback
        return self

    def handler(self, callback: Any) -> Self:
        self._callback = callback
        return self

    def callback(self, cb: Any) -> Self:
        self._callback = cb
        return self

    def build(self) -> discord.ui.Select:
        kwargs: dict[str, Any] = {
            "min_values": self._min_values,
            "max_values": self._max_values,
            "disabled": self._disabled,
        }
        if self._placeholder:
            kwargs["placeholder"] = self._placeholder
        if self._custom_id:
            kwargs["custom_id"] = self._custom_id
        if self._row is not None:
            kwargs["row"] = self._row
        if self._kind == "channel":
            if self._channel_types:
                kwargs["channel_types"] = self._channel_types
            cls = discord.ui.ChannelSelect
        elif self._kind == "user":
            cls = discord.ui.UserSelect
        elif self._kind == "role":
            cls = discord.ui.RoleSelect
        else:
            cls = discord.ui.MentionableSelect
        if self._default_values is not None:
            kwargs["default_values"] = self._default_values
        sel = cls(**kwargs)
        if self._callback:
            sel.callback = self._callback
        return sel


class ActionRowBuilder:
    def __init__(self, *, id: int | None = None) -> None:
        self._items: list[discord.ui.Button | discord.ui.Select] = []
        self._id = id

    def add(self, item: discord.ui.Button | discord.ui.Select) -> Self:
        self._items.append(item)
        return self

    def push(self, item: discord.ui.Button | discord.ui.Select) -> Self:
        self._items.append(item)
        return self

    def insert(self, item: discord.ui.Button | discord.ui.Select) -> Self:
        self._items.append(item)
        return self

    def append(self, item: discord.ui.Button | discord.ui.Select) -> Self:
        self._items.append(item)
        return self

    def put(self, item: discord.ui.Button | discord.ui.Select) -> Self:
        self._items.append(item)
        return self

    def attach(self, item: discord.ui.Button | discord.ui.Select) -> Self:
        self._items.append(item)
        return self

    def button(self, builder: ButtonBuilder) -> Self:
        self._items.append(builder.build())
        return self

    def btn(self, builder: ButtonBuilder) -> Self:
        self._items.append(builder.build())
        return self

    def select(self, builder: SelectBuilder) -> Self:
        self._items.append(builder.build())
        return self

    def dropdown(self, builder: SelectBuilder) -> Self:
        self._items.append(builder.build())
        return self

    def channel_select(self, builder: "TypedSelectBuilder") -> Self:
        self._items.append(builder.build())
        return self

    def user_select(self, builder: "TypedSelectBuilder") -> Self:
        self._items.append(builder.build())
        return self

    def role_select(self, builder: "TypedSelectBuilder") -> Self:
        self._items.append(builder.build())
        return self

    def mentionable_select(self, builder: "TypedSelectBuilder") -> Self:
        self._items.append(builder.build())
        return self

    def id(self, value: int) -> Self:
        self._id = value
        return self

    def build(self) -> discord.ui.ActionRow:
        kwargs: dict[str, Any] = {}
        if self._id is not None:
            kwargs["id"] = self._id
        return discord.ui.ActionRow(*self._items, **kwargs)


class SectionBuilder:
    def __init__(self) -> None:
        self._items: list[str | discord.ui.TextDisplay] = []
        self._accessory: discord.ui.Button | discord.ui.Thumbnail | None = None
        self._id: int | None = None

    def text(self, content: str) -> Self:
        self._items.append(content)
        return self

    def line(self, content: str) -> Self:
        self._items.append(content)
        return self

    def write(self, content: str) -> Self:
        self._items.append(content)
        return self

    def paragraph(self, content: str) -> Self:
        self._items.append(content)
        return self

    def add(self, content: str) -> Self:
        self._items.append(content)
        return self

    def put(self, content: str) -> Self:
        self._items.append(content)
        return self

    def push(self, content: str) -> Self:
        self._items.append(content)
        return self

    def display(self, item: discord.ui.TextDisplay) -> Self:
        self._items.append(item)
        return self

    def bold(self, content: str) -> Self:
        self._items.append(f"**{content}**")
        return self

    def italic(self, content: str) -> Self:
        self._items.append(f"*{content}*")
        return self

    def code(self, content: str, lang: str = "") -> Self:
        self._items.append(f"```{lang}\n{content}\n```")
        return self

    def quote(self, content: str) -> Self:
        self._items.append(f"> {content}")
        return self

    def heading(self, content: str, level: int = 2) -> Self:
        prefix = "#" * max(1, min(level, 3))
        self._items.append(f"{prefix} {content}")
        return self

    def accessory(self, item: discord.ui.Button | discord.ui.Thumbnail) -> Self:
        self._accessory = item
        return self

    def aside(self, item: discord.ui.Button | discord.ui.Thumbnail) -> Self:
        self._accessory = item
        return self

    def attachment(self, item: discord.ui.Button | discord.ui.Thumbnail) -> Self:
        self._accessory = item
        return self

    def thumbnail(self, url: str, *, description: str = "", spoiler: bool = False, id: int | None = None) -> Self:
        kwargs: dict[str, Any] = {}
        if description:
            kwargs["description"] = description
        if spoiler:
            kwargs["spoiler"] = spoiler
        if id is not None:
            kwargs["id"] = id
        self._accessory = discord.ui.Thumbnail(url, **kwargs)
        return self

    def image(self, url: str, *, description: str = "", spoiler: bool = False) -> Self:
        return self.thumbnail(url, description=description, spoiler=spoiler)

    def photo(self, url: str, *, description: str = "") -> Self:
        return self.thumbnail(url, description=description)

    def icon(self, url: str, *, description: str = "") -> Self:
        return self.thumbnail(url, description=description)

    def avatar(self, url: str, *, description: str = "") -> Self:
        return self.thumbnail(url, description=description)

    def button_accessory(self, builder: ButtonBuilder) -> Self:
        self._accessory = builder.build()
        return self

    def button(self, builder: ButtonBuilder) -> Self:
        self._accessory = builder.build()
        return self

    def id(self, value: int) -> Self:
        self._id = value
        return self

    def build(self) -> discord.ui.Section:
        kwargs: dict[str, Any] = {}
        if self._accessory:
            kwargs["accessory"] = self._accessory
        if self._id is not None:
            kwargs["id"] = self._id
        return discord.ui.Section(*self._items, **kwargs)


class GalleryBuilder:
    def __init__(self, *, id: int | None = None) -> None:
        self._items: list[discord.MediaGalleryItem] = []
        self._id = id

    def add(self, media: str | discord.File, *, description: str = "", spoiler: bool = False) -> Self:
        kwargs: dict[str, Any] = {}
        if description:
            kwargs["description"] = description
        if spoiler:
            kwargs["spoiler"] = spoiler
        self._items.append(discord.MediaGalleryItem(media, **kwargs))
        return self

    def image(self, url: str, *, description: str = "", spoiler: bool = False) -> Self:
        return self.add(url, description=description, spoiler=spoiler)

    def animated(self, url: str, *, description: str = "") -> Self:
        return self.add(url, description=description)

    def gif(self, url: str, *, description: str = "") -> Self:
        return self.add(url, description=description)

    def photo(self, url: str, *, description: str = "") -> Self:
        return self.add(url, description=description)

    def media(self, url: str, *, description: str = "", spoiler: bool = False) -> Self:
        return self.add(url, description=description, spoiler=spoiler)

    def attach(self, file: discord.File, *, description: str = "") -> Self:
        return self.add(file, description=description)

    def upload(self, file: discord.File, *, description: str = "") -> Self:
        return self.add(file, description=description)

    def push(self, url: str, *, description: str = "") -> Self:
        return self.add(url, description=description)

    def insert(self, url: str, *, description: str = "") -> Self:
        return self.add(url, description=description)

    def append(self, url: str, *, description: str = "") -> Self:
        return self.add(url, description=description)

    def spoiler(self, url: str, *, description: str = "") -> Self:
        return self.add(url, description=description, spoiler=True)

    def hidden(self, url: str, *, description: str = "") -> Self:
        return self.add(url, description=description, spoiler=True)

    def id(self, value: int) -> Self:
        self._id = value
        return self

    def build(self) -> discord.ui.MediaGallery:
        kwargs: dict[str, Any] = {}
        if self._id is not None:
            kwargs["id"] = self._id
        return discord.ui.MediaGallery(*self._items, **kwargs)


class ContainerBuilder:
    def __init__(self, *, id: int | None = None) -> None:
        self._children: list[Any] = []
        self._accent: discord.Color | int | None = None
        self._spoiler: bool = False
        self._inline_rows: set[int] = set()
        self._id = id

    def _resolve(self, component: Any) -> Any:
        if isinstance(component, (
            SectionBuilder, ActionRowBuilder, GalleryBuilder, ContainerBuilder
        )):
            return component.build()
        return component

    def add(self, component: Any) -> Self:
        self._children.append(self._resolve(component))
        return self

    def push(self, component: Any) -> Self:
        return self.add(component)

    def append(self, component: Any) -> Self:
        return self.add(component)

    def insert(self, component: Any) -> Self:
        return self.add(component)

    def attach(self, component: Any) -> Self:
        return self.add(component)

    def text(self, content: str, *, id: int | None = None) -> Self:
        kwargs: dict[str, Any] = {}
        if id is not None:
            kwargs["id"] = id
        self._children.append(discord.ui.TextDisplay(content, **kwargs))
        return self

    def write(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def line(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def paragraph(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def display(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def heading(self, content: str, level: int = 1, *, id: int | None = None) -> Self:
        prefix = "#" * max(1, min(level, 3))
        return self.text(f"{prefix} {content}", id=id)

    def h1(self, content: str, *, id: int | None = None) -> Self:
        return self.heading(content, 1, id=id)

    def h2(self, content: str, *, id: int | None = None) -> Self:
        return self.heading(content, 2, id=id)

    def h3(self, content: str, *, id: int | None = None) -> Self:
        return self.heading(content, 3, id=id)

    def bold(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"**{content}**", id=id)

    def italic(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"*{content}*", id=id)

    def underline(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"__{content}__", id=id)

    def strikethrough(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"~~{content}~~", id=id)

    def code(self, content: str, lang: str = "", *, id: int | None = None) -> Self:
        return self.text(f"```{lang}\n{content}\n```", id=id)

    def inline_code(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"`{content}`", id=id)

    def quote(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"> {content}", id=id)

    def field(self, name: str, value: str, *, id: int | None = None) -> Self:
        return self.text(f"**{name}:** {value}", id=id)

    def kv(self, key: str, value: str, *, id: int | None = None) -> Self:
        return self.field(key, value, id=id)

    def fields(self, mapping: dict[str, str]) -> Self:
        for name, value in mapping.items():
            self.field(name, value)
        return self

    def separator(self, *, large: bool = False, visible: bool = True, id: int | None = None) -> Self:
        spacing = discord.SeparatorSpacing.large if large else discord.SeparatorSpacing.small
        kwargs: dict[str, Any] = {}
        if id is not None:
            kwargs["id"] = id
        self._children.append(discord.ui.Separator(spacing=spacing, visible=visible, **kwargs))
        return self

    def divider(self, *, large: bool = False) -> Self:
        return self.separator(large=large, visible=True)

    def rule(self, *, large: bool = False) -> Self:
        return self.separator(large=large, visible=True)

    def gap(self, *, large: bool = False) -> Self:
        return self.separator(large=large, visible=False)

    def spacer(self, *, large: bool = False) -> Self:
        return self.separator(large=large, visible=False)

    def large_separator(self, *, visible: bool = True, id: int | None = None) -> Self:
        return self.separator(large=True, visible=visible, id=id)

    def large_divider(self, *, id: int | None = None) -> Self:
        return self.separator(large=True, visible=True, id=id)

    def large_gap(self, *, id: int | None = None) -> Self:
        return self.separator(large=True, visible=False, id=id)

    def small_separator(self, *, visible: bool = True, id: int | None = None) -> Self:
        return self.separator(large=False, visible=visible, id=id)

    def section(self, builder: SectionBuilder) -> Self:
        self._children.append(builder.build())
        return self

    def action_row(self, builder: ActionRowBuilder) -> Self:
        self._children.append(builder.build())
        return self

    def row(self, builder: ActionRowBuilder) -> Self:
        return self.action_row(builder)

    def button(self, builder: ButtonBuilder, *, inline: bool = True) -> Self:
        built = builder.build()
        tail = self._children[-1] if self._children else None
        if (
            inline
            and isinstance(tail, discord.ui.ActionRow)
            and id(tail) in self._inline_rows
            and len(tail.children) < 5
        ):
            tail.add_item(built)
            return self
        fresh = discord.ui.ActionRow(built)
        self._children.append(fresh)
        if inline:
            self._inline_rows.add(id(fresh))
        return self

    def btn(self, builder: ButtonBuilder, *, inline: bool = True) -> Self:
        return self.button(builder, inline=inline)

    def gallery(self, builder: GalleryBuilder) -> Self:
        self._children.append(builder.build())
        return self

    def nest(self, builder: ContainerBuilder) -> Self:
        self._children.append(builder.build())
        return self

    def child(self, builder: ContainerBuilder) -> Self:
        return self.nest(builder)

    def inner(self, builder: ContainerBuilder) -> Self:
        return self.nest(builder)

    def accent(self, color: discord.Color | int) -> Self:
        self._accent = color
        return self

    def color(self, color: discord.Color | int) -> Self:
        return self.accent(color)

    def colour(self, color: discord.Color | int) -> Self:
        return self.accent(color)

    def border(self, color: discord.Color | int) -> Self:
        return self.accent(color)

    def tint(self, color: discord.Color | int) -> Self:
        return self.accent(color)

    def hue(self, color: discord.Color | int) -> Self:
        return self.accent(color)

    def hex(self, value: str) -> Self:
        return self.accent(discord.Color.from_str(value))

    def rgb(self, r: int, g: int, b: int) -> Self:
        return self.accent(discord.Color.from_rgb(r, g, b))

    def spoiler(self, state: bool = True) -> Self:
        self._spoiler = state
        return self

    def hidden(self, state: bool = True) -> Self:
        self._spoiler = state
        return self

    def id(self, value: int) -> Self:
        self._id = value
        return self

    def build(self) -> discord.ui.Container:
        kwargs: dict[str, Any] = {"spoiler": self._spoiler}
        if self._accent is not None:
            kwargs["accent_color"] = self._accent
        if self._id is not None:
            kwargs["id"] = self._id
        return discord.ui.Container(*self._children, **kwargs)


class GradientColours:
    def __init__(
        self,
        primary: discord.Colour | int | str,
        secondary: discord.Colour | int | str | None = None,
        tertiary: discord.Colour | int | str | None = None,
    ) -> None:
        self._primary: discord.Colour = self._coerce(primary)
        self._secondary: discord.Colour | None = self._coerce(secondary)
        self._tertiary: discord.Colour | None = self._coerce(tertiary)

    @staticmethod
    def _coerce(value: discord.Colour | int | str | None) -> Any:
        if value is None:
            return None
        if isinstance(value, discord.Colour):
            return value
        if isinstance(value, int):
            return discord.Colour(value)
        return discord.Colour.from_str(value)

    @property
    def primary(self) -> discord.Colour:
        return self._primary

    @property
    def secondary(self) -> discord.Colour | None:
        return self._secondary

    @property
    def tertiary(self) -> discord.Colour | None:
        return self._tertiary

    def to_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"colour": self._primary}
        if self._secondary is not None:
            kwargs["secondary_colour"] = self._secondary
        if self._tertiary is not None:
            kwargs["tertiary_colour"] = self._tertiary
        return kwargs

    async def apply(self, role: discord.Role, *, reason: str | None = None) -> discord.Role:
        kwargs = self.to_kwargs()
        if reason is not None:
            kwargs["reason"] = reason
        return await role.edit(**kwargs)


class Vex(discord.ui.LayoutView):
    def __init__(self, *, timeout: float | None = 180.0) -> None:
        super().__init__(timeout=timeout)
        self._locked_to: set[int] | None = None
        self._lock_message: str = "You can't interact with this."
        self._on_timeout_cb: Any = None

    def lock_to(self, *user_ids: int, message: str | None = None) -> Self:
        self._locked_to = {int(u) for u in user_ids}
        if message is not None:
            self._lock_message = message
        return self

    def unlock(self) -> Self:
        self._locked_to = None
        return self

    def on_timeout_do(self, callback: Any) -> Self:
        self._on_timeout_cb = callback
        return self

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._locked_to is None:
            return True
        if interaction.user.id in self._locked_to:
            return True
        await interaction.response.send_message(self._lock_message, ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        for item in self.walk_children() if hasattr(self, "walk_children") else []:
            if hasattr(item, "disabled"):
                item.disabled = True
        if self._on_timeout_cb is not None:
            await discord.utils.maybe_coroutine(self._on_timeout_cb, self)

    def text(self, content: str, *, id: int | None = None) -> Self:
        kwargs: dict[str, Any] = {}
        if id is not None:
            kwargs["id"] = id
        self.add_item(discord.ui.TextDisplay(content, **kwargs))
        return self

    def write(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def line(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def paragraph(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def display(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def label(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def put(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def emit(self, content: str, *, id: int | None = None) -> Self:
        return self.text(content, id=id)

    def heading(self, content: str, level: int = 1, *, id: int | None = None) -> Self:
        prefix = "#" * max(1, min(level, 3))
        return self.text(f"{prefix} {content}", id=id)

    def h1(self, content: str, *, id: int | None = None) -> Self:
        return self.heading(content, 1, id=id)

    def h2(self, content: str, *, id: int | None = None) -> Self:
        return self.heading(content, 2, id=id)

    def h3(self, content: str, *, id: int | None = None) -> Self:
        return self.heading(content, 3, id=id)

    def bold(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"**{content}**", id=id)

    def italic(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"*{content}*", id=id)

    def underline(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"__{content}__", id=id)

    def strikethrough(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"~~{content}~~", id=id)

    def code(self, content: str, lang: str = "", *, id: int | None = None) -> Self:
        return self.text(f"```{lang}\n{content}\n```", id=id)

    def inline_code(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"`{content}`", id=id)

    def quote(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"> {content}", id=id)

    def blockquote(self, content: str, *, id: int | None = None) -> Self:
        return self.text(f"> {content}", id=id)

    def field(self, name: str, value: str, *, id: int | None = None) -> Self:
        return self.text(f"**{name}:** {value}", id=id)

    def kv(self, key: str, value: str, *, id: int | None = None) -> Self:
        return self.field(key, value, id=id)

    def fields(self, mapping: dict[str, str]) -> Self:
        for name, value in mapping.items():
            self.field(name, value)
        return self

    def mention_user(self, user_id: int, *, id: int | None = None) -> Self:
        return self.text(f"<@{user_id}>", id=id)

    def mention_role(self, role_id: int, *, id: int | None = None) -> Self:
        return self.text(f"<@&{role_id}>", id=id)

    def mention_channel(self, channel_id: int, *, id: int | None = None) -> Self:
        return self.text(f"<#{channel_id}>", id=id)

    def timestamp(self, dt_or_ts: Any, fmt: str = "f", *, id: int | None = None) -> Self:
        ts = int(dt_or_ts.timestamp()) if hasattr(dt_or_ts, "timestamp") else int(dt_or_ts)
        return self.text(f"<t:{ts}:{fmt}>", id=id)

    def relative(self, dt_or_ts: Any, *, id: int | None = None) -> Self:
        return self.timestamp(dt_or_ts, "R", id=id)

    def separator(self, *, large: bool = False, visible: bool = True, id: int | None = None) -> Self:
        spacing = discord.SeparatorSpacing.large if large else discord.SeparatorSpacing.small
        kwargs: dict[str, Any] = {}
        if id is not None:
            kwargs["id"] = id
        self.add_item(discord.ui.Separator(spacing=spacing, visible=visible, **kwargs))
        return self

    def divider(self, *, large: bool = False, id: int | None = None) -> Self:
        return self.separator(large=large, visible=True, id=id)

    def rule(self, *, large: bool = False, id: int | None = None) -> Self:
        return self.separator(large=large, visible=True, id=id)

    def hr(self, *, large: bool = False, id: int | None = None) -> Self:
        return self.separator(large=large, visible=True, id=id)

    def gap(self, *, large: bool = False, id: int | None = None) -> Self:
        return self.separator(large=large, visible=False, id=id)

    def spacer(self, *, large: bool = False, id: int | None = None) -> Self:
        return self.separator(large=large, visible=False, id=id)

    def pad(self, *, large: bool = False, id: int | None = None) -> Self:
        return self.separator(large=large, visible=False, id=id)

    def large_separator(self, *, visible: bool = True, id: int | None = None) -> Self:
        return self.separator(large=True, visible=visible, id=id)

    def large_divider(self, *, id: int | None = None) -> Self:
        return self.separator(large=True, visible=True, id=id)

    def large_gap(self, *, id: int | None = None) -> Self:
        return self.separator(large=True, visible=False, id=id)

    def small_separator(self, *, visible: bool = True, id: int | None = None) -> Self:
        return self.separator(large=False, visible=visible, id=id)

    def section(self, builder: SectionBuilder) -> Self:
        self.add_item(builder.build())
        return self

    def aside(self, builder: SectionBuilder) -> Self:
        return self.section(builder)

    def panel(self, builder: SectionBuilder) -> Self:
        return self.section(builder)

    def sidebar(self, builder: SectionBuilder) -> Self:
        return self.section(builder)

    def action_row(self, builder: ActionRowBuilder) -> Self:
        self.add_item(builder.build())
        return self

    def row(self, builder: ActionRowBuilder) -> Self:
        return self.action_row(builder)

    def buttons(self, builder: ActionRowBuilder) -> Self:
        return self.action_row(builder)

    def controls(self, builder: ActionRowBuilder) -> Self:
        return self.action_row(builder)

    def toolbar(self, builder: ActionRowBuilder) -> Self:
        return self.action_row(builder)

    def actions(self, builder: ActionRowBuilder) -> Self:
        return self.action_row(builder)

    def gallery(self, builder: GalleryBuilder) -> Self:
        self.add_item(builder.build())
        return self

    def images(self, builder: GalleryBuilder) -> Self:
        return self.gallery(builder)

    def media(self, builder: GalleryBuilder) -> Self:
        return self.gallery(builder)

    def photos(self, builder: GalleryBuilder) -> Self:
        return self.gallery(builder)

    def grid(self, builder: GalleryBuilder) -> Self:
        return self.gallery(builder)

    def container(self, builder: ContainerBuilder) -> Self:
        self.add_item(builder.build())
        return self

    def box(self, builder: ContainerBuilder) -> Self:
        return self.container(builder)

    def card(self, builder: ContainerBuilder) -> Self:
        return self.container(builder)

    def block(self, builder: ContainerBuilder) -> Self:
        return self.container(builder)

    def frame(self, builder: ContainerBuilder) -> Self:
        return self.container(builder)

    def embed(self, builder: ContainerBuilder) -> Self:
        return self.container(builder)

    def group(self, builder: ContainerBuilder) -> Self:
        return self.container(builder)

    def wrap(self, builder: ContainerBuilder) -> Self:
        return self.container(builder)

    async def send_to(
        self,
        target: discord.abc.Messageable,
        *,
        content: str | None = None,
        files: list[discord.File] | None = None,
        allowed_mentions: discord.AllowedMentions | None = None,
    ) -> discord.Message:
        kwargs: dict[str, Any] = {"view": self}
        if content:
            kwargs["content"] = content
        if files:
            kwargs["files"] = files
        if allowed_mentions:
            kwargs["allowed_mentions"] = allowed_mentions
        return await target.send(**kwargs)

    async def send(
        self,
        target: discord.abc.Messageable,
        *,
        content: str | None = None,
        files: list[discord.File] | None = None,
        allowed_mentions: discord.AllowedMentions | None = None,
    ) -> discord.Message:
        return await self.send_to(target, content=content, files=files, allowed_mentions=allowed_mentions)

    async def dispatch(
        self,
        target: discord.abc.Messageable,
        *,
        files: list[discord.File] | None = None,
    ) -> discord.Message:
        return await self.send_to(target, files=files)

    async def publish(
        self,
        target: discord.abc.Messageable,
        *,
        files: list[discord.File] | None = None,
    ) -> discord.Message:
        return await self.send_to(target, files=files)

    async def post(
        self,
        target: discord.abc.Messageable,
        *,
        files: list[discord.File] | None = None,
    ) -> discord.Message:
        return await self.send_to(target, files=files)

    async def reply_to(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool = False,
        files: list[discord.File] | None = None,
        allowed_mentions: discord.AllowedMentions | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {"view": self, "ephemeral": ephemeral}
        if files:
            kwargs["files"] = files
        if allowed_mentions:
            kwargs["allowed_mentions"] = allowed_mentions
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)

    async def respond(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool = False,
        files: list[discord.File] | None = None,
        allowed_mentions: discord.AllowedMentions | None = None,
    ) -> None:
        await self.reply_to(interaction, ephemeral=ephemeral, files=files, allowed_mentions=allowed_mentions)

    async def answer(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool = False,
    ) -> None:
        await self.reply_to(interaction, ephemeral=ephemeral)

    async def reply(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool = False,
    ) -> None:
        await self.reply_to(interaction, ephemeral=ephemeral)

    async def fire(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool = False,
    ) -> None:
        await self.reply_to(interaction, ephemeral=ephemeral)

    async def edit(
        self,
        interaction: discord.Interaction,
        *,
        allowed_mentions: discord.AllowedMentions | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {"view": self}
        if allowed_mentions:
            kwargs["allowed_mentions"] = allowed_mentions
        if interaction.response.is_done():
            await interaction.edit_original_response(**kwargs)
        else:
            await interaction.response.edit_message(**kwargs)

    async def update(self, interaction: discord.Interaction) -> None:
        await self.edit(interaction)

    async def patch(self, interaction: discord.Interaction) -> None:
        await self.edit(interaction)

    async def refresh(self, interaction: discord.Interaction) -> None:
        await self.edit(interaction)

    async def mutate(self, interaction: discord.Interaction) -> None:
        await self.edit(interaction)

    async def defer(self, interaction: discord.Interaction, *, ephemeral: bool = False, thinking: bool = False) -> None:
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=ephemeral, thinking=thinking)

    async def delete(self, interaction: discord.Interaction) -> None:
        if interaction.response.is_done():
            await interaction.delete_original_response()
        else:
            await interaction.response.defer()
            await interaction.delete_original_response()

    def cooldown(self, *, rate: int, per: float, bucket: commands.BucketType = commands.BucketType.user) -> Self:
        self._cooldown = commands.CooldownMapping.from_cooldown(rate, per, bucket)
        return self

    def slow(self, *, rate: int, per: float, bucket: commands.BucketType = commands.BucketType.user) -> Self:
        return self.cooldown(rate=rate, per=per, bucket=bucket)

    def limit(self, *, rate: int, per: float, bucket: commands.BucketType = commands.BucketType.user) -> Self:
        return self.cooldown(rate=rate, per=per, bucket=bucket)

    def throttle(self, *, rate: int, per: float, bucket: commands.BucketType = commands.BucketType.user) -> Self:
        return self.cooldown(rate=rate, per=per, bucket=bucket)

    def ratelimit(self, *, rate: int, per: float, bucket: commands.BucketType = commands.BucketType.user) -> Self:
        return self.cooldown(rate=rate, per=per, bucket=bucket)

    def reset_cooldown(self, message: discord.Message) -> Self:
        if hasattr(self, "_cooldown") and self._cooldown:
            bucket = self._cooldown.get_bucket(message)
            if bucket:
                bucket.reset()
        return self

    def clear_cooldown(self, message: discord.Message) -> Self:
        return self.reset_cooldown(message)

    def get_cooldown(self, message: discord.Message) -> commands.Cooldown | None:
        if hasattr(self, "_cooldown") and self._cooldown:
            return self._cooldown.get_bucket(message)
        return None

    def is_cooled(self, message: discord.Message) -> bool:
        cd = self.get_cooldown(message)
        if cd is None:
            return False
        retry = cd.update_rate_limit()
        return retry is not None

    def retry_after(self, message: discord.Message) -> float:
        cd = self.get_cooldown(message)
        if cd is None:
            return 0.0
        retry = cd.update_rate_limit()
        return retry if retry else 0.0


PageRenderer = Callable[[int, int, Any], Vex]


class Paginator(discord.ui.LayoutView):
    def __init__(
        self,
        pages: list[Any],
        *,
        renderer: PageRenderer,
        timeout: float | None = 180.0,
        loop: bool = False,
        ephemeral: bool = False,
    ) -> None:
        super().__init__(timeout=timeout)
        self._pages = pages
        self._renderer = renderer
        self._index = 0
        self._loop = loop
        self._ephemeral = ephemeral
        self._message: discord.Message | None = None
        self._build()

    @property
    def current(self) -> int:
        return self._index

    @property
    def total(self) -> int:
        return len(self._pages)

    @property
    def at_start(self) -> bool:
        return self._index == 0

    @property
    def at_end(self) -> bool:
        return self._index == len(self._pages) - 1

    @property
    def current_page(self) -> Any:
        return self._pages[self._index]

    def _build(self) -> None:
        self.clear_items()
        inner = self._renderer(self._index, len(self._pages), self._pages[self._index])
        if isinstance(inner, ContainerBuilder):
            self.add_item(inner.build())
        elif isinstance(inner, (Vex, discord.ui.LayoutView)):
            for child in inner.children:
                self.add_item(child)
        else:
            self.add_item(inner)

        at_start = self._index == 0
        at_end = self._index == len(self._pages) - 1

        first_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u00ab",
            custom_id="vex_page_first",
            disabled=at_start and not self._loop,
        )
        prev_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u2039",
            custom_id="vex_page_prev",
            disabled=at_start and not self._loop,
        )
        next_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u203a",
            custom_id="vex_page_next",
            disabled=at_end and not self._loop,
        )
        last_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u00bb",
            custom_id="vex_page_last",
            disabled=at_end and not self._loop,
        )

        first_btn.callback = self._handle_first
        prev_btn.callback = self._handle_prev
        next_btn.callback = self._handle_next
        last_btn.callback = self._handle_last

        nav_row = discord.ui.ActionRow(first_btn, prev_btn, next_btn, last_btn)
        self.add_item(nav_row)

    async def _sync(self, interaction: discord.Interaction) -> None:
        self._build()
        if interaction.response.is_done():
            await interaction.edit_original_response(view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def _handle_first(self, interaction: discord.Interaction) -> None:
        if self._loop and self.at_start:
            self._index = len(self._pages) - 1
        else:
            self._index = 0
        await self._sync(interaction)

    async def _handle_prev(self, interaction: discord.Interaction) -> None:
        if self.at_start and self._loop:
            self._index = len(self._pages) - 1
        elif not self.at_start:
            self._index -= 1
        await self._sync(interaction)

    async def _handle_next(self, interaction: discord.Interaction) -> None:
        if self.at_end and self._loop:
            self._index = 0
        elif not self.at_end:
            self._index += 1
        await self._sync(interaction)

    async def _handle_last(self, interaction: discord.Interaction) -> None:
        if self._loop and self.at_end:
            self._index = 0
        else:
            self._index = len(self._pages) - 1
        await self._sync(interaction)

    def jump(self, index: int) -> Self:
        self._index = max(0, min(index, len(self._pages) - 1))
        self._build()
        return self

    def seek(self, index: int) -> Self:
        return self.jump(index)

    def go_to(self, index: int) -> Self:
        return self.jump(index)

    def page(self, index: int) -> Self:
        return self.jump(index)

    async def send_to(
        self,
        target: discord.abc.Messageable,
        *,
        files: list[discord.File] | None = None,
    ) -> discord.Message:
        kwargs: dict[str, Any] = {"view": self}
        if files:
            kwargs["files"] = files
        self._message = await target.send(**kwargs)
        return self._message

    async def send(
        self,
        target: discord.abc.Messageable,
        *,
        files: list[discord.File] | None = None,
    ) -> discord.Message:
        return await self.send_to(target, files=files)

    async def dispatch(
        self,
        target: discord.abc.Messageable,
        *,
        files: list[discord.File] | None = None,
    ) -> discord.Message:
        return await self.send_to(target, files=files)

    async def reply_to(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool | None = None,
        files: list[discord.File] | None = None,
    ) -> None:
        use_ephemeral = ephemeral if ephemeral is not None else self._ephemeral
        kwargs: dict[str, Any] = {"view": self, "ephemeral": use_ephemeral}
        if files:
            kwargs["files"] = files
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)

    async def respond(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool | None = None,
    ) -> None:
        await self.reply_to(interaction, ephemeral=ephemeral)

    async def answer(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool | None = None,
    ) -> None:
        await self.reply_to(interaction, ephemeral=ephemeral)

    async def reply(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool | None = None,
    ) -> None:
        await self.reply_to(interaction, ephemeral=ephemeral)


def vex(*, timeout: float | None = 180.0) -> Vex:
    return Vex(timeout=timeout)


class TextInputBuilder:
    def __init__(self, key: str, label: str) -> None:
        self._key = key
        self._label = label
        self._style = discord.TextStyle.short
        self._placeholder: str | None = None
        self._default: str | None = None
        self._required: bool = True
        self._min: int | None = None
        self._max: int | None = None

    def label(self, text: str) -> Self:
        self._label = text
        return self

    def short(self) -> Self:
        self._style = discord.TextStyle.short
        return self

    def line(self) -> Self:
        self._style = discord.TextStyle.short
        return self

    def paragraph(self) -> Self:
        self._style = discord.TextStyle.paragraph
        return self

    def long(self) -> Self:
        self._style = discord.TextStyle.paragraph
        return self

    def multiline(self) -> Self:
        self._style = discord.TextStyle.paragraph
        return self

    def placeholder(self, text: str) -> Self:
        self._placeholder = text
        return self

    def hint(self, text: str) -> Self:
        self._placeholder = text
        return self

    def default(self, text: str) -> Self:
        self._default = text
        return self

    def prefill(self, text: str) -> Self:
        self._default = text
        return self

    def required(self, state: bool = True) -> Self:
        self._required = state
        return self

    def optional(self) -> Self:
        self._required = False
        return self

    def min(self, value: int) -> Self:
        self._min = value
        return self

    def max(self, value: int) -> Self:
        self._max = value
        return self

    def length(self, min_val: int, max_val: int) -> Self:
        self._min = min_val
        self._max = max_val
        return self

    def build(self) -> discord.ui.TextInput:
        kwargs: dict[str, Any] = {
            "label": self._label,
            "style": self._style,
            "custom_id": self._key,
            "required": self._required,
        }
        if self._placeholder is not None:
            kwargs["placeholder"] = self._placeholder
        if self._default is not None:
            kwargs["default"] = self._default
        if self._min is not None:
            kwargs["min_length"] = self._min
        if self._max is not None:
            kwargs["max_length"] = self._max
        return discord.ui.TextInput(**kwargs)


class _VexModal(discord.ui.Modal):
    def __init__(self, title: str, timeout: float | None, custom_id: str | None,
                 inputs: list[discord.ui.TextInput], on_submit: Any, on_error: Any) -> None:
        kwargs: dict[str, Any] = {"title": title}
        if timeout is not None:
            kwargs["timeout"] = timeout
        if custom_id is not None:
            kwargs["custom_id"] = custom_id
        super().__init__(**kwargs)
        self._inputs = inputs
        self._on_submit = on_submit
        self._on_error = on_error
        for item in inputs:
            self.add_item(item)

    def values(self) -> dict[str, str]:
        return {item.custom_id: item.value for item in self._inputs}

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if self._on_submit is None:
            await interaction.response.defer()
            return
        await discord.utils.maybe_coroutine(self._on_submit, interaction, self.values())

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if self._on_error is not None:
            await discord.utils.maybe_coroutine(self._on_error, interaction, error)
        else:
            await super().on_error(interaction, error)


class ModalBuilder:
    def __init__(self, title: str = "Form") -> None:
        self._title = title
        self._timeout: float | None = 180.0
        self._custom_id: str | None = None
        self._inputs: list[discord.ui.TextInput] = []
        self._on_submit: Any = None
        self._on_error: Any = None

    def title(self, text: str) -> Self:
        self._title = text
        return self

    def name(self, text: str) -> Self:
        self._title = text
        return self

    def timeout(self, seconds: float | None) -> Self:
        self._timeout = seconds
        return self

    def custom_id(self, value: str) -> Self:
        self._custom_id = value
        return self

    def cid(self, value: str) -> Self:
        self._custom_id = value
        return self

    def field(self, key: str, label: str, **kwargs: Any) -> Self:
        builder = TextInputBuilder(key, label)
        if kwargs.get("paragraph") or kwargs.get("long"):
            builder.paragraph()
        if "placeholder" in kwargs:
            builder.placeholder(kwargs["placeholder"])
        if "default" in kwargs:
            builder.default(kwargs["default"])
        if "required" in kwargs:
            builder.required(kwargs["required"])
        if "min" in kwargs:
            builder.min(kwargs["min"])
        if "max" in kwargs:
            builder.max(kwargs["max"])
        self._inputs.append(builder.build())
        return self

    def short(self, key: str, label: str, **kwargs: Any) -> Self:
        kwargs.pop("paragraph", None)
        kwargs.pop("long", None)
        return self.field(key, label, **kwargs)

    def paragraph(self, key: str, label: str, **kwargs: Any) -> Self:
        kwargs["paragraph"] = True
        return self.field(key, label, **kwargs)

    def input(self, builder: TextInputBuilder) -> Self:
        self._inputs.append(builder.build())
        return self

    def add(self, builder: TextInputBuilder) -> Self:
        self._inputs.append(builder.build())
        return self

    def on_submit(self, callback: Any) -> Self:
        self._on_submit = callback
        return self

    def handler(self, callback: Any) -> Self:
        self._on_submit = callback
        return self

    def on_error(self, callback: Any) -> Self:
        self._on_error = callback
        return self

    def build(self) -> discord.ui.Modal:
        return _VexModal(self._title, self._timeout, self._custom_id,
                         self._inputs, self._on_submit, self._on_error)

    async def send(self, interaction: discord.Interaction) -> discord.ui.Modal:
        modal = self.build()
        await interaction.response.send_modal(modal)
        return modal

    async def open(self, interaction: discord.Interaction) -> discord.ui.Modal:
        return await self.send(interaction)

    async def prompt(self, interaction: discord.Interaction) -> discord.ui.Modal:
        return await self.send(interaction)


def new(*, timeout: float | None = 180.0) -> Vex:
    return Vex(timeout=timeout)


def build(*, timeout: float | None = 180.0) -> Vex:
    return Vex(timeout=timeout)


def create(*, timeout: float | None = 180.0) -> Vex:
    return Vex(timeout=timeout)


def make(*, timeout: float | None = 180.0) -> Vex:
    return Vex(timeout=timeout)


def layout(*, timeout: float | None = 180.0) -> Vex:
    return Vex(timeout=timeout)


def view(*, timeout: float | None = 180.0) -> Vex:
    return Vex(timeout=timeout)


def message(*, timeout: float | None = 180.0) -> Vex:
    return Vex(timeout=timeout)


def button() -> ButtonBuilder:
    return ButtonBuilder()


def btn() -> ButtonBuilder:
    return ButtonBuilder()


def select() -> SelectBuilder:
    return SelectBuilder()


def dropdown() -> SelectBuilder:
    return SelectBuilder()


def channel_select() -> TypedSelectBuilder:
    return TypedSelectBuilder("channel")


def channel_picker() -> TypedSelectBuilder:
    return TypedSelectBuilder("channel")


def user_select() -> TypedSelectBuilder:
    return TypedSelectBuilder("user")


def user_picker() -> TypedSelectBuilder:
    return TypedSelectBuilder("user")


def role_select() -> TypedSelectBuilder:
    return TypedSelectBuilder("role")


def role_picker() -> TypedSelectBuilder:
    return TypedSelectBuilder("role")


def mentionable_select() -> TypedSelectBuilder:
    return TypedSelectBuilder("mentionable")


def action_row(*, id: int | None = None) -> ActionRowBuilder:
    return ActionRowBuilder(id=id)


def row(*, id: int | None = None) -> ActionRowBuilder:
    return ActionRowBuilder(id=id)


def section() -> SectionBuilder:
    return SectionBuilder()


def aside() -> SectionBuilder:
    return SectionBuilder()


def panel() -> SectionBuilder:
    return SectionBuilder()


def gallery(*, id: int | None = None) -> GalleryBuilder:
    return GalleryBuilder(id=id)


def images(*, id: int | None = None) -> GalleryBuilder:
    return GalleryBuilder(id=id)


def media(*, id: int | None = None) -> GalleryBuilder:
    return GalleryBuilder(id=id)


def container(*, id: int | None = None) -> ContainerBuilder:
    return ContainerBuilder(id=id)


def box(*, id: int | None = None) -> ContainerBuilder:
    return ContainerBuilder(id=id)


def card(*, id: int | None = None) -> ContainerBuilder:
    return ContainerBuilder(id=id)


def frame(*, id: int | None = None) -> ContainerBuilder:
    return ContainerBuilder(id=id)


def gradient(
    primary: discord.Colour | int | str,
    secondary: discord.Colour | int | str | None = None,
    tertiary: discord.Colour | int | str | None = None,
) -> GradientColours:
    return GradientColours(primary, secondary, tertiary)


def paginator(
    pages: list[Any],
    *,
    renderer: PageRenderer,
    timeout: float | None = 180.0,
    loop: bool = False,
    ephemeral: bool = False,
) -> Paginator:
    return Paginator(pages, renderer=renderer, timeout=timeout, loop=loop, ephemeral=ephemeral)


def paginate(
    pages: list[Any],
    *,
    renderer: PageRenderer,
    timeout: float | None = 180.0,
    loop: bool = False,
    ephemeral: bool = False,
) -> Paginator:
    return Paginator(pages, renderer=renderer, timeout=timeout, loop=loop, ephemeral=ephemeral)


def pages(
    data: list[Any],
    *,
    renderer: PageRenderer,
    timeout: float | None = 180.0,
    loop: bool = False,
) -> Paginator:
    return Paginator(data, renderer=renderer, timeout=timeout, loop=loop)


def modal(title: str = "Form") -> ModalBuilder:
    return ModalBuilder(title)


def form(title: str = "Form") -> ModalBuilder:
    return ModalBuilder(title)


def prompt(title: str = "Form") -> ModalBuilder:
    return ModalBuilder(title)


def text_input(key: str, label: str) -> TextInputBuilder:
    return TextInputBuilder(key, label)


def field_input(key: str, label: str) -> TextInputBuilder:
    return TextInputBuilder(key, label)




class CommandInfo:
    def __init__(self, name: str, func: Any | None = None) -> None:
        self.name: str = name
        self.func: Any | None = func
        self.description: str = ""
        self.syntax: str = ""
        self.example: str = ""
        self.category: str = "General"
        self.hidden: bool = False
        self.aliases: list[str] = []


def _attach_meta(func: Any, **kwargs: Any) -> CommandInfo:
    if not hasattr(func, "__vex_help__"):
        func.__vex_help__ = CommandInfo(getattr(func, "__name__", "unknown"), func)
    info = func.__vex_help__
    for k, v in kwargs.items():
        setattr(info, k, v)
    return info


def cmd(name: str | Callable[..., Any] | None = None, *, aliases: list[str] | None = None) -> Callable[[Any], Any]:
    def decorator(func: Any) -> Any:
        actual_name = name if isinstance(name, str) else getattr(func, "__name__", "unknown")
        info = CommandInfo(actual_name, func)
        if aliases:
            info.aliases = aliases
        func.__vex_help__ = info
        return func
    if callable(name):
        return decorator(name)
    return decorator


def cmd_desc(text: str) -> Callable[[Any], Any]:
    def decorator(func: Any) -> Any:
        _attach_meta(func, description=text)
        return func
    return decorator


def cmd_syntax(text: str) -> Callable[[Any], Any]:
    def decorator(func: Any) -> Any:
        _attach_meta(func, syntax=text)
        return func
    return decorator


def cmd_example(text: str) -> Callable[[Any], Any]:
    def decorator(func: Any) -> Any:
        _attach_meta(func, example=text)
        return func
    return decorator


def cmd_category(text: str) -> Callable[[Any], Any]:
    def decorator(func: Any) -> Any:
        _attach_meta(func, category=text)
        return func
    return decorator


def cmd_hidden(state: bool = True) -> Callable[[Any], Any]:
    def decorator(func: Any) -> Any:
        _attach_meta(func, hidden=state)
        return func
    return decorator


class HelpRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, CommandInfo] = {}

    def scan(self, obj: Any) -> Self:
        import inspect
        seen: set[str] = set()
        targets = [obj]
        if not inspect.isclass(obj):
            targets.append(type(obj))
        for target in targets:
            for name in dir(target):
                if name.startswith("_"):
                    continue
                try:
                    member = getattr(target, name, None)
                except Exception:
                    continue
                if member is None:
                    continue

                if hasattr(member, "__vex_help__"):
                    info = member.__vex_help__
                    if info.name not in seen:
                        seen.add(info.name)
                        self._commands[info.name] = info
                    continue

                if inspect.isfunction(member) and hasattr(member, "__vex_help__"):
                    info = member.__vex_help__
                    if info.name not in seen:
                        seen.add(info.name)
                        self._commands[info.name] = info
                    continue

                callback = getattr(member, "callback", None)
                if callback is not None and hasattr(callback, "__vex_help__"):
                    info = callback.__vex_help__
                    if info.name not in seen:
                        seen.add(info.name)
                        self._commands[info.name] = info
                    continue

                if not inspect.isclass(target) and inspect.ismethod(member):
                    underlying = getattr(member, "__func__", None)
                    if underlying and hasattr(underlying, "__vex_help__"):
                        info = underlying.__vex_help__
                        if info.name not in seen:
                            seen.add(info.name)
                            self._commands[info.name] = info
                        continue
        return self

    def get(self, name: str) -> CommandInfo | None:
        return self._commands.get(name)

    def list(self, *, category: str | None = None, include_hidden: bool = False) -> list[CommandInfo]:
        cmds = list(self._commands.values())
        if category is not None:
            cmds = [c for c in cmds if c.category == category]
        if not include_hidden:
            cmds = [c for c in cmds if not c.hidden]
        return cmds

    def help_card(self, name: str) -> ContainerBuilder:
        info = self.get(name)
        if info is None:
            return container().text("Command not found.")
        cb = container()
        cb.h2(info.name)
        if info.description:
            cb.text(info.description)
        if info.syntax:
            cb.field("Syntax", info.syntax)
        if info.example:
            cb.field("Example", info.example)
        if info.aliases:
            cb.field("Aliases", ", ".join(info.aliases))
        return cb

    def help_all(self, *, category: str | None = None, include_hidden: bool = False) -> list[ContainerBuilder]:
        return [self.help_card(c.name) for c in self.list(category=category, include_hidden=include_hidden)]

    def paginator(self, *, category: str | None = None, include_hidden: bool = False, timeout: float | None = 180.0, loop: bool = False) -> Paginator:
        pages = self.help_all(category=category, include_hidden=include_hidden)

        def renderer(idx: int, total: int, page: Any) -> ContainerBuilder:
            return page

        return Paginator(pages, renderer=renderer, timeout=timeout, loop=loop)


def registry() -> HelpRegistry:
    return HelpRegistry()


class VexError:
    MISSING_PERMISSIONS = "You do not have permission to do that."
    BOT_MISSING_PERMISSIONS = "I do not have permission to do that."
    NOT_FOUND = "That could not be found."
    ALREADY_EXISTS = "That already exists."
    FORBIDDEN = "You are not allowed to do that."
    OWNER_ONLY = "Only the bot owner can do that."
    SERVER_ONLY = "This can only be used in a server."
    DM_ONLY = "This can only be used in direct messages."
    NSFW_ONLY = "This can only be used in age-restricted channels."
    COOLDOWN = "You are using this too fast. Please wait and try again."
    MAX_CONCURRENCY = "Too many people are using this at once. Please try again shortly."
    DISABLED = "This command is currently disabled."
    CHANNEL_NOT_FOUND = "That channel could not be found."
    ROLE_NOT_FOUND = "That role could not be found."
    MEMBER_NOT_FOUND = "That member could not be found."
    USER_NOT_FOUND = "That user could not be found."
    GUILD_NOT_FOUND = "That server could not be found."
    MESSAGE_NOT_FOUND = "That message could not be found."
    EMOJI_NOT_FOUND = "That emoji could not be found."
    INVALID_ARGUMENT = "You provided an invalid value."
    MISSING_ARGUMENT = "You are missing a required value."
    TOO_MANY_ARGUMENTS = "You provided too many values."
    BAD_UNION = "None of the accepted types matched your input."
    CONVERSION_FAILED = "Your input could not be converted to the expected type."
    EXPECTED_INT = "A whole number is required."
    EXPECTED_FLOAT = "A number is required."
    EXPECTED_BOOL = "A yes or no value is required."
    VALUE_TOO_LONG = "Your input is too long."
    VALUE_TOO_SHORT = "Your input is too short."
    VALUE_OUT_OF_RANGE = "Your value is outside the allowed range."
    HTTP_ERROR = "A network error occurred. Please try again."
    RATE_LIMITED = "The bot is being rate limited. Please try again in a moment."
    FORBIDDEN_RESPONSE = "I was denied permission when trying to complete that action."
    NOT_FOUND_RESPONSE = "The resource I was trying to reach no longer exists."
    BOT_NO_ROLE = "I do not have the required role to do that."
    HIERARCHY_ERROR = "That user is above me in the role hierarchy."
    USER_HIERARCHY_ERROR = "You cannot perform that action on someone at or above your role."
    CANNOT_DM = "I could not send a direct message to that user."
    CANNOT_EDIT = "I cannot edit that message."
    CANNOT_DELETE = "I cannot delete that message."
    CANNOT_PIN = "I cannot pin that message."
    CANNOT_UNPIN = "I cannot unpin that message."
    CANNOT_REACT = "I cannot add reactions to that message."
    CANNOT_SEND = "I cannot send messages in that channel."
    CANNOT_EMBED = "I cannot send embeds in that channel."
    CANNOT_ATTACH = "I cannot attach files in that channel."
    CANNOT_MENTION = "I cannot use mentions in that channel."
    CANNOT_MANAGE_MESSAGES = "I cannot manage messages in that channel."
    CANNOT_MANAGE_ROLES = "I cannot manage roles."
    CANNOT_MANAGE_CHANNELS = "I cannot manage channels."
    CANNOT_KICK = "I cannot kick that member."
    CANNOT_BAN = "I cannot ban that member."
    CANNOT_TIMEOUT = "I cannot timeout that member."
    CANNOT_DEAFEN = "I cannot deafen that member."
    CANNOT_MUTE = "I cannot mute that member."
    CANNOT_MOVE = "I cannot move that member."
    ALREADY_BANNED = "That user is already banned."
    NOT_BANNED = "That user is not banned."
    ALREADY_MUTED = "That member is already muted."
    NOT_MUTED = "That member is not muted."
    SELF_ACTION = "You cannot perform this action on yourself."
    BOT_ACTION = "You cannot perform this action on a bot."
    ALREADY_IN_VOICE = "You are already in a voice channel."
    NOT_IN_VOICE = "You need to be in a voice channel to do that."
    BOT_NOT_IN_VOICE = "I am not in a voice channel."
    VOICE_CHANNEL_FULL = "That voice channel is full."
    UNEXPECTED = "Something went wrong. Please try again."
    TIMED_OUT = "This interaction timed out."
    INTERACTION_FAILED = "This interaction could not be completed."
    ALREADY_RESPONDED = "This interaction has already been responded to."
    UNKNOWN_INTERACTION = "This interaction is no longer valid."
    CONFIRM_CANCELLED = "Action cancelled."
    CONFIRM_TIMEOUT = "Confirmation timed out. Action cancelled."
    NOT_CONFIRMED = "You did not confirm the action."
    DATABASE_ERROR = "A database error occurred. Please try again."
    CONFIG_MISSING = "This feature has not been configured for this server."
    FEATURE_DISABLED = "This feature is disabled."
    API_ERROR = "An external service returned an error. Please try again."
    API_TIMEOUT = "An external service took too long to respond."
    PARSE_ERROR = "The response could not be understood."
    ATTACHMENT_REQUIRED = "You must attach a file."
    INVALID_ATTACHMENT = "That file type is not accepted."
    ATTACHMENT_TOO_LARGE = "That file is too large."
    NO_RESULTS = "No results were found."
    EMPTY_INPUT = "You did not provide any input."
    DUPLICATE_INPUT = "You provided the same value more than once."
    NUMERIC_ONLY = "Only numbers are accepted here."
    TEXT_ONLY = "Only text is accepted here."
    URL_REQUIRED = "A valid URL is required."
    INVALID_URL = "That URL is not valid."
    IMAGE_REQUIRED = "An image is required."
    INVALID_IMAGE = "That is not a valid image."
    INVALID_COLOR = "That is not a valid colour."
    INVALID_DATE = "That is not a valid date."
    INVALID_TIME = "That is not a valid time."
    INVALID_DURATION = "That is not a valid duration."
    INVALID_ID = "That is not a valid ID."
    INVALID_MENTION = "That is not a valid mention."
    INVALID_COMMAND = "That command does not exist."
    SUBCOMMAND_REQUIRED = "You must specify a subcommand."
    UNKNOWN_SUBCOMMAND = "That subcommand does not exist."
    SETUP_REQUIRED = "You need to run the setup command first."
    PREMIUM_REQUIRED = "This feature requires a premium subscription."
    VERIFICATION_REQUIRED = "You need to be verified to do that."
    AGE_RESTRICTED = "You must be of legal age to use this feature."
    TERMS_REQUIRED = "You must accept the terms before doing that."
    BLACKLISTED = "You are not allowed to use this bot."
    SERVER_BLACKLISTED = "This server is not allowed to use this bot."
    MAINTENANCE = "The bot is currently under maintenance. Please try again later."
    UNKNOWN = "An unknown error occurred."


class ConfirmView(discord.ui.LayoutView):
    def __init__(
        self,
        *,
        prompt: str = "Are you sure?",
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        timeout: float | None = 30.0,
        ephemeral: bool = True,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._prompt = prompt
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._result: bool | None = None
        self._future: asyncio.Future[bool] = asyncio.get_event_loop().create_future()

        confirm_btn = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label=confirm_label,
            custom_id="vex_confirm_yes",
        )
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label=cancel_label,
            custom_id="vex_confirm_no",
        )
        confirm_btn.callback = self._handle_confirm
        cancel_btn.callback = self._handle_cancel

        self.add_item(discord.ui.TextDisplay(prompt))
        self.add_item(discord.ui.ActionRow(confirm_btn, cancel_btn))

    @property
    def result(self) -> bool | None:
        return self._result

    @property
    def confirmed(self) -> bool:
        return self._result is True

    @property
    def cancelled(self) -> bool:
        return self._result is False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def _handle_confirm(self, interaction: discord.Interaction) -> None:
        self._result = True
        self.stop()
        if not self._future.done():
            self._future.set_result(True)
        await interaction.response.edit_message(view=self)

    async def _handle_cancel(self, interaction: discord.Interaction) -> None:
        self._result = False
        self.stop()
        if not self._future.done():
            self._future.set_result(False)
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        self._result = None
        if not self._future.done():
            self._future.set_result(False)

    async def wait_result(self) -> bool:
        return await self._future

    async def send_to(
        self,
        target: discord.abc.Messageable,
    ) -> bool:
        await target.send(view=self)
        return await self.wait_result()

    async def reply_to(
        self,
        interaction: discord.Interaction,
    ) -> bool:
        if interaction.response.is_done():
            await interaction.followup.send(view=self, ephemeral=self._ephemeral)
        else:
            await interaction.response.send_message(view=self, ephemeral=self._ephemeral)
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> bool:
        return await self.reply_to(interaction)

    async def ask(self, interaction: discord.Interaction) -> bool:
        return await self.reply_to(interaction)

    async def prompt_user(self, interaction: discord.Interaction) -> bool:
        return await self.reply_to(interaction)

    async def confirm(self, interaction: discord.Interaction) -> bool:
        return await self.reply_to(interaction)


def confirm_view(
    prompt: str = "Are you sure?",
    *,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    timeout: float | None = 30.0,
    ephemeral: bool = True,
    owner_id: int | None = None,
) -> ConfirmView:
    return ConfirmView(
        prompt=prompt,
        confirm_label=confirm_label,
        cancel_label=cancel_label,
        timeout=timeout,
        ephemeral=ephemeral,
        owner_id=owner_id,
    )


def confirm(
    prompt: str = "Are you sure?",
    *,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    timeout: float | None = 30.0,
    ephemeral: bool = True,
    owner_id: int | None = None,
) -> ConfirmView:
    return ConfirmView(
        prompt=prompt,
        confirm_label=confirm_label,
        cancel_label=cancel_label,
        timeout=timeout,
        ephemeral=ephemeral,
        owner_id=owner_id,
    )


def ask(
    prompt: str = "Are you sure?",
    *,
    owner_id: int | None = None,
    ephemeral: bool = True,
) -> ConfirmView:
    return ConfirmView(prompt=prompt, owner_id=owner_id, ephemeral=ephemeral)


__all__ = [
    "Vex",
    "Paginator",
    "ButtonBuilder",
    "SelectBuilder",
    "SelectOptionBuilder",
    "ActionRowBuilder",
    "SectionBuilder",
    "GalleryBuilder",
    "ContainerBuilder",
    "TypedSelectBuilder",
    "ModalBuilder",
    "TextInputBuilder",
    "PageRenderer",
    "GradientColours",
    "vex",
    "new",
    "build",
    "create",
    "make",
    "layout",
    "view",
    "message",
    "button",
    "btn",
    "select",
    "dropdown",
    "channel_select",
    "channel_picker",
    "user_select",
    "user_picker",
    "role_select",
    "role_picker",
    "mentionable_select",
    "action_row",
    "row",
    "section",
    "aside",
    "panel",
    "gallery",
    "images",
    "media",
    "container",
    "box",
    "card",
    "frame",
    "gradient",
    "paginator",
    "paginate",
    "pages",
    "modal",
    "form",
    "prompt",
    "text_input",
    "field_input",
    "CommandInfo",
    "cmd",
    "cmd_desc",
    "cmd_syntax",
    "cmd_example",
    "cmd_category",
    "cmd_hidden",
    "HelpRegistry",
    "registry",
    "VexError",
    "ConfirmView",
    "confirm_view",
    "confirm",
    "ask",
    "MultiConfirmView",
    "multi_confirm",
    "TimedConfirmView",
    "timed_confirm",
    "ChoiceView",
    "choice_view",
    "choice",
    "JumpSelectPaginator",
    "PageGroup",
    "grouped_paginator",
    "InfinitePaginator",
    "ScrollPaginator",
    "scroll_paginator",
    "PromptInput",
    "prompt_input",
    "wait_input",
    "edit_to_v2",
    "disable_all",
    "freeze_view",
    "AutoDeleteView",
    "auto_delete",
    "error_card",
    "success_card",
    "info_card",
    "SelectMenu",
    "select_menu",
    "pick",
    "RolePickerView",
    "role_picker",
    "ChannelPickerView",
    "channel_picker_view",
    "UserPickerView",
    "user_picker_view",
    "CooldownStore",
    "cooldown_store",
    "GlobalCooldown",
    "global_cooldown",
    "CooldownCard",
    "cooldown_card",
    "cmd_alias",
    "HelpRegistry",
    "safe_defer",
    "safe_edit",
    "safe_delete",
    "AuditCard",
    "audit_card",
    "DiffCard",
    "diff_card",
]


class MultiConfirmView(discord.ui.LayoutView):
    def __init__(
        self,
        *,
        prompt: str = "This action requires confirmation from multiple users.",
        threshold: int = 2,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        timeout: float | None = 60.0,
        ephemeral: bool = False,
    ) -> None:
        super().__init__(timeout=timeout)
        self._prompt = prompt
        self._threshold = threshold
        self._ephemeral = ephemeral
        self._confirmed_by: set[int] = set()
        self._cancelled: bool = False
        self._future: asyncio.Future[bool] = asyncio.get_event_loop().create_future()

        confirm_btn = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label=confirm_label,
            custom_id="vex_mconfirm_yes",
        )
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label=cancel_label,
            custom_id="vex_mconfirm_no",
        )
        confirm_btn.callback = self._handle_confirm
        cancel_btn.callback = self._handle_cancel

        self._text_id = 9001
        self.add_item(discord.ui.TextDisplay(self._current_text(), id=self._text_id))
        self.add_item(discord.ui.ActionRow(confirm_btn, cancel_btn))

    def _current_text(self) -> str:
        count = len(self._confirmed_by)
        return f"{self._prompt}\n\n{count}/{self._threshold} confirmations received."

    async def _handle_confirm(self, interaction: discord.Interaction) -> None:
        self._confirmed_by.add(interaction.user.id)
        if len(self._confirmed_by) >= self._threshold:
            self._future.set_result(True) if not self._future.done() else None
            self.stop()
        self.clear_items()
        self.add_item(discord.ui.TextDisplay(self._current_text(), id=self._text_id))
        confirm_btn = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Confirm",
            custom_id="vex_mconfirm_yes",
            disabled=len(self._confirmed_by) >= self._threshold,
        )
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancel",
            custom_id="vex_mconfirm_no",
        )
        confirm_btn.callback = self._handle_confirm
        cancel_btn.callback = self._handle_cancel
        self.add_item(discord.ui.ActionRow(confirm_btn, cancel_btn))
        await interaction.response.edit_message(view=self)

    async def _handle_cancel(self, interaction: discord.Interaction) -> None:
        self._cancelled = True
        self.stop()
        if not self._future.done():
            self._future.set_result(False)
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        if not self._future.done():
            self._future.set_result(False)

    async def wait_result(self) -> bool:
        return await self._future

    async def reply_to(self, interaction: discord.Interaction) -> bool:
        kwargs: dict[str, Any] = {"view": self, "ephemeral": self._ephemeral}
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> bool:
        return await self.reply_to(interaction)

    async def send_to(self, target: discord.abc.Messageable) -> bool:
        await target.send(view=self)
        return await self.wait_result()

    @property
    def confirmed_by(self) -> set[int]:
        return set(self._confirmed_by)

    @property
    def cancelled(self) -> bool:
        return self._cancelled


def multi_confirm(
    prompt: str = "This action requires confirmation from multiple users.",
    *,
    threshold: int = 2,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    timeout: float | None = 60.0,
    ephemeral: bool = False,
) -> MultiConfirmView:
    return MultiConfirmView(
        prompt=prompt,
        threshold=threshold,
        confirm_label=confirm_label,
        cancel_label=cancel_label,
        timeout=timeout,
        ephemeral=ephemeral,
    )


class TimedConfirmView(discord.ui.LayoutView):
    def __init__(
        self,
        *,
        prompt: str = "Are you sure?",
        seconds: int = 30,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        ephemeral: bool = True,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=float(seconds))
        self._prompt = prompt
        self._seconds = seconds
        self._remaining = seconds
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._result: bool | None = None
        self._future: asyncio.Future[bool] = asyncio.get_event_loop().create_future()
        self._message: discord.Message | None = None
        self._tick_task: asyncio.Task[None] | None = None

        confirm_btn = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label=confirm_label,
            custom_id="vex_tconfirm_yes",
        )
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label=cancel_label,
            custom_id="vex_tconfirm_no",
        )
        confirm_btn.callback = self._handle_confirm
        cancel_btn.callback = self._handle_cancel
        self.add_item(discord.ui.TextDisplay(self._current_text()))
        self.add_item(discord.ui.ActionRow(confirm_btn, cancel_btn))

    def _current_text(self) -> str:
        return f"{self._prompt}\n\nThis will expire in {self._remaining}s."

    async def _tick(self) -> None:
        while self._remaining > 0 and self._result is None:
            await asyncio.sleep(1)
            self._remaining -= 1
            if self._message is not None and self._result is None:
                self.clear_items()
                self.add_item(discord.ui.TextDisplay(self._current_text()))
                confirm_btn = discord.ui.Button(
                    style=discord.ButtonStyle.success,
                    label="Confirm",
                    custom_id="vex_tconfirm_yes",
                )
                cancel_btn = discord.ui.Button(
                    style=discord.ButtonStyle.danger,
                    label="Cancel",
                    custom_id="vex_tconfirm_no",
                )
                confirm_btn.callback = self._handle_confirm
                cancel_btn.callback = self._handle_cancel
                self.add_item(discord.ui.ActionRow(confirm_btn, cancel_btn))
                try:
                    await self._message.edit(view=self)
                except discord.HTTPException:
                    break

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def _handle_confirm(self, interaction: discord.Interaction) -> None:
        self._result = True
        self.stop()
        if self._tick_task:
            self._tick_task.cancel()
        if not self._future.done():
            self._future.set_result(True)
        await interaction.response.edit_message(view=self)

    async def _handle_cancel(self, interaction: discord.Interaction) -> None:
        self._result = False
        self.stop()
        if self._tick_task:
            self._tick_task.cancel()
        if not self._future.done():
            self._future.set_result(False)
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        self._result = None
        if not self._future.done():
            self._future.set_result(False)

    async def wait_result(self) -> bool:
        return await self._future

    async def reply_to(self, interaction: discord.Interaction) -> bool:
        kwargs: dict[str, Any] = {"view": self, "ephemeral": self._ephemeral}
        if interaction.response.is_done():
            msg = await interaction.followup.send(**kwargs, wait=True)
        else:
            await interaction.response.send_message(**kwargs)
            msg = await interaction.original_response()
        self._message = msg
        self._tick_task = asyncio.create_task(self._tick())
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> bool:
        return await self.reply_to(interaction)

    async def send_to(self, target: discord.abc.Messageable) -> bool:
        self._message = await target.send(view=self)
        self._tick_task = asyncio.create_task(self._tick())
        return await self.wait_result()

    @property
    def result(self) -> bool | None:
        return self._result


def timed_confirm(
    prompt: str = "Are you sure?",
    *,
    seconds: int = 30,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    ephemeral: bool = True,
    owner_id: int | None = None,
) -> TimedConfirmView:
    return TimedConfirmView(
        prompt=prompt,
        seconds=seconds,
        confirm_label=confirm_label,
        cancel_label=cancel_label,
        ephemeral=ephemeral,
        owner_id=owner_id,
    )


class ChoiceView(discord.ui.LayoutView):
    def __init__(
        self,
        choices: dict[str, str],
        *,
        prompt: str = "Choose an option.",
        timeout: float | None = 60.0,
        ephemeral: bool = True,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._prompt = prompt
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._result: str | None = None
        self._future: asyncio.Future[str | None] = asyncio.get_event_loop().create_future()

        self.add_item(discord.ui.TextDisplay(prompt))
        buttons: list[discord.ui.Button] = []
        for key, label in list(choices.items())[:5]:
            btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label=label,
                custom_id=f"vex_choice_{key}",
            )
            btn.callback = self._make_handler(key)
            buttons.append(btn)
        self.add_item(discord.ui.ActionRow(*buttons))

    def _make_handler(self, key: str) -> Any:
        async def handler(interaction: discord.Interaction) -> None:
            self._result = key
            self.stop()
            if not self._future.done():
                self._future.set_result(key)
            await interaction.response.edit_message(view=self)
        return handler

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if not self._future.done():
            self._future.set_result(None)

    async def wait_result(self) -> str | None:
        return await self._future

    async def reply_to(self, interaction: discord.Interaction) -> str | None:
        kwargs: dict[str, Any] = {"view": self, "ephemeral": self._ephemeral}
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> str | None:
        return await self.reply_to(interaction)

    async def send_to(self, target: discord.abc.Messageable) -> str | None:
        await target.send(view=self)
        return await self.wait_result()

    @property
    def result(self) -> str | None:
        return self._result


def choice_view(
    choices: dict[str, str],
    prompt: str = "Choose an option.",
    *,
    timeout: float | None = 60.0,
    ephemeral: bool = True,
    owner_id: int | None = None,
) -> ChoiceView:
    return ChoiceView(choices, prompt=prompt, timeout=timeout, ephemeral=ephemeral, owner_id=owner_id)


def choice(
    choices: dict[str, str],
    prompt: str = "Choose an option.",
    *,
    owner_id: int | None = None,
    ephemeral: bool = True,
) -> ChoiceView:
    return ChoiceView(choices, prompt=prompt, owner_id=owner_id, ephemeral=ephemeral)


class JumpSelectPaginator(Paginator):
    def __init__(
        self,
        pages: list[Any],
        *,
        renderer: PageRenderer,
        timeout: float | None = 180.0,
        loop: bool = False,
        ephemeral: bool = False,
        owner_id: int | None = None,
    ) -> None:
        self._owner_id = owner_id
        super().__init__(pages, renderer=renderer, timeout=timeout, loop=loop, ephemeral=ephemeral)

    def _build(self) -> None:
        self.clear_items()
        inner = self._renderer(self._index, len(self._pages), self._pages[self._index])
        if isinstance(inner, ContainerBuilder):
            self.add_item(inner.build())
        elif isinstance(inner, (Vex, discord.ui.LayoutView)):
            for child in inner.children:
                self.add_item(child)
        else:
            self.add_item(inner)

        at_start = self._index == 0
        at_end = self._index == len(self._pages) - 1

        first_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u00ab",
            custom_id="vex_jp_first",
            disabled=at_start and not self._loop,
        )
        prev_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u2039",
            custom_id="vex_jp_prev",
            disabled=at_start and not self._loop,
        )
        next_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u203a",
            custom_id="vex_jp_next",
            disabled=at_end and not self._loop,
        )
        last_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u00bb",
            custom_id="vex_jp_last",
            disabled=at_end and not self._loop,
        )
        first_btn.callback = self._handle_first
        prev_btn.callback = self._handle_prev
        next_btn.callback = self._handle_next
        last_btn.callback = self._handle_last
        self.add_item(discord.ui.ActionRow(first_btn, prev_btn, next_btn, last_btn))

        cap = min(len(self._pages), 25)
        options = [
            discord.SelectOption(
                label=f"Page {i + 1}",
                value=str(i),
                default=(i == self._index),
            )
            for i in range(cap)
        ]
        jump_sel = discord.ui.Select(
            placeholder=f"Jump to page ({self._index + 1}/{len(self._pages)})",
            options=options,
            custom_id="vex_jp_jump",
        )
        jump_sel.callback = self._handle_jump
        self.add_item(discord.ui.ActionRow(jump_sel))

    async def _handle_jump(self, interaction: discord.Interaction) -> None:
        self._index = int(interaction.data["values"][0])
        await self._sync(interaction)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False


class PageGroup:
    def __init__(self, name: str, pages: list[Any], *, renderer: PageRenderer) -> None:
        self.name = name
        self.pages = pages
        self.renderer = renderer


class GroupedPaginator(discord.ui.LayoutView):
    def __init__(
        self,
        groups: list[PageGroup],
        *,
        timeout: float | None = 180.0,
        ephemeral: bool = False,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._groups = groups
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._group_index = 0
        self._page_index = 0
        self._message: discord.Message | None = None
        self._build()

    @property
    def current_group(self) -> PageGroup:
        return self._groups[self._group_index]

    @property
    def current_page(self) -> Any:
        return self.current_group.pages[self._page_index]

    def _build(self) -> None:
        self.clear_items()
        group = self.current_group
        inner = group.renderer(self._page_index, len(group.pages), self.current_page)
        if isinstance(inner, ContainerBuilder):
            self.add_item(inner.build())
        elif isinstance(inner, (Vex, discord.ui.LayoutView)):
            for child in inner.children:
                self.add_item(child)
        else:
            self.add_item(inner)

        if len(self._groups) > 1:
            tab_options = [
                discord.SelectOption(
                    label=g.name,
                    value=str(i),
                    default=(i == self._group_index),
                )
                for i, g in enumerate(self._groups[:25])
            ]
            tab_sel = discord.ui.Select(
                placeholder="Switch tab",
                options=tab_options,
                custom_id="vex_gp_tab",
            )
            tab_sel.callback = self._handle_tab
            self.add_item(discord.ui.ActionRow(tab_sel))

        at_start = self._page_index == 0
        at_end = self._page_index == len(group.pages) - 1
        prev_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u2039",
            custom_id="vex_gp_prev",
            disabled=at_start,
        )
        next_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u203a",
            custom_id="vex_gp_next",
            disabled=at_end,
        )
        prev_btn.callback = self._handle_prev
        next_btn.callback = self._handle_next
        self.add_item(discord.ui.ActionRow(prev_btn, next_btn))

    async def _sync(self, interaction: discord.Interaction) -> None:
        self._build()
        if interaction.response.is_done():
            await interaction.edit_original_response(view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def _handle_tab(self, interaction: discord.Interaction) -> None:
        self._group_index = int(interaction.data["values"][0])
        self._page_index = 0
        await self._sync(interaction)

    async def _handle_prev(self, interaction: discord.Interaction) -> None:
        if self._page_index > 0:
            self._page_index -= 1
        await self._sync(interaction)

    async def _handle_next(self, interaction: discord.Interaction) -> None:
        if self._page_index < len(self.current_group.pages) - 1:
            self._page_index += 1
        await self._sync(interaction)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def send_to(self, target: discord.abc.Messageable) -> discord.Message:
        self._message = await target.send(view=self)
        return self._message

    async def reply_to(self, interaction: discord.Interaction, *, ephemeral: bool | None = None) -> None:
        use_ephemeral = ephemeral if ephemeral is not None else self._ephemeral
        kwargs: dict[str, Any] = {"view": self, "ephemeral": use_ephemeral}
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)

    async def respond(self, interaction: discord.Interaction, *, ephemeral: bool | None = None) -> None:
        await self.reply_to(interaction, ephemeral=ephemeral)


def grouped_paginator(
    groups: list[PageGroup],
    *,
    timeout: float | None = 180.0,
    ephemeral: bool = False,
    owner_id: int | None = None,
) -> GroupedPaginator:
    return GroupedPaginator(groups, timeout=timeout, ephemeral=ephemeral, owner_id=owner_id)


class InfinitePaginator(discord.ui.LayoutView):
    def __init__(
        self,
        fetch: Callable[[int], Awaitable[list[Any]]],
        *,
        renderer: PageRenderer,
        page_size: int = 10,
        timeout: float | None = 180.0,
        ephemeral: bool = False,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._fetch = fetch
        self._renderer = renderer
        self._page_size = page_size
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._index = 0
        self._cache: dict[int, list[Any]] = {}
        self._exhausted = False
        self._message: discord.Message | None = None

    async def _load_page(self, index: int) -> list[Any] | None:
        if index in self._cache:
            return self._cache[index]
        if self._exhausted:
            return None
        offset = index * self._page_size
        items = await self._fetch(offset)
        if not items:
            self._exhausted = True
            return None
        self._cache[index] = items
        return items

    async def _build(self) -> bool:
        page_items = await self._load_page(self._index)
        if page_items is None:
            return False
        self.clear_items()
        inner = self._renderer(self._index, -1, page_items)
        if isinstance(inner, ContainerBuilder):
            self.add_item(inner.build())
        elif isinstance(inner, (Vex, discord.ui.LayoutView)):
            for child in inner.children:
                self.add_item(child)
        else:
            self.add_item(inner)

        next_exists = (self._index + 1) in self._cache or not self._exhausted
        prev_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u2039",
            custom_id="vex_inf_prev",
            disabled=self._index == 0,
        )
        next_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u203a",
            custom_id="vex_inf_next",
            disabled=not next_exists,
        )
        prev_btn.callback = self._handle_prev
        next_btn.callback = self._handle_next
        self.add_item(discord.ui.ActionRow(prev_btn, next_btn))
        return True

    async def _sync(self, interaction: discord.Interaction) -> None:
        await self._build()
        if interaction.response.is_done():
            await interaction.edit_original_response(view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def _handle_prev(self, interaction: discord.Interaction) -> None:
        if self._index > 0:
            self._index -= 1
        await self._sync(interaction)

    async def _handle_next(self, interaction: discord.Interaction) -> None:
        next_page = await self._load_page(self._index + 1)
        if next_page is not None:
            self._index += 1
        await self._sync(interaction)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def send_to(self, target: discord.abc.Messageable) -> discord.Message:
        await self._build()
        self._message = await target.send(view=self)
        return self._message

    async def reply_to(self, interaction: discord.Interaction) -> None:
        await self._build()
        kwargs: dict[str, Any] = {"view": self, "ephemeral": self._ephemeral}
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)

    async def respond(self, interaction: discord.Interaction) -> None:
        await self.reply_to(interaction)


class ScrollPaginator(discord.ui.LayoutView):
    def __init__(
        self,
        pages: list[Any],
        *,
        renderer: PageRenderer,
        timeout: float | None = 180.0,
        loop: bool = False,
        ephemeral: bool = False,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._pages = pages
        self._renderer = renderer
        self._index = 0
        self._loop = loop
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._message: discord.Message | None = None
        self._build()

    def _build(self) -> None:
        self.clear_items()
        inner = self._renderer(self._index, len(self._pages), self._pages[self._index])
        if isinstance(inner, ContainerBuilder):
            self.add_item(inner.build())
        elif isinstance(inner, (Vex, discord.ui.LayoutView)):
            for child in inner.children:
                self.add_item(child)
        else:
            self.add_item(inner)

        at_start = self._index == 0
        at_end = self._index == len(self._pages) - 1
        self.add_item(discord.ui.TextDisplay(f"Page {self._index + 1} of {len(self._pages)}"))

        prev_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="\u2039 Previous",
            custom_id="vex_scroll_prev",
            disabled=at_start and not self._loop,
        )
        next_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Next \u203a",
            custom_id="vex_scroll_next",
            disabled=at_end and not self._loop,
        )
        prev_btn.callback = self._handle_prev
        next_btn.callback = self._handle_next
        self.add_item(discord.ui.ActionRow(prev_btn, next_btn))

    async def _sync(self, interaction: discord.Interaction) -> None:
        self._build()
        if interaction.response.is_done():
            await interaction.edit_original_response(view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def _handle_prev(self, interaction: discord.Interaction) -> None:
        if self._index == 0 and self._loop:
            self._index = len(self._pages) - 1
        elif self._index > 0:
            self._index -= 1
        await self._sync(interaction)

    async def _handle_next(self, interaction: discord.Interaction) -> None:
        if self._index == len(self._pages) - 1 and self._loop:
            self._index = 0
        elif self._index < len(self._pages) - 1:
            self._index += 1
        await self._sync(interaction)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def send_to(self, target: discord.abc.Messageable) -> discord.Message:
        self._message = await target.send(view=self)
        return self._message

    async def reply_to(self, interaction: discord.Interaction) -> None:
        kwargs: dict[str, Any] = {"view": self, "ephemeral": self._ephemeral}
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)

    async def respond(self, interaction: discord.Interaction) -> None:
        await self.reply_to(interaction)

    def jump(self, index: int) -> Self:
        self._index = max(0, min(index, len(self._pages) - 1))
        self._build()
        return self


def scroll_paginator(
    pages: list[Any],
    *,
    renderer: PageRenderer,
    timeout: float | None = 180.0,
    loop: bool = False,
    ephemeral: bool = False,
    owner_id: int | None = None,
) -> ScrollPaginator:
    return ScrollPaginator(
        pages,
        renderer=renderer,
        timeout=timeout,
        loop=loop,
        ephemeral=ephemeral,
        owner_id=owner_id,
    )


class PromptInput:
    def __init__(
        self,
        bot: commands.Bot,
        *,
        prompt: str | None = None,
        timeout: float = 60.0,
        delete_prompt: bool = False,
        delete_response: bool = False,
        check: Callable[[discord.Message], bool] | None = None,
    ) -> None:
        self._bot = bot
        self._prompt = prompt
        self._timeout = timeout
        self._delete_prompt = delete_prompt
        self._delete_response = delete_response
        self._check = check

    async def ask(
        self,
        channel: discord.abc.Messageable,
        *,
        user: discord.User | discord.Member | None = None,
    ) -> discord.Message | None:
        prompt_msg: discord.Message | None = None
        if self._prompt:
            prompt_msg = await channel.send(self._prompt)

        def default_check(m: discord.Message) -> bool:
            if not hasattr(channel, "id"):
                return True
            if m.channel.id != channel.id:
                return False
            if user is not None and m.author.id != user.id:
                return False
            return True

        check = self._check or default_check
        try:
            response: discord.Message = await self._bot.wait_for(
                "message",
                check=check,
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            if prompt_msg and self._delete_prompt:
                try:
                    await prompt_msg.delete()
                except discord.HTTPException:
                    pass
            return None

        if prompt_msg and self._delete_prompt:
            try:
                await prompt_msg.delete()
            except discord.HTTPException:
                pass
        if self._delete_response:
            try:
                await response.delete()
            except discord.HTTPException:
                pass

        return response

    async def wait(
        self,
        channel: discord.abc.Messageable,
        *,
        user: discord.User | discord.Member | None = None,
    ) -> discord.Message | None:
        return await self.ask(channel, user=user)

    async def collect(
        self,
        channel: discord.abc.Messageable,
        *,
        user: discord.User | discord.Member | None = None,
    ) -> str | None:
        msg = await self.ask(channel, user=user)
        return msg.content if msg else None


def prompt_input(
    bot: commands.Bot,
    prompt: str | None = None,
    *,
    timeout: float = 60.0,
    delete_prompt: bool = False,
    delete_response: bool = False,
    check: Callable[[discord.Message], bool] | None = None,
) -> PromptInput:
    return PromptInput(
        bot,
        prompt=prompt,
        timeout=timeout,
        delete_prompt=delete_prompt,
        delete_response=delete_response,
        check=check,
    )


def wait_input(
    bot: commands.Bot,
    prompt: str | None = None,
    *,
    timeout: float = 60.0,
) -> PromptInput:
    return PromptInput(bot, prompt=prompt, timeout=timeout)


async def edit_to_v2(
    message: discord.Message,
    view: discord.ui.LayoutView,
) -> discord.Message:
    return await message.edit(content=None, embeds=[], view=view)


async def disable_all(view: discord.ui.LayoutView) -> None:
    for item in view.walk_children():
        if hasattr(item, "disabled"):
            item.disabled = True


async def freeze_view(
    view: discord.ui.LayoutView,
    interaction: discord.Interaction,
) -> None:
    await disable_all(view)
    if interaction.response.is_done():
        await interaction.edit_original_response(view=view)
    else:
        await interaction.response.edit_message(view=view)


class AutoDeleteView(Vex):
    def __init__(self, *, timeout: float | None = 30.0) -> None:
        super().__init__(timeout=timeout)
        self._message: discord.Message | None = None

    async def on_timeout(self) -> None:
        await super().on_timeout()
        if self._message is not None:
            try:
                await self._message.delete()
            except discord.HTTPException:
                pass

    async def send_to(
        self,
        target: discord.abc.Messageable,
        *,
        content: str | None = None,
        files: list[discord.File] | None = None,
        allowed_mentions: discord.AllowedMentions | None = None,
    ) -> discord.Message:
        msg = await super().send_to(target, content=content, files=files, allowed_mentions=allowed_mentions)
        self._message = msg
        return msg

    async def reply_to(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool = False,
        files: list[discord.File] | None = None,
        allowed_mentions: discord.AllowedMentions | None = None,
    ) -> None:
        await super().reply_to(interaction, ephemeral=ephemeral, files=files, allowed_mentions=allowed_mentions)
        try:
            self._message = await interaction.original_response()
        except discord.HTTPException:
            pass


def auto_delete(*, timeout: float | None = 30.0) -> AutoDeleteView:
    return AutoDeleteView(timeout=timeout)


def error_card(message: str, *, title: str = "Error") -> ContainerBuilder:
    return (
        container()
        .hex("#ed4245")
        .h3(title)
        .text(message)
    )


def success_card(message: str, *, title: str = "Success") -> ContainerBuilder:
    return (
        container()
        .hex("#57f287")
        .h3(title)
        .text(message)
    )


def info_card(message: str, *, title: str = "Info") -> ContainerBuilder:
    return (
        container()
        .hex("#5865f2")
        .h3(title)
        .text(message)
    )


class SelectMenu(discord.ui.LayoutView):
    def __init__(
        self,
        options: list[tuple[str, str]],
        *,
        prompt: str = "Select an option.",
        placeholder: str = "Choose...",
        min_values: int = 1,
        max_values: int = 1,
        timeout: float | None = 60.0,
        ephemeral: bool = True,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._result: list[str] | None = None
        self._future: asyncio.Future[list[str] | None] = asyncio.get_event_loop().create_future()

        self.add_item(discord.ui.TextDisplay(prompt))
        select_options = [
            discord.SelectOption(label=label, value=value)
            for label, value in options[:25]
        ]
        sel = discord.ui.Select(
            placeholder=placeholder,
            options=select_options,
            min_values=min_values,
            max_values=max_values,
            custom_id="vex_selectmenu_pick",
        )
        sel.callback = self._handle_select
        self.add_item(discord.ui.ActionRow(sel))

    async def _handle_select(self, interaction: discord.Interaction) -> None:
        self._result = interaction.data.get("values", [])
        self.stop()
        if not self._future.done():
            self._future.set_result(self._result)
        await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if not self._future.done():
            self._future.set_result(None)

    async def wait_result(self) -> list[str] | None:
        return await self._future

    async def reply_to(self, interaction: discord.Interaction) -> list[str] | None:
        kwargs: dict[str, Any] = {"view": self, "ephemeral": self._ephemeral}
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> list[str] | None:
        return await self.reply_to(interaction)

    async def send_to(self, target: discord.abc.Messageable) -> list[str] | None:
        await target.send(view=self)
        return await self.wait_result()

    @property
    def result(self) -> list[str] | None:
        return self._result


def select_menu(
    options: list[tuple[str, str]],
    prompt: str = "Select an option.",
    *,
    placeholder: str = "Choose...",
    min_values: int = 1,
    max_values: int = 1,
    timeout: float | None = 60.0,
    ephemeral: bool = True,
    owner_id: int | None = None,
) -> SelectMenu:
    return SelectMenu(
        options,
        prompt=prompt,
        placeholder=placeholder,
        min_values=min_values,
        max_values=max_values,
        timeout=timeout,
        ephemeral=ephemeral,
        owner_id=owner_id,
    )


def pick(
    options: list[tuple[str, str]],
    prompt: str = "Select an option.",
    *,
    owner_id: int | None = None,
    ephemeral: bool = True,
) -> SelectMenu:
    return SelectMenu(options, prompt=prompt, owner_id=owner_id, ephemeral=ephemeral)


class RolePickerView(discord.ui.LayoutView):
    def __init__(
        self,
        *,
        prompt: str = "Select a role.",
        placeholder: str = "Choose a role...",
        min_values: int = 1,
        max_values: int = 1,
        timeout: float | None = 60.0,
        ephemeral: bool = True,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._result: list[discord.Role] | None = None
        self._future: asyncio.Future[list[discord.Role] | None] = asyncio.get_event_loop().create_future()

        self.add_item(discord.ui.TextDisplay(prompt))
        sel = discord.ui.RoleSelect(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            custom_id="vex_rolepicker",
        )
        sel.callback = self._handle_select
        self.add_item(discord.ui.ActionRow(sel))

    async def _handle_select(self, interaction: discord.Interaction) -> None:
        self._result = interaction.data.get("resolved", {}).get("roles", {})
        resolved = interaction.data.get("resolved", {})
        role_ids: list[str] = interaction.data.get("values", [])
        roles: list[discord.Role] = []
        if interaction.guild:
            for rid in role_ids:
                role = interaction.guild.get_role(int(rid))
                if role:
                    roles.append(role)
        self._result = roles
        self.stop()
        if not self._future.done():
            self._future.set_result(roles if roles else None)
        await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if not self._future.done():
            self._future.set_result(None)

    async def wait_result(self) -> list[discord.Role] | None:
        return await self._future

    async def reply_to(self, interaction: discord.Interaction) -> list[discord.Role] | None:
        kwargs: dict[str, Any] = {"view": self, "ephemeral": self._ephemeral}
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> list[discord.Role] | None:
        return await self.reply_to(interaction)

    @property
    def result(self) -> list[discord.Role] | None:
        return self._result


def role_picker(
    prompt: str = "Select a role.",
    *,
    placeholder: str = "Choose a role...",
    min_values: int = 1,
    max_values: int = 1,
    timeout: float | None = 60.0,
    ephemeral: bool = True,
    owner_id: int | None = None,
) -> RolePickerView:
    return RolePickerView(
        prompt=prompt,
        placeholder=placeholder,
        min_values=min_values,
        max_values=max_values,
        timeout=timeout,
        ephemeral=ephemeral,
        owner_id=owner_id,
    )


class ChannelPickerView(discord.ui.LayoutView):
    def __init__(
        self,
        *,
        prompt: str = "Select a channel.",
        placeholder: str = "Choose a channel...",
        channel_types: list[discord.ChannelType] | None = None,
        min_values: int = 1,
        max_values: int = 1,
        timeout: float | None = 60.0,
        ephemeral: bool = True,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._result: list[Any] | None = None
        self._future: asyncio.Future[list[Any] | None] = asyncio.get_event_loop().create_future()

        self.add_item(discord.ui.TextDisplay(prompt))
        sel_kwargs: dict[str, Any] = {
            "placeholder": placeholder,
            "min_values": min_values,
            "max_values": max_values,
            "custom_id": "vex_channelpicker",
        }
        if channel_types:
            sel_kwargs["channel_types"] = channel_types
        sel = discord.ui.ChannelSelect(**sel_kwargs)
        sel.callback = self._handle_select
        self.add_item(discord.ui.ActionRow(sel))

    async def _handle_select(self, interaction: discord.Interaction) -> None:
        channel_ids: list[str] = interaction.data.get("values", [])
        channels: list[Any] = []
        if interaction.guild:
            for cid in channel_ids:
                ch = interaction.guild.get_channel(int(cid))
                if ch:
                    channels.append(ch)
        self._result = channels
        self.stop()
        if not self._future.done():
            self._future.set_result(channels if channels else None)
        await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if not self._future.done():
            self._future.set_result(None)

    async def wait_result(self) -> list[Any] | None:
        return await self._future

    async def reply_to(self, interaction: discord.Interaction) -> list[Any] | None:
        kwargs: dict[str, Any] = {"view": self, "ephemeral": self._ephemeral}
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> list[Any] | None:
        return await self.reply_to(interaction)

    @property
    def result(self) -> list[Any] | None:
        return self._result


def channel_picker_view(
    prompt: str = "Select a channel.",
    *,
    placeholder: str = "Choose a channel...",
    channel_types: list[discord.ChannelType] | None = None,
    min_values: int = 1,
    max_values: int = 1,
    timeout: float | None = 60.0,
    ephemeral: bool = True,
    owner_id: int | None = None,
) -> ChannelPickerView:
    return ChannelPickerView(
        prompt=prompt,
        placeholder=placeholder,
        channel_types=channel_types,
        min_values=min_values,
        max_values=max_values,
        timeout=timeout,
        ephemeral=ephemeral,
        owner_id=owner_id,
    )


class UserPickerView(discord.ui.LayoutView):
    def __init__(
        self,
        *,
        prompt: str = "Select a user.",
        placeholder: str = "Choose a user...",
        min_values: int = 1,
        max_values: int = 1,
        timeout: float | None = 60.0,
        ephemeral: bool = True,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._result: list[discord.Member | discord.User] | None = None
        self._future: asyncio.Future[list[discord.Member | discord.User] | None] = asyncio.get_event_loop().create_future()

        self.add_item(discord.ui.TextDisplay(prompt))
        sel = discord.ui.UserSelect(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            custom_id="vex_userpicker",
        )
        sel.callback = self._handle_select
        self.add_item(discord.ui.ActionRow(sel))

    async def _handle_select(self, interaction: discord.Interaction) -> None:
        user_ids: list[str] = interaction.data.get("values", [])
        users: list[discord.Member | discord.User] = []
        for uid in user_ids:
            if interaction.guild:
                member = interaction.guild.get_member(int(uid))
                if member:
                    users.append(member)
                    continue
            user = interaction.client.get_user(int(uid))
            if user:
                users.append(user)
        self._result = users
        self.stop()
        if not self._future.done():
            self._future.set_result(users if users else None)
        await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None:
            return True
        if interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if not self._future.done():
            self._future.set_result(None)

    async def wait_result(self) -> list[discord.Member | discord.User] | None:
        return await self._future

    async def reply_to(self, interaction: discord.Interaction) -> list[discord.Member | discord.User] | None:
        kwargs: dict[str, Any] = {"view": self, "ephemeral": self._ephemeral}
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> list[discord.Member | discord.User] | None:
        return await self.reply_to(interaction)

    @property
    def result(self) -> list[discord.Member | discord.User] | None:
        return self._result


def user_picker_view(
    prompt: str = "Select a user.",
    *,
    placeholder: str = "Choose a user...",
    min_values: int = 1,
    max_values: int = 1,
    timeout: float | None = 60.0,
    ephemeral: bool = True,
    owner_id: int | None = None,
) -> UserPickerView:
    return UserPickerView(
        prompt=prompt,
        placeholder=placeholder,
        min_values=min_values,
        max_values=max_values,
        timeout=timeout,
        ephemeral=ephemeral,
        owner_id=owner_id,
    )


class CooldownStore:
    def __init__(self, *, rate: int, per: float, bucket: commands.BucketType = commands.BucketType.user) -> None:
        self._mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)

    def check(self, message: discord.Message) -> float:
        bucket = self._mapping.get_bucket(message)
        if bucket is None:
            return 0.0
        retry = bucket.update_rate_limit()
        return retry if retry else 0.0

    def is_limited(self, message: discord.Message) -> bool:
        return self.check(message) > 0.0

    def reset(self, message: discord.Message) -> None:
        bucket = self._mapping.get_bucket(message)
        if bucket:
            bucket.reset()

    def retry_after(self, message: discord.Message) -> float:
        bucket = self._mapping.get_bucket(message)
        if bucket is None:
            return 0.0
        retry = bucket.update_rate_limit()
        return retry if retry else 0.0

    def remaining(self, message: discord.Message) -> int:
        bucket = self._mapping.get_bucket(message)
        if bucket is None:
            return 0
        return max(0, bucket.rate - bucket._tokens)  # type: ignore[attr-defined]


def cooldown_store(
    *,
    rate: int,
    per: float,
    bucket: commands.BucketType = commands.BucketType.user,
) -> CooldownStore:
    return CooldownStore(rate=rate, per=per, bucket=bucket)


class GlobalCooldown:
    def __init__(self, *, rate: int, per: float) -> None:
        self._rate = rate
        self._per = per
        self._stores: dict[str, CooldownStore] = {}

    def store(self, name: str) -> CooldownStore:
        if name not in self._stores:
            self._stores[name] = CooldownStore(
                rate=self._rate,
                per=self._per,
                bucket=commands.BucketType.user,
            )
        return self._stores[name]

    def check(self, name: str, message: discord.Message) -> float:
        return self.store(name).check(message)

    def is_limited(self, name: str, message: discord.Message) -> bool:
        return self.store(name).is_limited(message)

    def reset(self, name: str, message: discord.Message) -> None:
        self.store(name).reset(message)

    def reset_all(self, message: discord.Message) -> None:
        for store in self._stores.values():
            store.reset(message)


def global_cooldown(*, rate: int, per: float) -> GlobalCooldown:
    return GlobalCooldown(rate=rate, per=per)


class CooldownCard:
    @staticmethod
    def build(retry_after: float, *, title: str = "Slow down") -> ContainerBuilder:
        seconds = round(retry_after, 1)
        if seconds < 60:
            time_str = f"{seconds}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            time_str = f"{minutes}m {secs}s" if secs else f"{minutes}m"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            time_str = f"{hours}h {minutes}m" if minutes else f"{hours}h"
        return (
            container()
            .hex("#fee75c")
            .h3(title)
            .text(f"Please wait {time_str} before trying again.")
        )

    @staticmethod
    def from_store(store: CooldownStore, message: discord.Message) -> ContainerBuilder | None:
        retry = store.retry_after(message)
        if retry <= 0:
            return None
        return CooldownCard.build(retry)


def cooldown_card(retry_after: float, *, title: str = "Slow down") -> ContainerBuilder:
    return CooldownCard.build(retry_after, title=title)


def cmd_alias(alias: str) -> Callable[[Any], Any]:
    def decorator(func: Any) -> Any:
        if not hasattr(func, "__vex_help__"):
            func.__vex_help__ = CommandInfo(getattr(func, "__name__", "unknown"), func)
        if alias not in func.__vex_help__.aliases:
            func.__vex_help__.aliases.append(alias)
        return func
    return decorator


def search_commands(
    registry_obj: HelpRegistry,
    query: str,
    *,
    limit: int = 5,
    include_hidden: bool = False,
) -> list[CommandInfo]:
    query_lower = query.lower()
    results: list[tuple[int, CommandInfo]] = []
    for info in registry_obj.list(include_hidden=include_hidden):
        score = 0
        if info.name.lower().startswith(query_lower):
            score = 3
        elif query_lower in info.name.lower():
            score = 2
        elif any(query_lower in a.lower() for a in info.aliases):
            score = 1
        elif query_lower in info.description.lower():
            score = 1
        if score > 0:
            results.append((score, info))
    results.sort(key=lambda x: x[0], reverse=True)
    return [info for _, info in results[:limit]]


def registry_to_select(
    registry_obj: HelpRegistry,
    *,
    placeholder: str = "Browse commands...",
    category: str | None = None,
    include_hidden: bool = False,
) -> SelectBuilder:
    cmds = registry_obj.list(category=category, include_hidden=include_hidden)
    sb = SelectBuilder()
    sb.placeholder(placeholder)
    for info in cmds[:25]:
        desc = info.description[:50] if info.description else None
        sb.add(info.name, info.name, description=desc)
    return sb


def registry_category_select(
    registry_obj: HelpRegistry,
    *,
    placeholder: str = "Browse categories...",
) -> SelectBuilder:
    all_cmds = registry_obj.list(include_hidden=False)
    seen: set[str] = set()
    categories: list[str] = []
    for info in all_cmds:
        if info.category not in seen:
            seen.add(info.category)
            categories.append(info.category)
    sb = SelectBuilder()
    sb.placeholder(placeholder)
    for cat in categories[:25]:
        count = sum(1 for c in all_cmds if c.category == cat)
        sb.add(cat, cat, description=f"{count} command{'s' if count != 1 else ''}")
    return sb


def registry_categories(registry_obj: HelpRegistry) -> list[str]:
    all_cmds = registry_obj.list(include_hidden=False)
    seen: set[str] = set()
    categories: list[str] = []
    for info in all_cmds:
        if info.category not in seen:
            seen.add(info.category)
            categories.append(info.category)
    return categories


async def safe_defer(
    interaction: discord.Interaction,
    *,
    ephemeral: bool = False,
    thinking: bool = False,
) -> None:
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=ephemeral, thinking=thinking)


async def safe_edit(
    interaction: discord.Interaction,
    view: discord.ui.LayoutView | None = None,
    *,
    allowed_mentions: discord.AllowedMentions | None = None,
) -> None:
    kwargs: dict[str, Any] = {}
    if view is not None:
        kwargs["view"] = view
    if allowed_mentions is not None:
        kwargs["allowed_mentions"] = allowed_mentions
    if not kwargs:
        return
    try:
        if interaction.response.is_done():
            await interaction.edit_original_response(**kwargs)
        else:
            await interaction.response.edit_message(**kwargs)
    except discord.HTTPException:
        pass


async def safe_delete(interaction: discord.Interaction) -> None:
    try:
        if not interaction.response.is_done():
            await interaction.response.defer()
        await interaction.delete_original_response()
    except discord.HTTPException:
        pass


class AuditCard:
    @staticmethod
    def build(
        *,
        action: str,
        actor: discord.User | discord.Member,
        target: discord.User | discord.Member | discord.Role | str | None = None,
        reason: str | None = None,
        fields: dict[str, str] | None = None,
        color: discord.Color | int | str | None = None,
    ) -> ContainerBuilder:
        cb = container()
        if color is not None:
            if isinstance(color, str):
                cb.hex(color)
            elif isinstance(color, int):
                cb.accent(color)
            else:
                cb.accent(color)
        cb.h3(action)
        cb.field("Actor", f"<@{actor.id}>")
        if target is not None:
            if isinstance(target, str):
                cb.field("Target", target)
            elif isinstance(target, discord.Role):
                cb.field("Target", f"<@&{target.id}>")
            else:
                cb.field("Target", f"<@{target.id}>")
        if reason:
            cb.field("Reason", reason)
        if fields:
            cb.fields(fields)
        return cb


def audit_card(
    *,
    action: str,
    actor: discord.User | discord.Member,
    target: discord.User | discord.Member | discord.Role | str | None = None,
    reason: str | None = None,
    fields: dict[str, str] | None = None,
    color: discord.Color | int | str | None = None,
) -> ContainerBuilder:
    return AuditCard.build(
        action=action,
        actor=actor,
        target=target,
        reason=reason,
        fields=fields,
        color=color,
    )


class DiffCard:
    @staticmethod
    def build(
        *,
        title: str = "Changes",
        before: dict[str, str],
        after: dict[str, str],
        color: discord.Color | int | str | None = None,
    ) -> ContainerBuilder:
        cb = container()
        if color is not None:
            if isinstance(color, str):
                cb.hex(color)
            elif isinstance(color, int):
                cb.accent(color)
            else:
                cb.accent(color)
        cb.h3(title)
        all_keys = list(dict.fromkeys(list(before.keys()) + list(after.keys())))
        for key in all_keys:
            old_val = before.get(key, "not set")
            new_val = after.get(key, "not set")
            if old_val == new_val:
                cb.field(key, new_val)
            else:
                cb.text(f"**{key}:** {old_val} -> {new_val}")
        return cb


def diff_card(
    *,
    title: str = "Changes",
    before: dict[str, str],
    after: dict[str, str],
    color: discord.Color | int | str | None = None,
) -> ContainerBuilder:
    return DiffCard.build(title=title, before=before, after=after, color=color)