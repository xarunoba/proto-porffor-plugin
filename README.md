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

porffor's `alpha-N` releases appear as `0.N.0` in proto. For example, `alpha-22` is `0.22.0`. Older `pre-alpha-*` releases are excluded.

According to porffor's maintainer on Discord, porffor will probably adopt semantic versioning at version 1.0, but this is not guaranteed. Until then, the `0.N.0` mapping is for proto compatibility and does not promise backward-compatible updates.

List available versions, then install and pin the latest:

```sh
proto versions porffor
proto install porffor latest
proto pin porffor latest --resolve
```

The updater checks at 00:00 and 12:00 UTC, or through **Run workflow**, and commits new alpha versions directly to the default branch. If a newer published release uses a different tag format, updates stop with an error until the plugin is adapted. Existing versions remain available. Installing `latest` alone does not change your project's pin.
