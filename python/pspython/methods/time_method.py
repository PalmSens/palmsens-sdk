from .method import MethodParameters


class TimeMethodParameters(MethodParameters):
    def update_dotnet_method(self, *, dotnet_method):
        super().update_dotnet_method(dotnet_method=dotnet_method)

    def to_dotnet_method(self):
        """Convert parameters to dotnet method."""

        raise NotImplementedError
