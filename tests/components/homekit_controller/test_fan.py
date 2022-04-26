"""Basic checks for HomeKit motion sensors and contact sensors."""
from aiohomekit.model.characteristics import CharacteristicsTypes
from aiohomekit.model.services import ServicesTypes

from tests.components.homekit_controller.common import setup_test_component


def create_fan_service(accessory):
    """
    Define fan v1 characteristics as per HAP spec.

    This service is no longer documented in R2 of the public HAP spec but existing
    devices out there use it (like the SIMPLEconnect fan)
    """
    service = accessory.add_service(ServicesTypes.FAN)

    cur_state = service.add_char(CharacteristicsTypes.ON)
    cur_state.value = 0

    direction = service.add_char(CharacteristicsTypes.ROTATION_DIRECTION)
    direction.value = 0

    speed = service.add_char(CharacteristicsTypes.ROTATION_SPEED)
    speed.value = 0


def create_fanv2_service(accessory):
    """Define fan v2 characteristics as per HAP spec."""
    service = accessory.add_service(ServicesTypes.FAN_V2)

    cur_state = service.add_char(CharacteristicsTypes.ACTIVE)
    cur_state.value = 0

    direction = service.add_char(CharacteristicsTypes.ROTATION_DIRECTION)
    direction.value = 0

    speed = service.add_char(CharacteristicsTypes.ROTATION_SPEED)
    speed.value = 0

    swing_mode = service.add_char(CharacteristicsTypes.SWING_MODE)
    swing_mode.value = 0


def create_fanv2_service_with_min_step(accessory):
    """Define fan v2 characteristics as per HAP spec."""
    service = accessory.add_service(ServicesTypes.FAN_V2)

    cur_state = service.add_char(CharacteristicsTypes.ACTIVE)
    cur_state.value = 0

    direction = service.add_char(CharacteristicsTypes.ROTATION_DIRECTION)
    direction.value = 0

    speed = service.add_char(CharacteristicsTypes.ROTATION_SPEED)
    speed.value = 0
    speed.minStep = 25

    swing_mode = service.add_char(CharacteristicsTypes.SWING_MODE)
    swing_mode.value = 0


def create_fanv2_service_without_rotation_speed(accessory):
    """Define fan v2 characteristics as per HAP spec."""
    service = accessory.add_service(ServicesTypes.FAN_V2)

    cur_state = service.add_char(CharacteristicsTypes.ACTIVE)
    cur_state.value = 0

    direction = service.add_char(CharacteristicsTypes.ROTATION_DIRECTION)
    direction.value = 0

    swing_mode = service.add_char(CharacteristicsTypes.SWING_MODE)
    swing_mode.value = 0


async def test_fan_read_state(hass, utcnow):
    """Test that we can read the state of a HomeKit fan accessory."""
    helper = await setup_test_component(hass, create_fan_service)

    state = await helper.async_update(
        ServicesTypes.FAN, {CharacteristicsTypes.ON: False}
    )
    assert state.state == "off"

    state = await helper.async_update(
        ServicesTypes.FAN, {CharacteristicsTypes.ON: True}
    )
    assert state.state == "on"


async def test_turn_on(hass, utcnow):
    """Test that we can turn a fan on."""
    helper = await setup_test_component(hass, create_fan_service)

    await hass.services.async_call(
        "fan",
        "turn_on",
        {"entity_id": "fan.testdevice", "percentage": 100},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ON: 1,
            CharacteristicsTypes.ROTATION_SPEED: 100,
        },
    )

    await hass.services.async_call(
        "fan",
        "turn_on",
        {"entity_id": "fan.testdevice", "percentage": 66},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ON: 1,
            CharacteristicsTypes.ROTATION_SPEED: 66.0,
        },
    )

    await hass.services.async_call(
        "fan",
        "turn_on",
        {"entity_id": "fan.testdevice", "percentage": 33},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ON: 1,
            CharacteristicsTypes.ROTATION_SPEED: 33.0,
        },
    )


async def test_turn_on_off_without_rotation_speed(hass, utcnow):
    """Test that we can turn a fan on."""
    helper = await setup_test_component(
        hass, create_fanv2_service_without_rotation_speed
    )

    await hass.services.async_call(
        "fan",
        "turn_on",
        {"entity_id": "fan.testdevice"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 1,
        },
    )

    await hass.services.async_call(
        "fan",
        "turn_off",
        {"entity_id": "fan.testdevice"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 0,
        },
    )


