from __future__ import annotations
import asyncio
import io
import os
import sys
import inspect
import logging
import datetime
import importlib
import traceback
import pkgutil
import discord
from discord import app_commands
from discord.ext import commands
from typing import Self, Callable, Awaitable, Any


def _new_future() -> "asyncio.Future[Any]":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.create_future()


async def _busy_reply(interaction: discord.Interaction, message: str) -> None:
    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except discord.HTTPException:
        pass


def _walk_components(view: discord.ui.LayoutView) -> list[Any]:
    collected: list[Any] = []

    def descend(items: Any) -> None:
        for item in items:
            collected.append(item)
            children = getattr(item, "children", None)
            if children:
                descend(list(children))

    descend(list(view.children))
    return collected


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
        self._once: bool = False
        self._debounce: float = 0.0
        self._busy_message: str = "Please wait a moment before trying that again."

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

    def once(self, state: bool = True) -> Self:
        self._once = state
        return self

    def fire_once(self) -> Self:
        self._once = True
        return self

    def single_use(self) -> Self:
        self._once = True
        return self

    def debounce(self, seconds: float) -> Self:
        self._debounce = max(0.0, float(seconds))
        return self

    def throttle(self, seconds: float) -> Self:
        return self.debounce(seconds)

    def cooldown(self, seconds: float) -> Self:
        return self.debounce(seconds)

    def busy(self, message: str) -> Self:
        self._busy_message = message
        return self

    def _guard(self, cb: Any) -> Any:
        if not self._once and self._debounce <= 0:
            return cb
        once = self._once
        window = self._debounce
        message = self._busy_message
        state: dict[str, Any] = {"used": False, "last": 0.0, "running": False}

        async def guarded(interaction: discord.Interaction) -> None:
            now = asyncio.get_running_loop().time()
            blocked = (
                state["running"]
                or (once and state["used"])
                or (window > 0 and (now - state["last"]) < window)
            )
            if blocked:
                await _busy_reply(interaction, message)
                return
            state["last"] = now
            state["used"] = True
            state["running"] = True
            try:
                await discord.utils.maybe_coroutine(cb, interaction)
            finally:
                state["running"] = False

        return guarded

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
            btn.callback = self._guard(self._callback)
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
        self._options.append(builder)
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
            "options": [
                o.build() if isinstance(o, SelectOptionBuilder) else o
                for o in self._options
                if o is not None
            ],
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
        if isinstance(media, str) and hasattr(discord, "UnfurledMediaItem"):
            media = discord.UnfurledMediaItem(url=media)
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


class MediaCollector:
    MAX_PER_GALLERY = 10
    SPOILER_PREFIX = "SPOILER_"
    GIF_EMBED_TYPES = ("gifv", "video")
    IMAGE_EMBED_TYPES = ("image",)

    def __init__(self) -> None:
        self._items: list[discord.MediaGalleryItem] = []
        self._files: list[discord.File] = []
        self._seen: set[str] = set()

    def _coerce(self, url: str) -> Any:
        if hasattr(discord, "UnfurledMediaItem"):
            return discord.UnfurledMediaItem(url=url)
        return url

    def _unique(self, name: str) -> str:
        base = name or "file"
        if base not in self._seen:
            self._seen.add(base)
            return base
        stem, dot, ext = base.rpartition(".")
        counter = 1
        while True:
            candidate = f"{stem}_{counter}.{ext}" if dot else f"{base}_{counter}"
            if candidate not in self._seen:
                self._seen.add(candidate)
                return candidate
            counter += 1

    @staticmethod
    def _rename(file: discord.File, new_name: str) -> None:
        try:
            file.filename = new_name
        except (AttributeError, TypeError):
            try:
                file._filename = new_name
            except (AttributeError, TypeError):
                pass

    def url(self, url: str, *, description: str = "", spoiler: bool = False) -> Self:
        if not url:
            return self
        kwargs: dict[str, Any] = {}
        if description:
            kwargs["description"] = description
        if spoiler:
            kwargs["spoiler"] = spoiler
        self._items.append(discord.MediaGalleryItem(self._coerce(url), **kwargs))
        return self

    def file(self, file: discord.File, *, description: str = "", spoiler: bool = False) -> Self:
        raw = file.filename or "file"
        flagged = spoiler or raw.startswith(self.SPOILER_PREFIX)
        clean = raw[len(self.SPOILER_PREFIX):] if raw.startswith(self.SPOILER_PREFIX) else raw
        name = self._unique(clean)
        self._rename(file, name)
        self._files.append(file)
        kwargs: dict[str, Any] = {}
        if description:
            kwargs["description"] = description
        if flagged:
            kwargs["spoiler"] = True
        self._items.append(discord.MediaGalleryItem(self._coerce(f"attachment://{name}"), **kwargs))
        return self

    async def attachment(self, attachment: discord.Attachment, *, use_cached: bool = True) -> bool:
        raw = attachment.filename or "file"
        flagged = raw.startswith(self.SPOILER_PREFIX)
        clean = raw[len(self.SPOILER_PREFIX):] if flagged else raw
        name = self._unique(clean)
        fetched: discord.File | None = None
        for cached in (use_cached, not use_cached):
            try:
                fetched = await attachment.to_file(filename=name, use_cached=cached)
                break
            except (discord.HTTPException, discord.NotFound, discord.Forbidden):
                continue
        if fetched is None:
            self._seen.discard(name)
            return False
        self._files.append(fetched)
        kwargs: dict[str, Any] = {}
        if flagged:
            kwargs["spoiler"] = True
        self._items.append(discord.MediaGalleryItem(self._coerce(f"attachment://{name}"), **kwargs))
        return True

    @classmethod
    def _embed_media(cls, embed: discord.Embed) -> str | None:
        etype = getattr(embed, "type", None)
        if etype in cls.GIF_EMBED_TYPES:
            video = getattr(embed, "video", None)
            if video is not None and getattr(video, "url", None):
                return video.url
            thumb = getattr(embed, "thumbnail", None)
            if thumb is not None and getattr(thumb, "url", None):
                return thumb.url
        if etype in cls.IMAGE_EMBED_TYPES:
            image = getattr(embed, "image", None)
            if image is not None and getattr(image, "url", None):
                return image.url
            thumb = getattr(embed, "thumbnail", None)
            if thumb is not None and getattr(thumb, "url", None):
                return thumb.url
        return None

    @staticmethod
    def _sticker_media(sticker: Any) -> str | None:
        fmt = getattr(sticker, "format", None)
        lottie = getattr(discord.StickerFormatType, "lottie", None)
        if fmt is not None and lottie is not None and fmt == lottie:
            return None
        return getattr(sticker, "url", None)

    async def from_message(
        self,
        message: discord.Message,
        *,
        download: bool = True,
        max_bytes: int | None = None,
    ) -> Self:
        for att in getattr(message, "attachments", []):
            within_limit = max_bytes is None or getattr(att, "size", 0) <= max_bytes
            if download and within_limit:
                if await self.attachment(att):
                    continue
            elif not download:
                self.url(att.url, spoiler=att.is_spoiler())
        for embed in getattr(message, "embeds", []):
            media = self._embed_media(embed)
            if media:
                self.url(media)
        for sticker in getattr(message, "stickers", []):
            media = self._sticker_media(sticker)
            if media:
                self.url(media)
        return self

    def galleries(self) -> list[discord.ui.MediaGallery]:
        out: list[discord.ui.MediaGallery] = []
        for start in range(0, len(self._items), self.MAX_PER_GALLERY):
            chunk = self._items[start:start + self.MAX_PER_GALLERY]
            out.append(discord.ui.MediaGallery(*chunk))
        return out

    def files(self) -> list[discord.File]:
        return self._files

    @property
    def has_media(self) -> bool:
        return bool(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)


class FileBuilder:
    def __init__(self, *, id: int | None = None) -> None:
        self._media: str | None = None
        self._spoiler: bool = False
        self._id = id
        self._file: discord.File | None = None

    def reference(self, name: str) -> Self:
        self._media = name if name.startswith("attachment://") else f"attachment://{name}"
        return self

    def named(self, name: str) -> Self:
        return self.reference(name)

    def attachment(self, name: str) -> Self:
        return self.reference(name)

    def url(self, url: str) -> Self:
        self._media = url
        return self

    def source(self, file: discord.File, *, name: str | None = None) -> Self:
        fname = name or file.filename or "file"
        if fname.startswith("SPOILER_"):
            fname = fname[len("SPOILER_"):]
        try:
            file.filename = fname
        except (AttributeError, TypeError):
            try:
                file._filename = fname
            except (AttributeError, TypeError):
                pass
        self._file = file
        self._media = f"attachment://{fname}"
        return self

    def upload(self, file: discord.File, *, name: str | None = None) -> Self:
        return self.source(file, name=name)

    def from_text(self, content: str | bytes, *, name: str = "file.txt") -> Self:
        return self.source(text_file(content, filename=name), name=name)

    def spoiler(self, state: bool = True) -> Self:
        self._spoiler = state
        return self

    def hidden(self, state: bool = True) -> Self:
        self._spoiler = state
        return self

    def id(self, value: int) -> Self:
        self._id = value
        return self

    @property
    def file(self) -> discord.File | None:
        return self._file

    def build(self) -> discord.ui.File:
        if self._media is None:
            raise VexValidationError("a file component needs a reference, url, or source before it can render")
        kwargs: dict[str, Any] = {"spoiler": self._spoiler}
        if self._id is not None:
            kwargs["id"] = self._id
        return discord.ui.File(self._media, **kwargs)


