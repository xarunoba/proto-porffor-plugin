# proto porffor plugin

Install and manage [porffor](https://github.com/CanadaHonk/porffor) with [proto](https://moonrepo.dev/docs/proto).

## Requirements

- proto 0.63.0 or newer.
- Linux or macOS on x64 or ARM64. Linux supports GNU libc and musl. On Windows, use WSL.
- A C compiler, such as Clang, for native compilation.

## Install

Add this to your project's `.prototools`:

```toml
porffor = "latest"

[plugins.tools]
porffor = "https://raw.githubusercontent.com/xarunoba/proto-porffor-plugin/alpha/porffor.toml"
```

The `alpha` branch tracks porffor's alpha releases. This URL will continue to select that series even if another branch becomes the default. To use a local checkout instead, set the plugin URL to `file://./porffor.toml`.

Review the plugin and configuration, then run:

```sh
proto trust .prototools
proto install porffor
proto run porffor -- --version
```

The trust step allows proto to load the plugin from your project's configuration.

## Use

With proto's shims on your `PATH`:

```sh
porf hello.js
porf native hello.js -o hello
```

Without shims, use `proto run porffor -- hello.js`.

## Update

porffor's `alpha-N` releases appear as `N.0.0` in proto: `alpha-22` becomes `22.0.0`. These numbers identify alpha releases and carry no stability or compatibility guarantee.

The plugin downloads prebuilt archives from GitHub Releases, using `alpha-{versionMajor}` to select the release.

List available versions, then install and pin the latest:

```sh
proto versions porffor
proto install porffor latest
proto pin porffor latest --resolve
```

Installing `latest` alone does not change your project's pin. Remote discovery and downloads require access to GitHub. Installation fails if the selected release's archive is unavailable for your platform. This branch supports only the `alpha-N` version pattern; a different upstream release format will use a separate plugin branch.
