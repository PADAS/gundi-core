from gundi_core.events.core import SystemEventBaseModel


class SystemCommandBaseModel(SystemEventBaseModel):
    # Marker class for system commands.
    # Technically, a command message is equal to an event message but expressing an intent.
    pass