class TableBuilder:
    def __init__(self, *, title: str | None = None) -> None:
        self._title = title
        self._headers: list[str] = []
        self._rows: list[list[str]] = []
        self._aligns: list[str] = []
        self._lang: str = ""
        self._gap: str = "  "
        self._cap: int | None = None

    def title(self, text: str) -> Self:
        self._title = text
        return self

    def caption(self, text: str) -> Self:
        self._title = text
        return self

    def headers(self, *names: Any) -> Self:
        self._headers = [str(n) for n in names]
        return self

    def columns(self, *names: Any) -> Self:
        return self.headers(*names)

    def head(self, *names: Any) -> Self:
        return self.headers(*names)

    def align(self, *aligns: str) -> Self:
        self._aligns = [a[:1].lower() for a in aligns]
        return self

    def row(self, *values: Any) -> Self:
        self._rows.append([str(v) for v in values])
        return self

    def add(self, *values: Any) -> Self:
        return self.row(*values)

    def record(self, *values: Any) -> Self:
        return self.row(*values)

    def extend(self, items: list[Any]) -> Self:
        for item in items:
            self.row(*item)
        return self

    def lang(self, language: str) -> Self:
        self._lang = language
        return self

    def code(self, language: str) -> Self:
        self._lang = language
        return self

    def gap(self, spaces: int) -> Self:
        self._gap = " " * max(1, spaces)
        return self

    def max_cell(self, width: int) -> Self:
        self._cap = max(1, width)
        return self

    def _clip(self, value: str) -> str:
        if self._cap is None or len(value) <= self._cap:
            return value
        if self._cap <= 1:
            return value[: self._cap]
        return value[: self._cap - 1] + "\u2026"

    def _cell(self, value: str, width: int, align: str) -> str:
        if align == "r":
            return value.rjust(width)
        if align == "c":
            return value.center(width)
        return value.ljust(width)

    def render(self) -> str:
        grid: list[list[str]] = []
        if self._headers:
            grid.append([self._clip(h) for h in self._headers])
        for row in self._rows:
            grid.append([self._clip(c) for c in row])
        prefix = f"{self._title}\n" if self._title else ""
        if not grid:
            return f"{prefix}```{self._lang}\n```"
        ncols = max(len(row) for row in grid)
        grid = [row + [""] * (ncols - len(row)) for row in grid]
        widths = [max(len(grid[r][c]) for r in range(len(grid))) for c in range(ncols)]
        aligns = [self._aligns[c] if c < len(self._aligns) else "l" for c in range(ncols)]
        lines: list[str] = []
        start = 0
        if self._headers:
            header = grid[0]
            lines.append(self._gap.join(self._cell(header[c], widths[c], aligns[c]) for c in range(ncols)))
            lines.append(self._gap.join("-" * widths[c] for c in range(ncols)))
            start = 1
        for row in grid[start:]:
            lines.append(self._gap.join(self._cell(row[c], widths[c], aligns[c]) for c in range(ncols)))
        body = "\n".join(lines)
        return f"{prefix}```{self._lang}\n{body}\n```"

    def text_display(self) -> discord.ui.TextDisplay:
        return discord.ui.TextDisplay(self.render())

    def build(self) -> discord.ui.TextDisplay:
        return self.text_display()


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

    def file(self, builder: FileBuilder) -> Self:
        self._children.append(builder.build())
        return self

    def attachment(self, builder: FileBuilder) -> Self:
        return self.file(builder)

    def document(self, builder: FileBuilder) -> Self:
        return self.file(builder)

    def table(self, builder: TableBuilder) -> Self:
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

    def add_galleries(self, source: MediaCollector | list[discord.ui.MediaGallery]) -> Self:
        built = source.galleries() if isinstance(source, MediaCollector) else source
        for component in built:
            self.add_item(component)
        return self

    def media_galleries(self, source: MediaCollector | list[discord.ui.MediaGallery]) -> Self:
        return self.add_galleries(source)

    def collect(self, source: MediaCollector | list[discord.ui.MediaGallery]) -> Self:
        return self.add_galleries(source)

    def images(self, builder: GalleryBuilder) -> Self:
        return self.gallery(builder)

    def media(self, builder: GalleryBuilder) -> Self:
        return self.gallery(builder)

    def file(self, builder: FileBuilder) -> Self:
        self.add_item(builder.build())
        return self

    def attachment(self, builder: FileBuilder) -> Self:
        return self.file(builder)

    def document(self, builder: FileBuilder) -> Self:
        return self.file(builder)

    def table(self, builder: TableBuilder) -> Self:
        self.add_item(builder.build())
        return self

    def _audit(self) -> tuple[int, int, list[str]]:
        total = 0
        text_chars = 0
        problems: list[str] = []
        for item in _walk_components(self):
            total += 1
            content = getattr(item, "content", None)
            if isinstance(content, str):
                text_chars += len(content)
            if isinstance(item, discord.ui.MediaGallery):
                count = len(getattr(item, "items", []))
                if count > MediaCollector.MAX_PER_GALLERY:
                    problems.append(f"a media gallery holds {count} items (Discord allows 10)")
        if total > 40:
            problems.append(f"{total} total components (Discord allows 40)")
        if text_chars > 4000:
            problems.append(f"{text_chars} characters of text (Discord allows 4000)")
        return total, text_chars, problems

    def is_valid(self) -> bool:
        return not self._audit()[2]

    def component_count(self) -> int:
        return self._audit()[0]

    def text_length(self) -> int:
        return self._audit()[1]

    def validate(self) -> Self:
        problems = self._audit()[2]
        if problems:
            raise VexValidationError("this view exceeds Discord's limits: " + "; ".join(problems))
        return self

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


def media_collector() -> MediaCollector:
    return MediaCollector()


def collector() -> MediaCollector:
    return MediaCollector()


def file_component(*, id: int | None = None) -> FileBuilder:
    return FileBuilder(id=id)


def file(*, id: int | None = None) -> FileBuilder:
    return FileBuilder(id=id)


def document(*, id: int | None = None) -> FileBuilder:
    return FileBuilder(id=id)


def table(*, title: str | None = None) -> TableBuilder:
    return TableBuilder(title=title)


def leaderboard(*, title: str | None = None) -> TableBuilder:
    return TableBuilder(title=title)


def text_file(content: str | bytes, filename: str = "message.txt", *, spoiler: bool = False) -> discord.File:
    raw = content.encode("utf-8") if isinstance(content, str) else content
    buffer = io.BytesIO(raw)
    buffer.seek(0)
    return discord.File(buffer, filename=filename, spoiler=spoiler)


def bytes_file(content: str | bytes, filename: str = "message.txt", *, spoiler: bool = False) -> discord.File:
    return text_file(content, filename, spoiler=spoiler)


def file_from_text(content: str | bytes, filename: str = "message.txt", *, spoiler: bool = False) -> discord.File:
    return text_file(content, filename, spoiler=spoiler)


def progress(
    value: float,
    maximum: float,
    *,
    width: int = 20,
    fill: str = "\u2588",
    track: str = "\u2591",
    prefix: str = "",
    suffix: str = "",
    show_percent: bool = True,
    show_value: bool = False,
    percent_format: str = "{pct:.0f}%",
) -> str:
    span = maximum if maximum else 1
    ratio = 0.0 if span <= 0 else max(0.0, min(1.0, value / span))
    filled = int(round(ratio * width))
    bar = prefix + fill * filled + track * (width - filled) + suffix
    tail = ""
    if show_percent:
        tail += " " + percent_format.format(pct=ratio * 100)
    if show_value:
        shown = int(value) if float(value).is_integer() else value
        cap = int(maximum) if float(maximum).is_integer() else maximum
        tail += f" ({shown}/{cap})"
    return bar + tail


def bar(value: float, maximum: float, **kwargs: Any) -> str:
    return progress(value, maximum, **kwargs)


def meter(value: float, maximum: float, **kwargs: Any) -> str:
    return progress(value, maximum, **kwargs)


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
        self._name_locked: bool = False
        self._desc_locked: bool = False
        self._desc_user_locked: bool = False


def _unwrap_callback(obj: Any) -> Any:
    callback = getattr(obj, "callback", None)
    if callback is not None and callable(callback):
        return callback
    return obj


def _attach_meta(obj: Any, *, lock_name: bool = False, lock_desc: bool = False, user_desc: bool = False, **kwargs: Any) -> CommandInfo:
    target = _unwrap_callback(obj)
    info = getattr(target, "__vex_help__", None)
    if info is None:
        default_name = getattr(target, "__name__", None) or getattr(obj, "name", None) or "unknown"
        info = CommandInfo(default_name, target)
        try:
            setattr(target, "__vex_help__", info)
        except (AttributeError, TypeError):
            try:
                setattr(obj, "__vex_help__", info)
            except (AttributeError, TypeError):
                pass
    for key, value in kwargs.items():
        if value is None:
            continue
        if isinstance(value, str) and value == "":
            continue
        if key == "aliases":
            if not value:
                continue
            for alias in value:
                if alias not in info.aliases:
                    info.aliases.append(alias)
            continue
        if key == "name":
            if info._name_locked and not lock_name:
                continue
            if lock_name:
                info._name_locked = True
        elif key == "description":
            if info._desc_user_locked and not user_desc:
                continue
            if info._desc_locked and not lock_desc and not user_desc:
                continue
            if user_desc:
                info._desc_user_locked = True
                info._desc_locked = True
            elif lock_desc:
                info._desc_locked = True
        setattr(info, key, value)
    return info


def _apply_command_meta(
    obj: Any,
    command_name: str,
    *,
    description: str | None,
    resolved: str,
    category: str | None = None,
    aliases: list[str] | None = None,
) -> CommandInfo:
    info = _attach_meta(obj, lock_name=True, name=command_name, category=category, aliases=aliases)
    if description is not None:
        _attach_meta(obj, lock_desc=True, description=description)
    elif resolved and resolved != "\u2026":
        if not info._desc_locked and not info._desc_user_locked and not info.description:
            info.description = resolved
    return info


def cmd(name: str | Callable[..., Any] | None = None, *, aliases: list[str] | None = None) -> Callable[[Any], Any]:
    def decorator(obj: Any) -> Any:
        meta: dict[str, Any] = {}
        if isinstance(name, str):
            meta["name"] = name
        if aliases:
            meta["aliases"] = aliases
        _attach_meta(obj, **meta)
        return obj
    if callable(name) and not isinstance(name, str):
        return decorator(name)
    return decorator


def cmd_desc(text: str) -> Callable[[Any], Any]:
    def decorator(obj: Any) -> Any:
        _attach_meta(obj, user_desc=True, description=text)
        return obj
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


class VexValidationError(Exception):
    pass


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
        self._future: asyncio.Future[bool] = _new_future()

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
        self._future: asyncio.Future[bool] = _new_future()

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
        self._future: asyncio.Future[bool] = _new_future()
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
        self._future: asyncio.Future[str | None] = _new_future()

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


class Theme:
    def __init__(
        self,
        *,
        error: str = "#ed4245",
        success: str = "#57f287",
        info: str = "#5865f2",
        warning: str = "#fee75c",
        accent: str = "#5865f2",
        muted: str = "#4f545c",
    ) -> None:
        self.error = error
        self.success = success
        self.info = info
        self.warning = warning
        self.accent = accent
        self.muted = muted

    def color(self, name: str) -> str:
        return getattr(self, name, self.accent)

    def colour(self, name: str) -> str:
        return self.color(name)