async def test_turn_off(hass, utcnow):
    """Test that we can turn a fan off."""
    helper = await setup_test_component(hass, create_fan_service)

    await helper.async_update(ServicesTypes.FAN, {CharacteristicsTypes.ON: 1})

    await hass.services.async_call(
        "fan",
        "turn_off",
        {"entity_id": "fan.testdevice"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ON: 0,
        },
    )


async def test_set_speed(hass, utcnow):
    """Test that we set fan speed."""
    helper = await setup_test_component(hass, create_fan_service)

    await helper.async_update(ServicesTypes.FAN, {CharacteristicsTypes.ON: 1})

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 100},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ROTATION_SPEED: 100.0,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 66},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ROTATION_SPEED: 66.0,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 33},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ROTATION_SPEED: 33.0,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 0},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ON: 0,
        },
    )


async def test_set_percentage(hass, utcnow):
    """Test that we set fan speed by percentage."""
    helper = await setup_test_component(hass, create_fan_service)

    await helper.async_update(ServicesTypes.FAN, {CharacteristicsTypes.ON: 1})

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 66},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ROTATION_SPEED: 66,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 0},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ON: 0,
        },
    )


async def test_speed_read(hass, utcnow):
    """Test that we can read a fans oscillation."""
    helper = await setup_test_component(hass, create_fan_service)

    state = await helper.async_update(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ON: 1,
            CharacteristicsTypes.ROTATION_SPEED: 100,
        },
    )
    assert state.attributes["percentage"] == 100
    assert state.attributes["percentage_step"] == 1.0

    state = await helper.async_update(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ROTATION_SPEED: 50,
        },
    )
    assert state.attributes["percentage"] == 50

    state = await helper.async_update(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ROTATION_SPEED: 25,
        },
    )
    assert state.attributes["percentage"] == 25

    state = await helper.async_update(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ON: 0,
            CharacteristicsTypes.ROTATION_SPEED: 0,
        },
    )
    assert state.attributes["percentage"] == 0


async def test_set_direction(hass, utcnow):
    """Test that we can set fan spin direction."""
    helper = await setup_test_component(hass, create_fan_service)

    await hass.services.async_call(
        "fan",
        "set_direction",
        {"entity_id": "fan.testdevice", "direction": "reverse"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ROTATION_DIRECTION: 1,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_direction",
        {"entity_id": "fan.testdevice", "direction": "forward"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN,
        {
            CharacteristicsTypes.ROTATION_DIRECTION: 0,
        },
    )


async def test_direction_read(hass, utcnow):
    """Test that we can read a fans oscillation."""
    helper = await setup_test_component(hass, create_fan_service)

    state = await helper.async_update(
        ServicesTypes.FAN, {CharacteristicsTypes.ROTATION_DIRECTION: 0}
    )
    assert state.attributes["direction"] == "forward"

    state = await helper.async_update(
        ServicesTypes.FAN, {CharacteristicsTypes.ROTATION_DIRECTION: 1}
    )
    assert state.attributes["direction"] == "reverse"


async def test_fanv2_read_state(hass, utcnow):
    """Test that we can read the state of a HomeKit fan accessory."""
    helper = await setup_test_component(hass, create_fanv2_service)

    state = await helper.async_update(
        ServicesTypes.FAN_V2, {CharacteristicsTypes.ACTIVE: False}
    )
    assert state.state == "off"

    state = await helper.async_update(
        ServicesTypes.FAN_V2, {CharacteristicsTypes.ACTIVE: True}
    )
    assert state.state == "on"


async def test_v2_turn_on(hass, utcnow):
    """Test that we can turn a fan on."""
    helper = await setup_test_component(hass, create_fanv2_service)

    await hass.services.async_call(
        "fan",
        "turn_on",
        {"entity_id": "fan.testdevice", "percentage": 100},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 1,
            CharacteristicsTypes.ROTATION_SPEED: 100,
        },
    )

    await hass.services.async_call(
        "fan",
        "turn_on",
        {"entity_id": "fan.testdevice", "percentage": 66},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 1,
            CharacteristicsTypes.ROTATION_SPEED: 66,
        },
    )

    await hass.services.async_call(
        "fan",
        "turn_on",
        {"entity_id": "fan.testdevice", "percentage": 33},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 1,
            CharacteristicsTypes.ROTATION_SPEED: 33,
        },
    )

    await hass.services.async_call(
        "fan",
        "turn_off",
        {"entity_id": "fan.testdevice"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 0,
            CharacteristicsTypes.ROTATION_SPEED: 33,
        },
    )

    await hass.services.async_call(
        "fan",
        "turn_on",
        {"entity_id": "fan.testdevice"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 1,
            CharacteristicsTypes.ROTATION_SPEED: 33,
        },
    )


