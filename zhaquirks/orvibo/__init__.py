import asyncio
import logging
import math

from zigpy.quirks import CustomCluster, CustomDevice
from zigpy.zcl.clusters.security import IasZone
from zigpy.zcl.clusters.measurement import (
    OccupancySensing,
)
from .. import Bus, LocalDataCluster
from ..const import (
    CLUSTER_COMMAND,
    OFF,
    ON,
    ZONE_STATE,
    MOTION_EVENT,
)

_LOGGER = logging.getLogger(__name__)

ORVIBO = "ORVIBO"
BATTERY_SIZE = "battery_size"
ZONE_TYPE = 0x0001
MOTION_TYPE = 0x000D
OCCUPANCY_STATE = 0


class OrviboCustomDevice(CustomDevice):
    """Custom device representing orvibo devices."""

    def __init__(self, *args, **kwargs):
        """Init."""
        self.battery_bus = Bus()
        if not hasattr(self, BATTERY_SIZE):
            self.battery_size = 10
        super().__init__(*args, **kwargs)


class OccupancyCluster(CustomCluster, OccupancySensing):
    """Occupancy cluster."""

    cluster_id = OccupancySensing.cluster_id

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        _LOGGER.warning("%s - Resetting motion sensor", "init")  # FIXME
        self.endpoint.device.motion_bus.add_listener(self)
        self._timer_handle = None

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        _LOGGER.warning("%s - Update motion sensor {}", attrid, value)  # FIXME
        if attrid == OCCUPANCY_STATE and value == ON:
            if self._timer_handle:
                self._timer_handle.cancel()
            self.endpoint.device.motion_bus.listener_event(MOTION_EVENT)
            loop = asyncio.get_event_loop()
            self._timer_handle = loop.call_later(15, self._turn_off)

    def _turn_off(self):
        self._timer_handle = None
        _LOGGER.warning("%s - Resetting motion sensor {}", "attrid", "value")  # FIXME

        self._update_attribute(OCCUPANCY_STATE, OFF)


class MotionCluster(LocalDataCluster, IasZone):
    """Motion cluster."""

    cluster_id = IasZone.cluster_id

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self._timer_handle = None
        _LOGGER.warning("%s - Resetting motion sensor", "init")  # FIXME
        self.endpoint.device.motion_bus.add_listener(self)
        super()._update_attribute(ZONE_TYPE, MOTION_TYPE)

    def motion_event(self):
        """Motion event."""
        super().listener_event(CLUSTER_COMMAND, None, ZONE_STATE, [ON])

        _LOGGER.warning("%s - Received motion event message", self.endpoint.device.ieee) # FIXME

        if self._timer_handle:
            self._timer_handle.cancel()

        loop = asyncio.get_event_loop()
        self._timer_handle = loop.call_later(15, self._turn_off)

    def _turn_off(self):
        _LOGGER.warning("%s - Resetting motion sensor", self.endpoint.device.ieee) # FIXME
        self._timer_handle = None
        super().listener_event(CLUSTER_COMMAND, None, ZONE_STATE, [OFF])