_THEME = Theme()


def theme() -> Theme:
    return _THEME


def set_theme(**colors: str) -> Theme:
    for key, value in colors.items():
        if hasattr(_THEME, key):
            setattr(_THEME, key, value)
    return _THEME


def use_theme(custom: Theme) -> Theme:
    global _THEME
    _THEME = custom
    return _THEME


def error_card(message: str, *, title: str = "Error") -> ContainerBuilder:
    return (
        container()
        .hex(theme().error)
        .h3(title)
        .text(message)
    )


def success_card(message: str, *, title: str = "Success") -> ContainerBuilder:
    return (
        container()
        .hex(theme().success)
        .h3(title)
        .text(message)
    )


def info_card(message: str, *, title: str = "Info") -> ContainerBuilder:
    return (
        container()
        .hex(theme().info)
        .h3(title)
        .text(message)
    )


def warning_card(message: str, *, title: str = "Warning") -> ContainerBuilder:
    return (
        container()
        .hex(theme().warning)
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
        self._future: asyncio.Future[list[str] | None] = _new_future()

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
        self._future: asyncio.Future[list[discord.Role] | None] = _new_future()

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
        self._future: asyncio.Future[list[Any] | None] = _new_future()

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
        self._future: asyncio.Future[list[discord.Member | discord.User] | None] = _new_future()

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
        return max(0, bucket.rate - bucket._tokens)


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
    def decorator(obj: Any) -> Any:
        info = _attach_meta(obj)
        if alias not in info.aliases:
            info.aliases.append(alias)
        return obj
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


_PRESENCE_PROFILES: dict[str, dict[str, str]] = {
    "desktop": {
        "os": "Windows",
        "browser": "Discord Client",
        "device": "discord_client",
    },
    "mac": {
        "os": "Mac OS X",
        "browser": "Discord Client",
        "device": "discord_client",
    },
    "linux": {
        "os": "Linux",
        "browser": "Discord Client",
        "device": "discord_client",
    },
    "mobile": {
        "os": "iOS",
        "browser": "Discord iOS",
        "device": "discord_ios",
    },
    "android": {
        "os": "Android",
        "browser": "Discord Android",
        "device": "discord_android",
    },
    "vr": {
        "os": "Android",
        "browser": "Discord VR",
        "device": "discord_vr",
    },
    "web": {
        "os": "Windows",
        "browser": "Chrome",
        "device": "",
    },
    "embedded": {
        "os": "Discord Embedded",
        "browser": "Discord Embedded",
        "device": "discord_embedded",
    },
}


class PresenceHandler:
    _active_profile: dict[str, str] | None = None
    _original_identify: Any = None
    _original_send: Any = None
    _patched: bool = False

    @classmethod
    def _make_identify(cls) -> Any:
        original = cls._original_identify

        async def _patched_identify(self_ws: Any) -> None:
            profile = cls._active_profile
            if profile is not None:
                self_ws.__dict__["_vex_presence_profile"] = profile
            await original(self_ws)

        return _patched_identify

    @classmethod
    def _make_send(cls) -> Any:
        original_send = discord.gateway.DiscordWebSocket.send_as_json
        cls._original_send = original_send

        async def _patched_send(self_ws: Any, data: Any) -> None:
            profile: dict[str, str] | None = self_ws.__dict__.get("_vex_presence_profile")
            if profile is not None and isinstance(data, dict) and data.get("op") == discord.gateway.DiscordWebSocket.IDENTIFY:
                d = data.setdefault("d", {})
                props = d.setdefault("properties", {})
                props["os"] = profile["os"]
                props["browser"] = profile["browser"]
                props["device"] = profile["device"]
            await original_send(self_ws, data)

        return _patched_send

    _INVALIDATE_SESSION_MSG: str = '{"op":9,"d":false}'

    @classmethod
    def _schedule_reidentify(cls, bot: Any) -> None:
        loop = getattr(bot, "loop", None)
        if loop is not None and loop.is_running():
            loop.create_task(cls.reidentify_all(bot))

    @classmethod
    def apply(cls, profile: str | dict[str, str], *, bot: Any = None) -> None:
        if isinstance(profile, str):
            resolved = _PRESENCE_PROFILES.get(profile.lower())
            if resolved is None:
                raise ValueError(f"Unknown presence profile '{profile}'. Valid options: {list(_PRESENCE_PROFILES)}")
            cls._active_profile = resolved
        else:
            cls._active_profile = profile

        if not cls._patched:
            cls._original_identify = discord.gateway.DiscordWebSocket.identify
            discord.gateway.DiscordWebSocket.identify = cls._make_identify()
            discord.gateway.DiscordWebSocket.send_as_json = cls._make_send()
            cls._patched = True

        if bot is not None:
            cls._schedule_reidentify(bot)

    @classmethod
    async def apply_async(cls, profile: str | dict[str, str], *, bot: Any) -> None:
        cls.apply(profile)
        await cls.reidentify_all(bot)

    @classmethod
    async def _invalidate_ws(cls, ws: Any) -> None:
        try:
            await ws.received_message(cls._INVALIDATE_SESSION_MSG)
        except Exception:
            pass

    @classmethod
    async def reidentify_all(cls, bot: Any) -> None:
        raw_shards: dict[int, Any] = getattr(bot, "_AutoShardedClient__shards", {})
        if raw_shards:
            for shard in raw_shards.values():
                ws = getattr(shard, "ws", None)
                if ws is not None:
                    await cls._invalidate_ws(ws)
        else:
            ws = getattr(bot, "ws", None)
            if ws is not None:
                await cls._invalidate_ws(ws)

    @classmethod
    def restore(cls, *, bot: Any = None) -> None:
        if cls._patched:
            if cls._original_identify is not None:
                discord.gateway.DiscordWebSocket.identify = cls._original_identify
                cls._original_identify = None
            if cls._original_send is not None:
                discord.gateway.DiscordWebSocket.send_as_json = cls._original_send
                cls._original_send = None
            cls._patched = False
            cls._active_profile = None

        if bot is not None:
            cls._schedule_reidentify(bot)

    @classmethod
    async def restore_async(cls, *, bot: Any) -> None:
        cls.restore()
        await cls.reidentify_all(bot)

    @classmethod
    def current(cls) -> dict[str, str] | None:
        return cls._active_profile

    @classmethod
    def profiles(cls) -> list[str]:
        return list(_PRESENCE_PROFILES)

    @classmethod
    def desktop(cls, *, bot: Any = None) -> None:
        cls.apply("desktop", bot=bot)

    @classmethod
    def mac(cls, *, bot: Any = None) -> None:
        cls.apply("mac", bot=bot)

    @classmethod
    def linux(cls, *, bot: Any = None) -> None:
        cls.apply("linux", bot=bot)

    @classmethod
    def mobile(cls, *, bot: Any = None) -> None:
        cls.apply("mobile", bot=bot)

    @classmethod
    def android(cls, *, bot: Any = None) -> None:
        cls.apply("android", bot=bot)

    @classmethod
    def vr(cls, *, bot: Any = None) -> None:
        cls.apply("vr", bot=bot)

    @classmethod
    def web(cls, *, bot: Any = None) -> None:
        cls.apply("web", bot=bot)

    @classmethod
    def embedded(cls, *, bot: Any = None) -> None:
        cls.apply("embedded", bot=bot)

    @classmethod
    def custom(cls, *, bot: Any = None, **props: str) -> None:
        cls.apply(props, bot=bot)


def presence(profile: str | dict[str, str], *, bot: Any = None) -> None:
    PresenceHandler.apply(profile, bot=bot)

class PollBuilder:
    def __init__(self, question: str = "") -> None:
        self._question = question
        self._duration = datetime.timedelta(hours=24)
        self._multiple = False
        self._answers: list[tuple[str, Any]] = []

    def question(self, text: str) -> Self:
        self._question = text
        return self

    def ask(self, text: str) -> Self:
        return self.question(text)

    def prompt(self, text: str) -> Self:
        return self.question(text)

    def duration(self, *, days: int = 0, hours: int = 0, minutes: int = 0) -> Self:
        self._duration = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        return self

    def hours(self, count: float) -> Self:
        self._duration = datetime.timedelta(hours=count)
        return self

    def days(self, count: float) -> Self:
        self._duration = datetime.timedelta(days=count)
        return self

    def multiple(self, state: bool = True) -> Self:
        self._multiple = state
        return self

    def single(self) -> Self:
        self._multiple = False
        return self

    def answer(self, text: str, *, emoji: Any = None) -> Self:
        self._answers.append((text, emoji))
        return self

    def option(self, text: str, *, emoji: Any = None) -> Self:
        return self.answer(text, emoji=emoji)

    def choice(self, text: str, *, emoji: Any = None) -> Self:
        return self.answer(text, emoji=emoji)

    def options(self, items: list[Any]) -> Self:
        for item in items:
            if isinstance(item, (list, tuple)):
                self.answer(str(item[0]), emoji=item[1] if len(item) > 1 else None)
            else:
                self.answer(str(item))
        return self

    def build(self) -> discord.Poll:
        poll = discord.Poll(question=self._question, duration=self._duration, multiple=self._multiple)
        for text, emoji in self._answers:
            if emoji is not None:
                poll.add_answer(text=text, emoji=emoji)
            else:
                poll.add_answer(text=text)
        return poll


def poll(question: str = "") -> PollBuilder:
    return PollBuilder(question)


def survey(question: str = "") -> PollBuilder:
    return PollBuilder(question)


def persist(view: discord.ui.LayoutView, bot: commands.Bot) -> discord.ui.LayoutView:
    if getattr(view, "timeout", None) is not None:
        raise VexValidationError("persistent views must be created with timeout=None so they survive restarts")
    missing: list[str] = []
    for item in _walk_components(view):
        if isinstance(item, discord.ui.Button):
            if item.url is None and getattr(item, "sku_id", None) is None and not item.custom_id:
                missing.append("button")
        elif isinstance(item, discord.ui.Select):
            if not item.custom_id:
                missing.append("select")
    if missing:
        kinds = ", ".join(sorted(set(missing)))
        raise VexValidationError(f"persistent views need a custom_id on every interactive component; missing on: {kinds}")
    bot.add_view(view)
    return view


def register_view(view: discord.ui.LayoutView, bot: commands.Bot) -> discord.ui.LayoutView:
    return persist(view, bot)


def make_persistent(view: discord.ui.LayoutView, bot: commands.Bot) -> discord.ui.LayoutView:
    return persist(view, bot)


class TypedConfirmView(discord.ui.LayoutView):
    def __init__(
        self,
        *,
        prompt: str,
        phrase: str,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        field_label: str | None = None,
        case_sensitive: bool = False,
        timeout: float | None = 60.0,
        ephemeral: bool = True,
        owner_id: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._phrase = phrase
        self._case = case_sensitive
        self._ephemeral = ephemeral
        self._owner_id = owner_id
        self._result: bool | None = None
        self._field_label = field_label or f"Type {phrase} to confirm"
        self._future: asyncio.Future[bool] = _new_future()
        confirm_btn = discord.ui.Button(style=discord.ButtonStyle.danger, label=confirm_label, custom_id="vex_typed_yes")
        cancel_btn = discord.ui.Button(style=discord.ButtonStyle.secondary, label=cancel_label, custom_id="vex_typed_no")
        confirm_btn.callback = self._open_modal
        cancel_btn.callback = self._cancel
        self.add_item(discord.ui.TextDisplay(prompt))
        self.add_item(discord.ui.TextDisplay(f"-# You will be asked to type `{phrase}` to continue."))
        self.add_item(discord.ui.ActionRow(confirm_btn, cancel_btn))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._owner_id is None or interaction.user.id == self._owner_id:
            return True
        await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
        return False

    def _matches(self, value: str) -> bool:
        left = value.strip()
        right = self._phrase.strip()
        if not self._case:
            left = left.casefold()
            right = right.casefold()
        return left == right

    def _freeze(self) -> None:
        for item in list(self.children):
            if hasattr(item, "disabled"):
                item.disabled = True
            for child in getattr(item, "children", []) or []:
                if hasattr(child, "disabled"):
                    child.disabled = True

    async def _open_modal(self, interaction: discord.Interaction) -> None:
        outer = self
        field = discord.ui.TextInput(
            label=outer._field_label[:45],
            custom_id="vex_typed_phrase",
            required=True,
            max_length=max(1, min(len(outer._phrase) + 20, 100)),
        )

        class _PhraseModal(discord.ui.Modal, title="Confirm action"):
            def __init__(self) -> None:
                super().__init__(timeout=outer.timeout or 60.0)
                self.add_item(field)

            async def on_submit(self, inner: discord.Interaction) -> None:
                if outer._matches(field.value):
                    outer._result = True
                    outer._freeze()
                    outer.stop()
                    if not outer._future.done():
                        outer._future.set_result(True)
                    await inner.response.edit_message(view=outer)
                else:
                    await inner.response.send_message(VexError.NOT_CONFIRMED, ephemeral=True)

        await interaction.response.send_modal(_PhraseModal())

    async def _cancel(self, interaction: discord.Interaction) -> None:
        self._result = False
        self._freeze()
        self.stop()
        if not self._future.done():
            self._future.set_result(False)
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        self._result = None
        if not self._future.done():
            self._future.set_result(False)

    @property
    def result(self) -> bool | None:
        return self._result

    @property
    def confirmed(self) -> bool:
        return self._result is True

    async def wait_result(self) -> bool:
        return await self._future

    async def send_to(self, target: discord.abc.Messageable) -> bool:
        await target.send(view=self)
        return await self.wait_result()

    async def reply_to(self, interaction: discord.Interaction) -> bool:
        if interaction.response.is_done():
            await interaction.followup.send(view=self, ephemeral=self._ephemeral)
        else:
            await interaction.response.send_message(view=self, ephemeral=self._ephemeral)
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> bool:
        return await self.reply_to(interaction)

    async def ask(self, interaction: discord.Interaction) -> bool:
        return await self.reply_to(interaction)


def typed_confirm(
    prompt: str,
    phrase: str,
    *,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    field_label: str | None = None,
    case_sensitive: bool = False,
    timeout: float | None = 60.0,
    ephemeral: bool = True,
    owner_id: int | None = None,
) -> TypedConfirmView:
    return TypedConfirmView(
        prompt=prompt,
        phrase=phrase,
        confirm_label=confirm_label,
        cancel_label=cancel_label,
        field_label=field_label,
        case_sensitive=case_sensitive,
        timeout=timeout,
        ephemeral=ephemeral,
        owner_id=owner_id,
    )


class WizardStep:
    def __init__(self, title: str, fields: list[Any]) -> None:
        self.title = title
        self.fields = fields


class Wizard(discord.ui.LayoutView):
    def __init__(
        self,
        steps: list[WizardStep] | None = None,
        *,
        title: str = "Setup",
        timeout: float | None = 300.0,
        owner_id: int | None = None,
        ephemeral: bool = True,
    ) -> None:
        super().__init__(timeout=timeout)
        self._steps: list[WizardStep] = list(steps or [])
        self._title = title
        self._owner_id = owner_id
        self._ephemeral = ephemeral
        self._index = 0
        self._data: dict[str, str] = {}
        self._future: asyncio.Future[dict[str, str] | None] = _new_future()

    def step(self, title: str, fields: list[Any]) -> Self:
        self._steps.append(WizardStep(title, fields))
        return self

    def add_step(self, title: str, fields: list[Any]) -> Self:
        return self.step(title, fields)

    def interaction_check(self, interaction: discord.Interaction) -> Any:
        async def check() -> bool:
            if self._owner_id is None or interaction.user.id == self._owner_id:
                return True
            await interaction.response.send_message(VexError.FORBIDDEN, ephemeral=True)
            return False
        return check()

    def _render(self) -> None:
        self.clear_items()
        if not self._steps:
            self.add_item(discord.ui.TextDisplay(f"# {self._title}"))
            self.add_item(discord.ui.TextDisplay("No steps were configured."))
            return
        current = self._steps[self._index]
        self.add_item(discord.ui.TextDisplay(f"# {self._title}"))
        self.add_item(discord.ui.TextDisplay(f"**Step {self._index + 1} of {len(self._steps)}** \u00b7 {current.title}"))
        self.add_item(discord.ui.TextDisplay(progress(self._index, len(self._steps), width=14, show_percent=False)))
        open_btn = discord.ui.Button(style=discord.ButtonStyle.primary, label="Open form", custom_id="vex_wizard_open")
        cancel_btn = discord.ui.Button(style=discord.ButtonStyle.secondary, label="Cancel", custom_id="vex_wizard_cancel")
        open_btn.callback = self._open
        cancel_btn.callback = self._cancel
        self.add_item(discord.ui.ActionRow(open_btn, cancel_btn))

    def _finish(self) -> None:
        self.clear_items()
        self.add_item(discord.ui.TextDisplay(f"# {self._title}"))
        self.add_item(discord.ui.TextDisplay("All steps complete."))

    async def _open(self, interaction: discord.Interaction) -> None:
        outer = self
        current = self._steps[self._index]
        inputs = [field.build() if hasattr(field, "build") else field for field in current.fields]

        class _StepModal(discord.ui.Modal, title=current.title[:45] or "Step"):
            def __init__(self) -> None:
                super().__init__(timeout=outer.timeout or 300.0)
                for field in inputs:
                    self.add_item(field)

            async def on_submit(self, inner: discord.Interaction) -> None:
                for field in inputs:
                    outer._data[field.custom_id] = field.value
                outer._index += 1
                if outer._index >= len(outer._steps):
                    outer._finish()
                    outer.stop()
                    if not outer._future.done():
                        outer._future.set_result(dict(outer._data))
                else:
                    outer._render()
                await inner.response.edit_message(view=outer)

        await interaction.response.send_modal(_StepModal())

    async def _cancel(self, interaction: discord.Interaction) -> None:
        self.clear_items()
        self.add_item(discord.ui.TextDisplay(f"# {self._title}"))
        self.add_item(discord.ui.TextDisplay(VexError.CONFIRM_CANCELLED))
        self.stop()
        if not self._future.done():
            self._future.set_result(None)
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        if not self._future.done():
            self._future.set_result(None)

    @property
    def data(self) -> dict[str, str]:
        return dict(self._data)

    async def wait_result(self) -> dict[str, str] | None:
        return await self._future

    async def send_to(self, target: discord.abc.Messageable) -> dict[str, str] | None:
        self._render()
        await target.send(view=self)
        return await self.wait_result()

    async def reply_to(self, interaction: discord.Interaction) -> dict[str, str] | None:
        self._render()
        if interaction.response.is_done():
            await interaction.followup.send(view=self, ephemeral=self._ephemeral)
        else:
            await interaction.response.send_message(view=self, ephemeral=self._ephemeral)
        return await self.wait_result()

    async def respond(self, interaction: discord.Interaction) -> dict[str, str] | None:
        return await self.reply_to(interaction)


def wizard(
    steps: list[WizardStep] | None = None,
    *,
    title: str = "Setup",
    timeout: float | None = 300.0,
    owner_id: int | None = None,
    ephemeral: bool = True,
) -> Wizard:
    return Wizard(steps, title=title, timeout=timeout, owner_id=owner_id, ephemeral=ephemeral)


class LiveView(Vex):
    def __init__(
        self,
        renderer: Callable[["LiveView"], Any],
        *,
        interval: float = 5.0,
        timeout: float | None = 300.0,
        max_updates: int | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._renderer = renderer
        self._interval = max(1.0, float(interval))
        self._max = max_updates
        self._updates = 0
        self._message: discord.Message | None = None
        self._task: asyncio.Task[None] | None = None
        self._apply()

    def _mount(self, item: Any) -> None:
        if isinstance(item, ContainerBuilder):
            self.add_item(item.build())
        elif isinstance(item, (SectionBuilder, ActionRowBuilder, GalleryBuilder, FileBuilder, TableBuilder)):
            self.add_item(item.build())
        elif isinstance(item, str):
            self.add_item(discord.ui.TextDisplay(item))
        elif item is not None:
            self.add_item(item)

    def _apply(self) -> None:
        self.clear_items()
        produced = self._renderer(self)
        if produced is None:
            return
        items = produced if isinstance(produced, list) else [produced]
        for item in items:
            self._mount(item)

    def _start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._loop())

    async def _loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._interval)
                if self.is_finished():
                    break
                self._updates += 1
                self._apply()
                if self._message is not None:
                    try:
                        await self._message.edit(view=self)
                    except discord.HTTPException:
                        break
                if self._max is not None and self._updates >= self._max:
                    break
        except asyncio.CancelledError:
            pass

    async def refresh(self) -> None:
        self._apply()
        if self._message is not None:
            try:
                await self._message.edit(view=self)
            except discord.HTTPException:
                pass

    def stop(self) -> None:
        super().stop()
        if self._task is not None and not self._task.done():
            self._task.cancel()

    async def on_timeout(self) -> None:
        await super().on_timeout()
        if self._task is not None and not self._task.done():
            self._task.cancel()
        if self._message is not None:
            try:
                await self._message.edit(view=self)
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
        self._start()
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
            self._message = None
        self._start()


def live(
    renderer: Callable[["LiveView"], Any],
    *,
    interval: float = 5.0,
    timeout: float | None = 300.0,
    max_updates: int | None = None,
) -> LiveView:
    return LiveView(renderer, interval=interval, timeout=timeout, max_updates=max_updates)


_log = logging.getLogger("vex")

_PENDING_APP_COMMANDS: list[Any] = []
_PENDING_TEXT_COMMANDS: list[Any] = []


def _is_class_scoped(func: Any) -> bool:
    qualname = getattr(func, "__qualname__", "")
    if "." not in qualname:
        return False
    parent = qualname.rsplit(".", 1)[0]
    return not parent.endswith("<locals>")


def _short_doc(func: Any) -> str:
    doc = inspect.getdoc(func)
    if not doc:
        return ""
    first = doc.strip().splitlines()[0].strip()
    return first[:100]


def _resolve_description(func: Any, supplied: str | None) -> str:
    if supplied:
        return supplied[:100]
    inferred = _short_doc(func)
    return inferred or "\u2026"


def _as_object(value: int | discord.abc.Snowflake) -> discord.Object:
    if isinstance(value, discord.Object):
        return value
    snowflake_id = getattr(value, "id", None)
    if snowflake_id is not None:
        return discord.Object(id=int(snowflake_id))
    return discord.Object(id=int(value))


def _normalise_guilds(
    guild: int | discord.abc.Snowflake | None,
    guilds: list[int | discord.abc.Snowflake] | None,
) -> list[discord.Object] | None:
    collected: list[discord.Object] = []
    if guild is not None:
        collected.append(_as_object(guild))
    if guilds:
        for entry in guilds:
            collected.append(_as_object(entry))
    return collected or None


def slash_cmd(
    name: str | Callable[..., Any] | None = None,
    *,
    description: str | None = None,
    guild: int | discord.abc.Snowflake | None = None,
    guilds: list[int | discord.abc.Snowflake] | None = None,
    nsfw: bool = False,
    category: str | None = None,
    extras: dict[str, Any] | None = None,
) -> Any:
    direct: Any = None
    if callable(name) and not isinstance(name, str):
        direct = name
        name = None

    def decorator(func: Any) -> app_commands.Command:
        command_name = (name or getattr(func, "__name__", "command")).lower().replace(" ", "-")
        resolved = _resolve_description(func, description)
        command = app_commands.command(name=command_name, description=resolved)(func)
        if nsfw:
            command.nsfw = True
        if extras:
            command.extras.update(extras)
        _apply_command_meta(func, command_name, description=description, resolved=resolved, category=category)
        targets = _normalise_guilds(guild, guilds)
        if targets is not None:
            setattr(command, "_vex_guilds", targets)
        setattr(command, "_vex_kind", "slash")
        _drain_pending_checks(func, command)
        if not _is_class_scoped(func):
            _PENDING_APP_COMMANDS.append(command)
        return command

    if direct is not None:
        return decorator(direct)
    return decorator


def hybrid_cmd(
    name: str | Callable[..., Any] | None = None,
    *,
    description: str | None = None,
    aliases: list[str] | None = None,
    guild: int | discord.abc.Snowflake | None = None,
    guilds: list[int | discord.abc.Snowflake] | None = None,
    with_app_command: bool = True,
    category: str | None = None,
    extras: dict[str, Any] | None = None,
) -> Any:
    direct: Any = None
    if callable(name) and not isinstance(name, str):
        direct = name
        name = None

    def decorator(func: Any) -> commands.HybridCommand:
        command_name = name or getattr(func, "__name__", "command")
        resolved = _resolve_description(func, description)
        command = commands.hybrid_command(
            name=command_name,
            description=resolved,
            aliases=aliases or [],
            with_app_command=with_app_command,
            extras=extras or {},
        )(func)
        _apply_command_meta(func, command_name, description=description, resolved=resolved, category=category, aliases=aliases)
        targets = _normalise_guilds(guild, guilds)
        if targets is not None:
            setattr(command, "_vex_guilds", targets)
        setattr(command, "_vex_kind", "hybrid")
        _drain_pending_checks(func, command)
        if not _is_class_scoped(func):
            _PENDING_TEXT_COMMANDS.append(command)
        return command

    if direct is not None:
        return decorator(direct)
    return decorator


def _wants_argument(cls: type) -> bool:
    try:
        signature = inspect.signature(cls.__init__)
    except (ValueError, TypeError):
        return False
    parameters = [
        param
        for param in signature.parameters.values()
        if param.name != "self" and param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
    ]
    return len(parameters) >= 1


class Bot(commands.Bot):
    def __init__(
        self,
        command_prefix: Any = "!",
        *,
        intents: discord.Intents | None = None,
        description: str | None = None,
        owner_id: int | None = None,
        owner_ids: set[int] | None = None,
        help_command: Any = "keep",
        message_content: bool = False,
        members: bool = False,
        presences: bool = False,
        cogs: list[str] | str | None = None,
        auto_sync: bool = False,
        sync_guild: int | discord.abc.Snowflake | None = None,
        case_insensitive: bool = True,
        strip_after_prefix: bool = True,
        on_ready_log: bool = True,
        handle_errors: bool = True,
        setup: Callable[["Bot"], Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = message_content
            intents.members = members
            intents.presences = presences
        if help_command != "keep":
            kwargs["help_command"] = help_command
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            description=description,
            owner_id=owner_id,
            owner_ids=owner_ids,
            case_insensitive=case_insensitive,
            strip_after_prefix=strip_after_prefix,
            **kwargs,
        )
        self._auto_sync = auto_sync
        self._sync_guild = _as_object(sync_guild) if sync_guild is not None else None
        self._cog_targets: list[str] = [cogs] if isinstance(cogs, str) else list(cogs or [])
        self._post_setup = setup
        self._on_ready_log = on_ready_log
        self._handle_errors = handle_errors
        self._announced = False
        if handle_errors:
            self.tree.error(self._tree_error)

    def _add_app_command(self, command: app_commands.Command) -> None:
        targets = getattr(command, "_vex_guilds", None)
        if targets:
            self.tree.add_command(command, guilds=targets)
        else:
            self.tree.add_command(command)

    def _add_text_command(self, command: commands.Command) -> None:
        targets = getattr(command, "_vex_guilds", None)
        if targets:
            try:
                app_commands.guilds(*targets)(command)
            except Exception:
                pass
        if self.get_command(command.name) is None:
            self.add_command(command)

    def _adopt_app_command(self, command: app_commands.Command) -> None:
        if command in _PENDING_APP_COMMANDS:
            _PENDING_APP_COMMANDS.remove(command)
        self._add_app_command(command)

    def _adopt_text_command(self, command: commands.Command) -> None:
        if command in _PENDING_TEXT_COMMANDS:
            _PENDING_TEXT_COMMANDS.remove(command)
        self._add_text_command(command)

    async def _register_pending(self) -> None:
        for command in list(_PENDING_APP_COMMANDS):
            try:
                self._add_app_command(command)
            except app_commands.CommandAlreadyRegistered:
                pass
        _PENDING_APP_COMMANDS.clear()
        for command in list(_PENDING_TEXT_COMMANDS):
            self._add_text_command(command)
        _PENDING_TEXT_COMMANDS.clear()
        for event_name, callback in list(_PENDING_LISTENERS):
            self.add_listener(callback, name=event_name)
        _PENDING_LISTENERS.clear()

    @staticmethod
    def _discover_extensions(target: str) -> list[str]:
        looks_like_path = (
            os.sep in target
            or (os.altsep and os.altsep in target)
            or target.endswith(".py")
            or os.path.isdir(target)
        )
        if looks_like_path:
            path = os.path.abspath(target)
            if path.endswith(".py"):
                directory = os.path.dirname(path)
                package = os.path.basename(directory)
                module = os.path.splitext(os.path.basename(path))[0]
                parent = os.path.dirname(directory)
                if parent not in sys.path:
                    sys.path.insert(0, parent)
                return [f"{package}.{module}"]
            package = os.path.basename(path.rstrip(os.sep))
            parent = os.path.dirname(path.rstrip(os.sep))
            if parent not in sys.path:
                sys.path.insert(0, parent)
            discovered: list[str] = []
            for entry in sorted(os.listdir(path)):
                if entry.startswith("_") or not entry.endswith(".py"):
                    continue
                discovered.append(f"{package}.{entry[:-3]}")
            return discovered
        try:
            module = importlib.import_module(target)
        except ImportError:
            return [target]
        if hasattr(module, "__path__"):
            return [name for _, name, _ in pkgutil.iter_modules(module.__path__, module.__name__ + ".")]
        return [target]

    async def _load_one(self, name: str) -> bool:
        try:
            await self.load_extension(name)
            return True
        except commands.NoEntryPointError:
            module = importlib.import_module(name)
            added = 0
            for _, member in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(member, commands.Cog)
                    and member is not commands.Cog
                    and member.__module__ == module.__name__
                ):
                    instance = member(self) if _wants_argument(member) else member()
                    await self.add_cog(instance)
                    added += 1
            return added > 0
        except commands.ExtensionAlreadyLoaded:
            return True

    async def load_cogs(self, target: str) -> list[str]:
        loaded: list[str] = []
        for name in self._discover_extensions(target):
            try:
                if await self._load_one(name):
                    loaded.append(name)
            except commands.ExtensionError:
                _log.exception("Failed to load extension '%s'", name)
        if loaded:
            _log.info("Loaded %d cog module(s): %s", len(loaded), ", ".join(loaded))
        return loaded

    async def reload_cogs(self, target: str) -> list[str]:
        reloaded: list[str] = []
        for name in self._discover_extensions(target):
            try:
                await self.reload_extension(name)
                reloaded.append(name)
            except commands.ExtensionNotLoaded:
                if await self._load_one(name):
                    reloaded.append(name)
            except commands.ExtensionError:
                _log.exception("Failed to reload extension '%s'", name)
        return reloaded

    async def sync(self, guild: int | discord.abc.Snowflake | None = None, *, copy_global: bool = False) -> list[app_commands.AppCommand]:
        target = _as_object(guild) if guild is not None else None
        if target is not None:
            if copy_global:
                self.tree.copy_global_to(guild=target)
            return await self.tree.sync(guild=target)
        return await self.tree.sync()

    async def _maybe_sync(self) -> None:
        if not self._auto_sync:
            return
        try:
            if self._sync_guild is not None:
                synced = await self.sync(self._sync_guild, copy_global=True)
                _log.info("Synced %d command(s) to guild %s", len(synced), self._sync_guild.id)
            else:
                synced = await self.sync()
                _log.info("Synced %d command(s) globally", len(synced))
        except discord.HTTPException as exc:
            _log.warning("Application command sync failed: %s", exc)

    async def setup_hook(self) -> None:
        for target in self._cog_targets:
            await self.load_cogs(target)
        await self._register_pending()
        await self._maybe_sync()
        if self._post_setup is not None:
            await discord.utils.maybe_coroutine(self._post_setup, self)

    async def on_ready(self) -> None:
        if self._announced or not self._on_ready_log:
            return
        self._announced = True
        user = self.user
        guild_count = len(self.guilds)
        _log.info("Logged in as %s (%s) across %d guild(s)", user, getattr(user, "id", "?"), guild_count)

    def slash_cmd(self, name: str | Callable[..., Any] | None = None, **kwargs: Any) -> Any:
        if callable(name) and not isinstance(name, str):
            command = slash_cmd(**kwargs)(name)
            self._adopt_app_command(command)
            return command
        base = slash_cmd(name, **kwargs)

        def wrapper(func: Any) -> app_commands.Command:
            command = base(func)
            self._adopt_app_command(command)
            return command

        return wrapper

    def hybrid_cmd(self, name: str | Callable[..., Any] | None = None, **kwargs: Any) -> Any:
        if callable(name) and not isinstance(name, str):
            command = hybrid_cmd(**kwargs)(name)
            self._adopt_text_command(command)
            return command
        base = hybrid_cmd(name, **kwargs)

        def wrapper(func: Any) -> commands.HybridCommand:
            command = base(func)
            self._adopt_text_command(command)
            return command

        return wrapper

    async def _tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if not self._handle_errors:
            raise error
        message = describe_error(error)
        if message is None:
            original = getattr(error, "original", error)
            command_name = getattr(interaction.command, "qualified_name", "unknown")
            _log.error("Unhandled app command error in '%s'", command_name, exc_info=original)
            message = VexError.UNEXPECTED
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            pass

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if not self._handle_errors:
            return
        if self.extra_events.get("on_command_error"):
            return
        command = ctx.command
        if command is not None and command.has_error_handler():
            return
        cog = ctx.cog
        if cog is not None and cog.has_error_handler():
            return
        if isinstance(error, commands.CommandNotFound):
            return
        message = describe_error(error)
        if message is None:
            original = getattr(error, "original", error)
            command_name = getattr(command, "qualified_name", "unknown")
            _log.error("Unhandled command error in '%s'", command_name, exc_info=original)
            message = VexError.UNEXPECTED
        try:
            await ctx.send(message)
        except discord.HTTPException:
            pass

    def listener(self, name: str | None = None) -> Any:
        return self.listen(name) if name else self.listen()

    def run(self, token: str | None = None, **kwargs: Any) -> None:
        token = (
            token
            or os.environ.get("DISCORD_TOKEN")
            or os.environ.get("BOT_TOKEN")
            or os.environ.get("TOKEN")
        )
        if not token:
            raise RuntimeError(
                "No bot token supplied. Pass run(token) or set the DISCORD_TOKEN environment variable."
            )
        if "log_handler" not in kwargs and not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(name)s: %(message)s")
        super().run(token, **kwargs)


Client = Bot


def bot(command_prefix: Any = "!", **kwargs: Any) -> Bot:
    return Bot(command_prefix, **kwargs)


def client(command_prefix: Any = "!", **kwargs: Any) -> Bot:
    return Bot(command_prefix, **kwargs)


def _defined_in_class_body(depth: int = 2) -> bool:
    try:
        frame = sys._getframe(depth)
    except ValueError:
        return False
    return "__qualname__" in frame.f_locals and "__module__" in frame.f_locals


class Cog(commands.Cog):
    def __init__(self, bot: Bot | None = None) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        return None

    async def cog_unload(self) -> None:
        return None


class SlashGroup(app_commands.Group):
    def slash_cmd(
        self,
        name: str | Callable[..., Any] | None = None,
        *,
        description: str | None = None,
        nsfw: bool = False,
        extras: dict[str, Any] | None = None,
    ) -> Any:
        direct: Any = None
        if callable(name) and not isinstance(name, str):
            direct = name
            name = None

        def decorator(func: Any) -> app_commands.Command:
            resolved = _resolve_description(func, description)
            child_name = (name or getattr(func, "__name__", "command")).lower().replace(" ", "-")
            built = self.command(name=child_name, description=resolved, nsfw=nsfw, extras=extras or {})(func)
            info = _apply_command_meta(func, child_name, description=description, resolved=resolved)
            if info.category == "General":
                info.category = self.name
            _drain_pending_checks(func, built)
            return built

        if direct is not None:
            return decorator(direct)
        return decorator

    def sub(self, name: str | Callable[..., Any] | None = None, **kwargs: Any) -> Any:
        return self.slash_cmd(name, **kwargs)

    def subgroup(self, name: str, *, description: str = "\u2026") -> "SlashGroup":
        child = SlashGroup(name=name, description=description, parent=self)
        return child


def slash_group(
    name: str,
    *,
    description: str = "\u2026",
    guild: int | discord.abc.Snowflake | None = None,
    guilds: list[int | discord.abc.Snowflake] | None = None,
    guild_only: bool = False,
    nsfw: bool = False,
) -> SlashGroup:
    group_obj = SlashGroup(name=name, description=description, guild_only=guild_only, nsfw=nsfw)
    targets = _normalise_guilds(guild, guilds)
    if targets is not None:
        setattr(group_obj, "_vex_guilds", targets)
    setattr(group_obj, "_vex_kind", "group")
    if not _defined_in_class_body():
        _PENDING_APP_COMMANDS.append(group_obj)
    return group_obj


def group(name: str, **kwargs: Any) -> SlashGroup:
    return slash_group(name, **kwargs)


def command_group(name: str, **kwargs: Any) -> SlashGroup:
    return slash_group(name, **kwargs)


def hybrid_group(
    name: str | Callable[..., Any] | None = None,
    *,
    description: str | None = None,
    aliases: list[str] | None = None,
    guild: int | discord.abc.Snowflake | None = None,
    guilds: list[int | discord.abc.Snowflake] | None = None,
    with_app_command: bool = True,
    fallback: str | None = None,
) -> Any:
    direct: Any = None
    if callable(name) and not isinstance(name, str):
        direct = name
        name = None

    def decorator(func: Any) -> commands.HybridGroup:
        command_name = name or getattr(func, "__name__", "group")
        resolved = _resolve_description(func, description)
        built = commands.hybrid_group(
            name=command_name,
            description=resolved,
            aliases=aliases or [],
            with_app_command=with_app_command,
            fallback=fallback,
        )(func)
        _apply_command_meta(func, command_name, description=description, resolved=resolved, aliases=aliases)
        targets = _normalise_guilds(guild, guilds)
        if targets is not None:
            setattr(built, "_vex_guilds", targets)
        setattr(built, "_vex_kind", "hybrid_group")
        _drain_pending_checks(func, built)
        if not _is_class_scoped(func):
            _PENDING_TEXT_COMMANDS.append(built)
        return built

    if direct is not None:
        return decorator(direct)
    return decorator


_PENDING_LISTENERS: list[tuple[str, Callable[..., Any]]] = []

_BUCKETS = {
    "default": commands.BucketType.default,
    "global": commands.BucketType.default,
    "user": commands.BucketType.user,
    "member": commands.BucketType.member,
    "guild": commands.BucketType.guild,
    "server": commands.BucketType.guild,
    "channel": commands.BucketType.channel,
    "category": commands.BucketType.category,
    "role": commands.BucketType.role,
}


class _OwnerCheckFailure(app_commands.CheckFailure):
    pass


class _NSFWCheckFailure(app_commands.CheckFailure):
    pass


def _bucket_type(bucket: "str | commands.BucketType") -> commands.BucketType:
    if isinstance(bucket, commands.BucketType):
        return bucket
    return _BUCKETS.get(str(bucket).lower(), commands.BucketType.user)


def _cooldown_key(bucket: "str | commands.BucketType") -> Callable[[discord.Interaction], Any]:
    name = bucket.name if isinstance(bucket, commands.BucketType) else str(bucket).lower()
    if name in ("guild", "server"):
        return lambda interaction: interaction.guild_id
    if name == "channel":
        return lambda interaction: interaction.channel_id
    if name in ("default", "global"):
        return lambda interaction: None
    return lambda interaction: interaction.user.id


def _format_retry(message: str, retry_after: float | None) -> str:
    if not retry_after:
        return message
    seconds = max(1, int(retry_after + 0.5))
    unit = "second" if seconds == 1 else "seconds"
    return f"{message} Try again in {seconds} {unit}."


def describe_error(error: BaseException) -> str | None:
    retry_after = getattr(error, "retry_after", None)
    if isinstance(error, commands.CommandNotFound):
        return None
    if isinstance(error, (commands.CommandOnCooldown, app_commands.CommandOnCooldown)):
        return _format_retry(VexError.COOLDOWN, retry_after)
    if isinstance(error, commands.MaxConcurrencyReached):
        return VexError.MAX_CONCURRENCY
    if isinstance(error, (commands.BotMissingPermissions, app_commands.BotMissingPermissions)):
        return VexError.BOT_MISSING_PERMISSIONS
    if isinstance(error, (commands.MissingPermissions, app_commands.MissingPermissions)):
        return VexError.MISSING_PERMISSIONS
    if isinstance(error, (_OwnerCheckFailure, commands.NotOwner)):
        return VexError.OWNER_ONLY
    if isinstance(error, (_NSFWCheckFailure, commands.NSFWChannelRequired)):
        return VexError.NSFW_ONLY
    if isinstance(error, (commands.NoPrivateMessage, app_commands.NoPrivateMessage)):
        return VexError.SERVER_ONLY
    if isinstance(error, commands.PrivateMessageOnly):
        return VexError.DM_ONLY
    if isinstance(error, (commands.MissingRole, commands.MissingAnyRole, commands.BotMissingRole, commands.BotMissingAnyRole, app_commands.MissingRole, app_commands.MissingAnyRole)):
        return VexError.FORBIDDEN
    if isinstance(error, commands.MissingRequiredArgument):
        return VexError.MISSING_ARGUMENT
    if isinstance(error, (commands.BadArgument, commands.BadUnionArgument)):
        return VexError.INVALID_ARGUMENT
    if isinstance(error, commands.UserInputError):
        return VexError.INVALID_ARGUMENT
    if isinstance(error, commands.DisabledCommand):
        return VexError.DISABLED
    if isinstance(error, (commands.CheckFailure, app_commands.CheckFailure)):
        return VexError.FORBIDDEN
    return None


def listener(name: str | Callable[..., Any] | None = None) -> Any:
    direct: Any = None
    if callable(name) and not isinstance(name, str):
        direct = name
        name = None

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        event_name = name or getattr(func, "__name__", "on_event")
        if _is_class_scoped(func):
            return commands.Cog.listener(name=event_name)(func)
        setattr(func, "_vex_listener", event_name)
        _PENDING_LISTENERS.append((event_name, func))
        return func

    if direct is not None:
        return decorator(direct)
    return decorator


event = listener


def _stash_or_apply(target: Any, app_deco: Callable[[Any], Any], ext_deco: Callable[[Any], Any]) -> Any:
    if isinstance(target, commands.Command):
        ext_deco(target)
        return target
    if isinstance(target, app_commands.Command):
        app_deco(target)
        return target
    if isinstance(target, app_commands.Group):
        try:
            app_deco(target)
        except Exception:
            pass
        return target
    pending = getattr(target, "_vex_pending_checks", None)
    if pending is None:
        pending = []
        setattr(target, "_vex_pending_checks", pending)
    pending.append((app_deco, ext_deco))
    return target


def _drain_pending_checks(func: Any, built: Any) -> Any:
    pending = getattr(func, "_vex_pending_checks", None)
    if not pending:
        return built
    if isinstance(built, commands.Command):
        for _app_deco, ext_deco in pending:
            ext_deco(built)
    elif isinstance(built, app_commands.Command):
        for app_deco, _ext_deco in pending:
            app_deco(built)
    try:
        delattr(func, "_vex_pending_checks")
    except AttributeError:
        pass
    return built


def _dual_decorator(app_deco: Callable[[Any], Any], ext_deco: Callable[[Any], Any], target: Any) -> Any:
    def decorator(obj: Any) -> Any:
        return _stash_or_apply(obj, app_deco, ext_deco)

    if target is None:
        return decorator
    return decorator(target)


async def _owner_predicate(interaction: discord.Interaction) -> bool:
    bot_client = interaction.client
    checker = getattr(bot_client, "is_owner", None)
    if checker is not None and await checker(interaction.user):
        return True
    raise _OwnerCheckFailure("You do not own this bot.")


async def _nsfw_predicate(interaction: discord.Interaction) -> bool:
    channel = interaction.channel
    if channel is not None and getattr(channel, "is_nsfw", lambda: False)():
        return True
    raise _NSFWCheckFailure("This channel is not age-restricted.")


def owner_only(target: Any = None) -> Any:
    return _dual_decorator(app_commands.check(_owner_predicate), commands.is_owner(), target)


def guild_only(target: Any = None) -> Any:
    return _dual_decorator(app_commands.guild_only(), commands.guild_only(), target)


def dm_only(target: Any = None) -> Any:
    return _dual_decorator(app_commands.dm_only(), commands.dm_only(), target)


def nsfw_only(target: Any = None) -> Any:
    def app_deco(obj: Any) -> Any:
        app_commands.check(_nsfw_predicate)(obj)
        try:
            obj.nsfw = True
        except Exception:
            pass
        return obj

    def ext_deco(obj: Any) -> Any:
        commands.is_nsfw()(obj)
        app_command = getattr(obj, "app_command", None)
        if app_command is not None:
            try:
                app_command.nsfw = True
            except Exception:
                pass
        return obj

    return _dual_decorator(app_deco, ext_deco, target)


def has_permissions(**perms: bool) -> Callable[[Any], Any]:
    def decorator(obj: Any) -> Any:
        return _stash_or_apply(
            obj,
            app_commands.checks.has_permissions(**perms),
            commands.has_permissions(**perms),
        )

    return decorator


def bot_has_permissions(**perms: bool) -> Callable[[Any], Any]:
    def decorator(obj: Any) -> Any:
        return _stash_or_apply(
            obj,
            app_commands.checks.bot_has_permissions(**perms),
            commands.bot_has_permissions(**perms),
        )

    return decorator


def has_role(role: "int | str") -> Callable[[Any], Any]:
    def decorator(obj: Any) -> Any:
        return _stash_or_apply(
            obj,
            app_commands.checks.has_role(role),
            commands.has_role(role),
        )

    return decorator


def has_any_role(*roles: "int | str") -> Callable[[Any], Any]:
    def decorator(obj: Any) -> Any:
        return _stash_or_apply(
            obj,
            app_commands.checks.has_any_role(*roles),
            commands.has_any_role(*roles),
        )

    return decorator


def cooldown(rate: int, per: float, *, bucket: "str | commands.BucketType" = "user") -> Callable[[Any], Any]:
    bucket_type = _bucket_type(bucket)
    key = _cooldown_key(bucket)

    def decorator(obj: Any) -> Any:
        return _stash_or_apply(
            obj,
            app_commands.checks.cooldown(rate, per, key=key),
            commands.cooldown(rate, per, bucket_type),
        )

    return decorator


def guild_cooldown(rate: int, per: float) -> Callable[[Any], Any]:
    return cooldown(rate, per, bucket="guild")


def check(predicate: Callable[..., Any]) -> Callable[[Any], Any]:
    def decorator(obj: Any) -> Any:
        return _stash_or_apply(
            obj,
            app_commands.check(predicate),
            commands.check(predicate),
        )

    return decorator


import re as _re

_MENTION_RE = _re.compile(r"^<@!?(\d{2,20})>$")
_ROLE_MENTION_RE = _re.compile(r"^<@&(\d{2,20})>$")
_CHANNEL_MENTION_RE = _re.compile(r"^<#(\d{2,20})>$")
_ID_RE = _re.compile(r"^(\d{2,20})$")
_CUSTOM_EMOJI_RE = _re.compile(r"^<(a?):([A-Za-z0-9_]+):(\d{2,20})>$")
_DURATION_RE = _re.compile(r"(\d+)\s*([wdhms])", _re.IGNORECASE)
_DURATION_UNITS = {"w": 604800, "d": 86400, "h": 3600, "m": 60, "s": 1}


class ConvertError(commands.BadArgument, app_commands.AppCommandError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def _interaction_of(ctx_or_itx: Any) -> "discord.Interaction | None":
    if isinstance(ctx_or_itx, discord.Interaction):
        return ctx_or_itx
    return getattr(ctx_or_itx, "interaction", None)


def _client_of(ctx_or_itx: Any) -> Any:
    if isinstance(ctx_or_itx, discord.Interaction):
        return ctx_or_itx.client
    return getattr(ctx_or_itx, "bot", None) or getattr(ctx_or_itx, "client", None)


def _guild_of(ctx_or_itx: Any) -> "discord.Guild | None":
    return getattr(ctx_or_itx, "guild", None)


class _BaseConverter(app_commands.Transformer, commands.Converter):
    error_message: str = VexError.NOT_FOUND
    allow_none: bool = False

    async def _resolve(self, source: Any, value: str) -> Any:
        raise NotImplementedError

    async def _finish(self, source: Any, value: Any) -> Any:
        text = (str(value) if value is not None else "").strip()
        if not text:
            if self.allow_none:
                return None
            raise ConvertError(self.error_message)
        result = await self._resolve(source, text)
        if result is None and not self.allow_none:
            raise ConvertError(self.error_message)
        return result

    async def transform(self, interaction: discord.Interaction, value: Any) -> Any:
        return await self._finish(interaction, value)

    async def convert(self, ctx: commands.Context, argument: str) -> Any:
        return await self._finish(ctx, argument)


class _UserConverter(_BaseConverter):
    error_message = VexError.USER_NOT_FOUND
    type = discord.AppCommandOptionType.user

    def __init__(self, *, allow_none: bool = False) -> None:
        self.allow_none = allow_none

    async def transform(self, interaction: discord.Interaction, value: Any) -> Any:
        if isinstance(value, (discord.User, discord.Member)):
            return value
        return await self._finish(interaction, value)

    async def _resolve(self, source: Any, value: str) -> Any:
        client = _client_of(source)
        guild = _guild_of(source)
        match = _MENTION_RE.match(value) or _ID_RE.match(value)
        if match:
            uid = int(match.group(1))
            if guild is not None:
                member = guild.get_member(uid)
                if member is not None:
                    return member
            if client is not None:
                cached = client.get_user(uid)
                if cached is not None:
                    return cached
            if guild is not None:
                try:
                    return await guild.fetch_member(uid)
                except (discord.NotFound, discord.HTTPException):
                    pass
            if client is not None:
                try:
                    return await client.fetch_user(uid)
                except (discord.NotFound, discord.HTTPException):
                    return None
            return None
        if guild is not None:
            lowered = value.lower()
            if value.startswith("@"):
                value = value[1:]
                lowered = value.lower()
            named = discord.utils.find(
                lambda m: m.name.lower() == lowered or m.display_name.lower() == lowered or str(m).lower() == lowered,
                guild.members,
            )
            if named is not None:
                return named
            prefixed = discord.utils.find(
                lambda m: m.name.lower().startswith(lowered) or m.display_name.lower().startswith(lowered),
                guild.members,
            )
            if prefixed is not None:
                return prefixed
        return None


class _MemberConverter(_UserConverter):
    error_message = VexError.MEMBER_NOT_FOUND

    async def _resolve(self, source: Any, value: str) -> Any:
        guild = _guild_of(source)
        if guild is None:
            return None
        result = await super()._resolve(source, value)
        if result is None:
            return None
        if isinstance(result, discord.Member):
            return result
        member = guild.get_member(result.id)
        if member is not None:
            return member
        try:
            return await guild.fetch_member(result.id)
        except (discord.NotFound, discord.HTTPException):
            return None


class _RoleConverter(_BaseConverter):
    error_message = VexError.ROLE_NOT_FOUND
    type = discord.AppCommandOptionType.role

    def __init__(self, *, allow_none: bool = False) -> None:
        self.allow_none = allow_none

    async def transform(self, interaction: discord.Interaction, value: Any) -> Any:
        if isinstance(value, discord.Role):
            return value
        return await self._finish(interaction, value)

    async def _resolve(self, source: Any, value: str) -> Any:
        guild = _guild_of(source)
        if guild is None:
            return None
        match = _ROLE_MENTION_RE.match(value) or _ID_RE.match(value)
        if match:
            return guild.get_role(int(match.group(1)))
        lowered = value.lower()
        return discord.utils.find(lambda r: r.name.lower() == lowered, guild.roles) or discord.utils.find(
            lambda r: r.name.lower().startswith(lowered), guild.roles
        )


class _ChannelConverter(_BaseConverter):
    error_message = VexError.CHANNEL_NOT_FOUND
    type = discord.AppCommandOptionType.channel

    def __init__(self, *, allow_none: bool = False) -> None:
        self.allow_none = allow_none

    async def transform(self, interaction: discord.Interaction, value: Any) -> Any:
        if isinstance(value, (discord.abc.GuildChannel, discord.Thread)):
            return value
        return await self._finish(interaction, value)

    async def _resolve(self, source: Any, value: str) -> Any:
        guild = _guild_of(source)
        if guild is None:
            return None
        match = _CHANNEL_MENTION_RE.match(value) or _ID_RE.match(value)
        if match:
            return guild.get_channel_or_thread(int(match.group(1))) if hasattr(guild, "get_channel_or_thread") else guild.get_channel(int(match.group(1)))
        lowered = value.lstrip("#").lower()
        return discord.utils.find(lambda c: c.name.lower() == lowered, guild.channels) or discord.utils.find(
            lambda c: c.name.lower().startswith(lowered), guild.channels
        )


class _DurationConverter(_BaseConverter):
    error_message = "Give a duration like 1d12h, 90m, or 2h30m."
    type = discord.AppCommandOptionType.string

    def __init__(self, *, allow_none: bool = False, minimum: int | None = None, maximum: int | None = None) -> None:
        self.allow_none = allow_none
        self.minimum = minimum
        self.maximum = maximum

    async def _resolve(self, source: Any, value: str) -> Any:
        matches = list(_DURATION_RE.finditer(value))
        if not matches or _DURATION_RE.sub("", value).strip():
            return None
        total = sum(int(m.group(1)) * _DURATION_UNITS[m.group(2).lower()] for m in matches)
        if total <= 0:
            return None
        if self.minimum is not None and total < self.minimum:
            raise ConvertError("That duration is too short.")
        if self.maximum is not None and total > self.maximum:
            raise ConvertError("That duration is too long.")
        return total


class _EmojiConverter(_BaseConverter):
    error_message = VexError.EMOJI_NOT_FOUND
    type = discord.AppCommandOptionType.string

    def __init__(self, *, allow_none: bool = False) -> None:
        self.allow_none = allow_none

    async def _resolve(self, source: Any, value: str) -> Any:
        custom = _CUSTOM_EMOJI_RE.match(value)
        if custom:
            client = _client_of(source)
            if client is not None:
                found = client.get_emoji(int(custom.group(3)))
                if found is not None:
                    return found
            return value
        partial = discord.PartialEmoji.from_str(value)
        if partial.is_unicode_emoji():
            name = partial.name or ""
            if name and not all(ch.isascii() and (ch.isalnum() or ch.isspace()) for ch in name):
                return name
            return None
        return value


def _build(factory: Any, allow_none: bool, **kwargs: Any) -> Any:
    instance = factory(allow_none=allow_none, **kwargs)
    return app_commands.Transform[Any, instance]


def user(*, optional: bool = False) -> Any:
    return _build(_UserConverter, optional)


def member(*, optional: bool = False) -> Any:
    return _build(_MemberConverter, optional)


def role(*, optional: bool = False) -> Any:
    return _build(_RoleConverter, optional)


def channel(*, optional: bool = False) -> Any:
    return _build(_ChannelConverter, optional)


def duration(*, optional: bool = False, minimum: int | None = None, maximum: int | None = None) -> Any:
    return _build(_DurationConverter, optional, minimum=minimum, maximum=maximum)


def emoji(*, optional: bool = False) -> Any:
    return _build(_EmojiConverter, optional)


class convert:
    user = staticmethod(user)
    member = staticmethod(member)
    role = staticmethod(role)
    channel = staticmethod(channel)
    duration = staticmethod(duration)
    emoji = staticmethod(emoji)
    User = _UserConverter
    Member = _MemberConverter
    Role = _RoleConverter
    Channel = _ChannelConverter
    Duration = _DurationConverter
    Emoji = _EmojiConverter
    Error = ConvertError

    @staticmethod
    async def to_user(source: Any, value: str, *, optional: bool = False) -> Any:
        return await _UserConverter(allow_none=optional)._finish(source, value)

    @staticmethod
    async def to_member(source: Any, value: str, *, optional: bool = False) -> Any:
        return await _MemberConverter(allow_none=optional)._finish(source, value)

    @staticmethod
    async def to_role(source: Any, value: str, *, optional: bool = False) -> Any:
        return await _RoleConverter(allow_none=optional)._finish(source, value)

    @staticmethod
    async def to_channel(source: Any, value: str, *, optional: bool = False) -> Any:
        return await _ChannelConverter(allow_none=optional)._finish(source, value)

    @staticmethod
    def to_duration(value: str, *, minimum: int | None = None, maximum: int | None = None) -> "int | None":
        matches = list(_DURATION_RE.finditer(value or ""))
        if not matches or _DURATION_RE.sub("", value or "").strip():
            return None
        total = sum(int(m.group(1)) * _DURATION_UNITS[m.group(2).lower()] for m in matches)
        if total <= 0:
            return None
        if minimum is not None and total < minimum:
            return None
        if maximum is not None and total > maximum:
            return None
        return total

    @staticmethod
    def to_emoji(value: str) -> "str | None":
        if not value:
            return None
        custom = _CUSTOM_EMOJI_RE.match(value)
        if custom:
            return value
        partial = discord.PartialEmoji.from_str(value)
        if partial.is_unicode_emoji():
            name = partial.name or ""
            if name and not all(ch.isascii() and (ch.isalnum() or ch.isspace()) for ch in name):
                return name
            return None
        return value


__all__ = [
    "Vex",
    "convert",
    "ConvertError",
    "Bot",
    "Client",
    "Cog",
    "bot",
    "client",
    "vex",
    "ActionRowBuilder",
    "AuditCard",
    "AutoDeleteView",
    "ButtonBuilder",
    "ChannelPickerView",
    "ChoiceView",
    "CommandInfo",
    "ConfirmView",
    "ContainerBuilder",
    "CooldownCard",
    "CooldownStore",
    "DiffCard",
    "FileBuilder",
    "GalleryBuilder",
    "GlobalCooldown",
    "GradientColours",
    "GroupedPaginator",
    "HelpRegistry",
    "InfinitePaginator",
    "JumpSelectPaginator",
    "LiveView",
    "MediaCollector",
    "ModalBuilder",
    "MultiConfirmView",
    "PageGroup",
    "PageRenderer",
    "Paginator",
    "PollBuilder",
    "PresenceHandler",
    "PromptInput",
    "RolePickerView",
    "ScrollPaginator",
    "SectionBuilder",
    "SelectBuilder",
    "SelectMenu",
    "SelectOptionBuilder",
    "SlashGroup",
    "TableBuilder",
    "TextInputBuilder",
    "Theme",
    "TimedConfirmView",
    "TypedConfirmView",
    "TypedSelectBuilder",
    "UserPickerView",
    "VexError",
    "VexValidationError",
    "Wizard",
    "WizardStep",
    "action_row",
    "aside",
    "ask",
    "audit_card",
    "auto_delete",
    "bar",
    "bot_has_permissions",
    "box",
    "btn",
    "build",
    "button",
    "bytes_file",
    "card",
    "channel_picker",
    "channel_picker_view",
    "channel_select",
    "check",
    "choice",
    "choice_view",
    "cmd",
    "cmd_alias",
    "cmd_category",
    "cmd_desc",
    "cmd_example",
    "cmd_hidden",
    "cmd_syntax",
    "collector",
    "command_group",
    "confirm",
    "confirm_view",
    "container",
    "cooldown",
    "cooldown_card",
    "cooldown_store",
    "create",
    "describe_error",
    "diff_card",
    "disable_all",
    "dm_only",
    "document",
    "dropdown",
    "edit_to_v2",
    "error_card",
    "event",
    "field_input",
    "file",
    "file_component",
    "file_from_text",
    "form",
    "frame",
    "freeze_view",
    "gallery",
    "global_cooldown",
    "gradient",
    "group",
    "grouped_paginator",
    "guild_cooldown",
    "guild_only",
    "has_any_role",
    "has_permissions",
    "has_role",
    "hybrid_cmd",
    "hybrid_group",
    "images",
    "info_card",
    "layout",
    "leaderboard",
    "listener",
    "live",
    "make",
    "make_persistent",
    "media",
    "media_collector",
    "mentionable_select",
    "message",
    "meter",
    "modal",
    "multi_confirm",
    "new",
    "nsfw_only",
    "owner_only",
    "pages",
    "paginate",
    "paginator",
    "panel",
    "persist",
    "pick",
    "poll",
    "presence",
    "progress",
    "prompt",
    "prompt_input",
    "register_view",
    "registry",
    "registry_categories",
    "registry_category_select",
    "registry_to_select",
    "role_picker",
    "role_select",
    "row",
    "safe_defer",
    "safe_delete",
    "safe_edit",
    "scroll_paginator",
    "search_commands",
    "section",
    "select",
    "select_menu",
    "set_theme",
    "slash_cmd",
    "slash_group",
    "success_card",
    "survey",
    "table",
    "text_file",
    "text_input",
    "theme",
    "timed_confirm",
    "typed_confirm",
    "use_theme",
    "user_picker",
    "user_picker_view",
    "user_select",
    "view",
    "wait_input",
    "warning_card",
    "wizard",
]
