from ._base import _DataResourceBase
from ._ingest import _DataResourceIngest
from ._log import _DataResourceLog
from ._prepare import _DataResourcePrepare
from ._load import _DataResourceLoad

class DataResource(_DataResourceBase, _DataResourceLog, _DataResourceIngest, _DataResourcePrepare, _DataResourceLoad):
    pass