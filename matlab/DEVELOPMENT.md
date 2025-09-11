# Development

## Making a release

The Matlab release uses [SemVer](http://semver.org/) versioning scheme.

1. Make a release on [GitHub](https://github.com/PalmSens/PalmSens_SDK/releases).

The **release tag must start with `'matlab-'`**.
This triggers the workflow that zips the matlab directory and adds it to the release.

If this fails, to manually publish:

```bash
cd matlab
zip ../matlab-$VERSION.zip *
cd ..
```

Add zip file to release.
