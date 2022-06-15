from typing import TYPE_CHECKING
from oteapi.models import AttrDict, ResourceConfig, SessionUpdate
from pydantic import Field, AnyUrl
from pydantic.dataclasses import dataclass
from aiida import load_profile, orm
from aiida.manage.configuration import Profile, load_profile
from aiida.manage.configuration import get_config
from ..models.aiida import AiiDAProfileConfig
import dlite

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict

class AiidaConnectConfig(AttrDict):
    """AiidaDataSource specific Configuration."""

    aiida_profile: AiiDAProfileConfig = Field(
        ...,
        description="AiiDA Profile specifications",
    )
    single_data_node_uuid: str = Field(
        ...,
        description="SingleDataNode identifier",
    )
    entity_url: AnyUrl = Field(
        ...,
        description="DLite Entity"
    )



class AiidaResourceConfig(ResourceConfig):
    """Demo resource strategy config."""

    accessUrl: AnyUrl = Field(
        "http://localhost",
        const=True,
        description=ResourceConfig.__fields__["accessUrl"].field_info.description,
    )

    accessService: str = Field(
        "AiiDA",
        const=True,
        description=ResourceConfig.__fields__["accessService"].field_info.description,
    )
    configuration: AiidaConnectConfig = Field(
        ...,
        description="Aiida Profile configuration.",
    )


class SessionUpdateAiiDAResource(SessionUpdate):
    """Class for returning values from AiiDA Resource strategy."""

    output: dict = Field(
        ...,
        description=(
            "The output from downloading the response from the given `accessUrl`."
        ),
    )
    uuid : str = Field(
        ...,
        description=(
            "UUID of the store DLite entity"
        )

    )


@dataclass
class AiiDAResourceStrategy:
    """Resource Strategy.

    **Registers strategies**:

    - `("accessService", "AiiDA")`

    """

    resource_config: AiidaResourceConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTEAPI
        Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        return SessionUpdate()

    def get(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> SessionUpdateAiiDAResource:
        """Execute the strategy.

        This method will be called through the strategy-specific endpoint of the
        OTEAPI Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """

        # Create a new AiiDA Profile from the input configuration
        profile_config = self.resource_config.configuration.aiida_profile

        # https://aiida.readthedocs.io/projects/aiida-core/en/latest/reference/apidoc/aiida.manage.configuration.html
        profile = Profile(profile_config.profile_name,
                  config=dict(
                    storage=profile_config.storage.dict(),
                    process_control=profile_config.process_control.dict()))


        # Append the profile to the current AiiDA configuration
        config = get_config()
        config.add_profile(profile)
        config.set_default_profile(profile.name)
        load_profile(profile.name)

        storage_cls = profile.storage_cls
        storage_cls.migrate(profile)

        config.update_profile(profile)
        config.store()

        # Fetch data from the specified Data Node
        data = orm.load_node(uuid=f'{self.resource_config.configuration.single_data_node_uuid}')

        r = requests.get(self.resource_config.configuration.entity_url, allow_redirects=True)
        Entity = dlite.Instance.from_json(r.text)

        entity_instance = Entity()

        # TODO: Change .data to a configurable property
        entity_instance.data = data.get_content()

        # TODO: Save the entity somewhere. Preferably in a config-specified dataspace.
        # entity_instance.save('json', os.path.join(cwd, "output.json"), "mode=w")
        entity_instance.uuid

        # Create output and return
        output = SessionUpdateAiiDAResource(output=dict(status='ok'), uuid=entity_instance.uuid)

        return output
