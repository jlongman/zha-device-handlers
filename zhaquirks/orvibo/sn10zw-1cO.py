"""Orvibo motion sensor."""
import math

from zigpy.profiles import zha
from zigpy.zcl.clusters.general import Basic, Identify, PowerConfiguration, Scenes, Groups
from zigpy.zcl.clusters.security import IasZone

from . import (
    ORVIBO,
    OrviboCustomDevice,
    MotionCluster,
    OccupancyCluster,
)
from .. import Bus, PowerConfigurationCluster
from ..const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
    SKIP_CONFIGURATION,
)

ORVIBO_CLUSTER_ID = 0xFFFF

#  Discovered endpoint information:
#   <Optional endpoint=1 profile=260 device_type=1026 device_version=1
#       input_clusters=[0, 3, 1280, 65535, 1]
#       output_clusters=[0, 4, 3, 5, 1]
#       >
#  {
#   "node_descriptor": "<NodeDescriptor
#       byte1=2
#       byte2=64
#       mac_capability_flags=128
#       manufacturer_code=4151
#       maximum_buffer_size=127
#       maximum_incoming_transfer_size=100
#       server_mask=0
#       maximum_outgoing_transfer_size=100
#       descriptor_capability_field=0
#       >",
#   "endpoints": {
#     "1": {
#       "profile_id": 260,
#       "device_type": "0x0402",
#       "in_clusters": [
#         "0x0000",
#         "0x0001",
#         "0x0003",
#         "0x0500",
#         "0xffff"
#       ],
#       "out_clusters": [
#         "0x0000",
#         "0x0001",
#         "0x0003",
#         "0x0004",
#         "0x0005"
#       ]
#     }
#   },
#   "manufacturer": "ORVIBO",
#   "model": "895a2d80097f4ae2b2d40500d5e03dcc",
#   "class": "zigpy.device.Device"
# }


class MotionOrvibo(OrviboCustomDevice):
    """Custom device representing aqara body sensors."""

    def __init__(self, *args, **kwargs):
        """Init."""
        self.battery_size = 9
        self.motion_bus = Bus()
        super().__init__(*args, **kwargs)

    signature = {
        MODELS_INFO: [(ORVIBO, "895a2d80097f4ae2b2d40500d5e03dcc")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.IAS_ZONE,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    Identify.cluster_id,
                    IasZone.cluster_id,
                    ORVIBO_CLUSTER_ID,
                ],
                OUTPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                ],
            }
        },
    }

    replacement = {
        # SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfigurationCluster,
                    Identify.cluster_id,
                    OccupancyCluster,
                    MotionCluster,
                    ORVIBO_CLUSTER_ID,
                ],
                OUTPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                ],
            }
        },
    }
