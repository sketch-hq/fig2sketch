from enum import IntEnum

from .common import Point
from dataclasses import dataclass, field


class OverlayBackgroundInteraction(IntEnum):
    NONE = 0
    CLOSES_OVERLAY = 1


class PrototypePresentationStyle(IntEnum):
    SCREEN = 0
    OVERLAY = 1


class AnimationType(IntEnum):
    NONE = -1
    SLIDE_FROM_RIGHT = 0
    SLIDE_FROM_LEFT = 1
    SLIDE_FROM_BOTTOM = 2
    SLIDE_FROM_TOP = 3


@dataclass(kw_only=True)
class FlowOverlaySettings:
    _class: str = field(default='MSImmutableFlowOverlaySettings', init=False)
    offset: Point
    overlayAnchor: Point
    sourceAnchor: Point
    overlayType: int = 1

    @staticmethod
    def Centered() -> 'FlowOverlaySettings':
        point = Point(0.5, 0.5)

        return FlowOverlaySettings(
            offset=Point(0, 0),
            overlayAnchor=point,
            sourceAnchor=point
        )


@dataclass(kw_only=True)
class FlowConnection:
    _class: str = field(default='MSImmutableFlowConnection', init=False)
    destinationArtboardID: str = None
    animationType: AnimationType = AnimationType.NONE
    maintainScrollPosition: bool = False
    shouldCloseExistingOverlays: bool = False


@dataclass(kw_only=True)
class PrototypeViewport:
    _class: str = field(default='MSImmutablePrototypeViewport', init=False)
    name: str
    size: str
    # libraryID: str = 'EB972BCC-0467-4E50-998E-0AC5A39517F0'
    # templateID: str = '55992B99-92E5-4A93-AF90-B3A461675C05'
