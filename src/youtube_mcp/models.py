"""Pydantic data models for structured, token-optimized YouTube responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VideoSummary(BaseModel):
    video_id: str
    title: str
    channel_id: str
    channel_title: str
    published_at: str
    description: str
    duration: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    url: str


class ChannelSummary(BaseModel):
    channel_id: str
    title: str
    description: str
    custom_url: Optional[str] = None
    published_at: Optional[str] = None
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    view_count: Optional[int] = None
    uploads_playlist_id: Optional[str] = None
    url: str


class PlaylistItemSummary(BaseModel):
    video_id: str
    title: str
    channel_title: str
    published_at: str
    position: int
    url: str


class CommentSummary(BaseModel):
    comment_id: str
    author: str
    author_channel_url: Optional[str] = None
    text: str
    like_count: int
    published_at: str
    reply_count: Optional[int] = 0


class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: float


class TranscriptResponse(BaseModel):
    video_id: str
    language: str
    is_generated: bool
    format: str
    segment_count: int
    content: Any  # Union[str, List[TranscriptSegment]]


class SearchItem(BaseModel):
    id: str
    kind: str  # video, channel, playlist
    title: str
    channel_title: str
    published_at: str
    description: str
    url: str


class SearchResponse(BaseModel):
    query: str
    total_results: Optional[int] = None
    next_page_token: Optional[str] = None
    results: List[SearchItem]