async def test_v2_turn_off(hass, utcnow):
    """Test that we can turn a fan off."""
    helper = await setup_test_component(hass, create_fanv2_service)

    await helper.async_update(ServicesTypes.FAN_V2, {CharacteristicsTypes.ACTIVE: 1})

    await hass.services.async_call(
        "fan",
        "turn_off",
        {"entity_id": "fan.testdevice"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 0,
        },
    )


async def test_v2_set_speed(hass, utcnow):
    """Test that we set fan speed."""
    helper = await setup_test_component(hass, create_fanv2_service)

    await helper.async_update(ServicesTypes.FAN_V2, {CharacteristicsTypes.ACTIVE: 1})

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 100},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ROTATION_SPEED: 100,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 66},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ROTATION_SPEED: 66,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 33},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ROTATION_SPEED: 33,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 0},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 0,
        },
    )


async def test_v2_set_percentage(hass, utcnow):
    """Test that we set fan speed by percentage."""
    helper = await setup_test_component(hass, create_fanv2_service)

    await helper.async_update(ServicesTypes.FAN_V2, {CharacteristicsTypes.ACTIVE: 1})

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 66},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ROTATION_SPEED: 66,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 0},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 0,
        },
    )


async def test_v2_set_percentage_with_min_step(hass, utcnow):
    """Test that we set fan speed by percentage."""
    helper = await setup_test_component(hass, create_fanv2_service_with_min_step)

    await helper.async_update(ServicesTypes.FAN_V2, {CharacteristicsTypes.ACTIVE: 1})

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 66},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ROTATION_SPEED: 75,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.testdevice", "percentage": 0},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 0,
        },
    )


async def test_v2_speed_read(hass, utcnow):
    """Test that we can read a fans oscillation."""
    helper = await setup_test_component(hass, create_fanv2_service)

    state = await helper.async_update(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 1,
            CharacteristicsTypes.ROTATION_SPEED: 100,
        },
    )
    assert state.attributes["percentage"] == 100

    state = await helper.async_update(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ROTATION_SPEED: 50,
        },
    )
    assert state.attributes["percentage"] == 50

    state = await helper.async_update(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ROTATION_SPEED: 25,
        },
    )
    assert state.attributes["percentage"] == 25

    state = await helper.async_update(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ACTIVE: 0,
            CharacteristicsTypes.ROTATION_SPEED: 0,
        },
    )
    assert state.attributes["percentage"] == 0


async def test_v2_set_direction(hass, utcnow):
    """Test that we can set fan spin direction."""
    helper = await setup_test_component(hass, create_fanv2_service)

    await hass.services.async_call(
        "fan",
        "set_direction",
        {"entity_id": "fan.testdevice", "direction": "reverse"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ROTATION_DIRECTION: 1,
        },
    )

    await hass.services.async_call(
        "fan",
        "set_direction",
        {"entity_id": "fan.testdevice", "direction": "forward"},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.ROTATION_DIRECTION: 0,
        },
    )


async def test_v2_direction_read(hass, utcnow):
    """Test that we can read a fans oscillation."""
    helper = await setup_test_component(hass, create_fanv2_service)

    state = await helper.async_update(
        ServicesTypes.FAN_V2, {CharacteristicsTypes.ROTATION_DIRECTION: 0}
    )
    assert state.attributes["direction"] == "forward"

    state = await helper.async_update(
        ServicesTypes.FAN_V2, {CharacteristicsTypes.ROTATION_DIRECTION: 1}
    )
    assert state.attributes["direction"] == "reverse"


async def test_v2_oscillate(hass, utcnow):
    """Test that we can control a fans oscillation."""
    helper = await setup_test_component(hass, create_fanv2_service)

    await hass.services.async_call(
        "fan",
        "oscillate",
        {"entity_id": "fan.testdevice", "oscillating": True},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.SWING_MODE: 1,
        },
    )

    await hass.services.async_call(
        "fan",
        "oscillate",
        {"entity_id": "fan.testdevice", "oscillating": False},
        blocking=True,
    )
    helper.async_assert_service_values(
        ServicesTypes.FAN_V2,
        {
            CharacteristicsTypes.SWING_MODE: 0,
        },
    )


async def test_v2_oscillate_read(hass, utcnow):
    """Test that we can read a fans oscillation."""
    helper = await setup_test_component(hass, create_fanv2_service)

    state = await helper.async_update(
        ServicesTypes.FAN_V2, {CharacteristicsTypes.SWING_MODE: 0}
    )
    assert state.attributes["oscillating"] is False

    state = await helper.async_update(
        ServicesTypes.FAN_V2, {CharacteristicsTypes.SWING_MODE: 1}
    )
    assert state.attributes["oscillating"] is True
