# Development

## Making a release

PalmSens .NET MAUI SDK uses the [SemVer](http://semver.org/) versioning scheme.

1. Bump the version (`major`/`minor`/`patch` as needed), see [bump-my-version](https://github.com/callowayproject/bump-my-version).

```console
bump-my-version minor
```

2. Make a release on [GitHub](https://github.com/PalmSens/PalmSens_SDK/releases).

The **release tag must start with `'maui-'`**. This triggers the build that packages the `maui/` directory and uploads the asset to the tagged release.
