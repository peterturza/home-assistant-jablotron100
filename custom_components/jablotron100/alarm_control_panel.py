from homeassistant import config_entries, core
from homeassistant.const import (
	STATE_ALARM_DISARMED,
	STATE_ALARM_ARMED_AWAY,
	STATE_ALARM_ARMED_NIGHT,
	STATE_ALARM_ARMING,
)
from homeassistant.components.alarm_control_panel import (
	AlarmControlPanelEntity,
	FORMAT_NUMBER,
	FORMAT_TEXT,
	SUPPORT_ALARM_ARM_AWAY,
	SUPPORT_ALARM_ARM_NIGHT,
)
from homeassistant.helpers.typing import StateType
from typing import Optional
from .const import DATA_JABLOTRON, DOMAIN
from .jablotron import JablotronEntity, JablotronAlarmControlPanel


async def async_setup_entry(hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry, async_add_entities) -> None:
	jablotron = hass.data[DOMAIN][config_entry.entry_id][DATA_JABLOTRON]

	async_add_entities((JablotronAlarmControlPanelEntity(jablotron, control) for control in jablotron.alarm_control_panels()))


class JablotronAlarmControlPanelEntity(JablotronEntity, AlarmControlPanelEntity):
	_control: JablotronAlarmControlPanel

	@property
	def state(self) -> StateType:
		return self._state

	@property
	def code_format(self) -> Optional[str]:
		if self._state == STATE_ALARM_DISARMED:
			code_required = self._jablotron.is_code_required_for_arm()
		else:
			code_required = self._jablotron.is_code_required_for_disarm()

		if not code_required:
			return None

		return FORMAT_TEXT if self._jablotron.code_contains_asterisk() is True else FORMAT_NUMBER

	@property
	def supported_features(self) -> int:
		return SUPPORT_ALARM_ARM_AWAY | SUPPORT_ALARM_ARM_NIGHT

	async def async_alarm_disarm(self, code: Optional[str] = None) -> None:
		if self._state == STATE_ALARM_DISARMED:
			return

		code = JablotronAlarmControlPanelEntity._clean_code(code)

		if code is None and self._jablotron.is_code_required_for_disarm():
			return

		self._jablotron.modify_alarm_control_panel_section_state(self._control.section, STATE_ALARM_DISARMED, code)
		self.update_state(STATE_ALARM_DISARMED)

	async def async_alarm_arm_away(self, code: Optional[str] = None) -> None:
		if self._state == STATE_ALARM_ARMED_AWAY:
			return

		code = JablotronAlarmControlPanelEntity._clean_code(code)

		if code is None and self._jablotron.is_code_required_for_arm():
			return

		self.update_state(STATE_ALARM_ARMING)
		self._jablotron.modify_alarm_control_panel_section_state(self._control.section, STATE_ALARM_ARMED_AWAY, code)

	async def async_alarm_arm_night(self, code: Optional[str] = None) -> None:
		if self._state == STATE_ALARM_ARMED_NIGHT or self._state == STATE_ALARM_ARMED_AWAY:
			return

		code = JablotronAlarmControlPanelEntity._clean_code(code)

		if code is None and self._jablotron.is_code_required_for_arm():
			return

		self.update_state(STATE_ALARM_ARMING)
		self._jablotron.modify_alarm_control_panel_section_state(self._control.section, STATE_ALARM_ARMED_NIGHT, code)

	@staticmethod
	def _clean_code(code: Optional[str]) -> Optional[str]:
		return None if code == "" else code
